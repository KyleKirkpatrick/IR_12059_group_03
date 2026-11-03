import math
from platform import node
import time
from typing import List

import rclpy
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, JointConstraint
from rclpy.node import Node
from std_msgs.msg import String
import json


class PineappleNavigator(Node):
    def __init__(self):
        super().__init__('pineapple_navigator')

        # Robot flags
        self.robot_holding_box = False
        self.robot_stuck = False
        self.robot_active = False
        self.box_on_conveyor = False
        self.box_zone = 0

        # Navigation
        self.nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

        self.waypoints = [
            ('home',      0.0,   0.0,    0.0,      10),
            ('pickup_A',  1.56, -0.562, -0.00143, 5.0),
            ('pickup_B',  1.28, -0.0802, -0.00134, 5.0),
            ('pickup_C',  1.18,  0.0802, -0.00143, 5.0),
            ('dropoff',  30.1,  -6.35,   0.00253, 5.0),
        ]

        # Subscription to HMI information
        self.subscription = self.create_subscription(
            String,
            'hmi/unified_status',
            self.listener_callback,
            10,
        )

        # Arm configuration
        self.joint_names: List[str] = ['joint_1','joint_2','joint_3','joint_4','joint_5','joint_6']
        self.planning_group: str = 'tmr_arm'
        self.action_name: str = '/move_action'  # keep identical to your setup

        # Action client for MoveIt 
        self.moveit_client = ActionClient(self, MoveGroup, self.action_name)
        self.get_logger().info('Waiting for MoveGroup action server...')
        self.moveit_client.wait_for_server()
        self.get_logger().info('MoveGroup action server ready.')

        self.arm_positions = [
            ('home', [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
            ('pick', [0.0, math.radians(62.0), math.radians(42.0), 0.0, 0.0, 0.0]),
            ('carry', [0.0, math.radians(-75.0), math.radians(140.0), math.radians(280.0), 0.0, 0.0]),
            ('place', [0.0, math.radians(43.0), math.radians(46.0), 0.0, 0.0, 0.0])
        ]

        self.run()

    def listener_callback(self, msg):
        try:
            data = json.loads(msg.data) # parse JSON string into Python dict
            time_stamp :float = float(data["stamp"].get("sec", 0)) + float(data["stamp"].get("nanosec", 0)) * 1e-9

            # Remove "kg" from the weight string
            weight_str = data["box"].get("weight_raw", "0")
            if isinstance(weight_str, str):
                if weight_str.endswith("kg"):
                    weight_str = weight_str[:-2]
                if weight_str.startswith(": "):
                    weight_str = weight_str[2:]
            else:
                weight_str = "0"
            box_weight : float = float(weight_str)  

            # Remove any leading ": " from the location string
            box_location : str = data["box"].get("location", "")
            if isinstance(box_location, str):
                if box_location.startswith(": "):
                    box_location = box_location[2:]
            else:
                box_location = ""

            counts = data["counts"]

            # print("Received PLC status:")
            # print(f" Time: {time_stamp}")
            # print(f" Weight: {box_weight} kg")
            # print(f" Location: {box_location}")
            # print(f" Counts: big={counts['big']}, medium={counts['medium']}, "f"small={counts['small']}, total={counts['total']}")
            # print() # empty line at the end

            if box_weight > 0:
                if not self.box_on_conveyor:
                    self.get_logger().info('Box detected on conveyor.')
                self.box_on_conveyor = True
            else:
                if self.box_on_conveyor:
                    self.get_logger().info('Box removed from conveyor.')
                self.box_on_conveyor = False

            # Determine box zone based on location
            if box_location == "A":
                self.box_zone = 1
            elif box_location == "B":
                self.box_zone = 2
            elif box_location == "C":
                self.box_zone = 3
            else:
                self.box_zone = 0

        except Exception as e:
            self.get_logger().error(f"Failed to parse JSON: {e}\nRaw msg={msg.data}")


    def make_pose(self, x: float, y: float, yaw: float) -> PoseStamped:
        """x, y in metres, yaw in RADIANS, all in the 'map' frame."""
        ps = PoseStamped()
        ps.header.frame_id = 'map'
        ps.pose.position.x = x
        ps.pose.position.y = y
        half = yaw * 0.5
        ps.pose.orientation.z = math.sin(half)
        ps.pose.orientation.w = math.cos(half)
        return ps

    def send_and_wait_nav(self, pose: PoseStamped) -> bool:
        pose.header.stamp = self.get_clock().now().to_msg()
        goal = NavigateToPose.Goal()
        goal.pose = pose

        def feedback_cb(fb):
                self.get_logger().info(
                    f'Distance remaining: {fb.feedback.distance_remaining:.2f} m',
                    throttle_duration_sec=2.0)

        send_future = self.nav_client.send_goal_async(goal, feedback_callback=feedback_cb)
        rclpy.spin_until_future_complete(self, send_future)
        handle = send_future.result()
        if not handle or not handle.accepted:
            self.get_logger().error('Goal was rejected!')
            return False
        
        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        result = result_future.result()
        if result is None or result.status != GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().error('Goal failed.')
            return False
        return True

    def go_to_waypoint(self, name: str):
        for wp in self.waypoints:
            if wp[0] == name:
                x, y, yaw, wait = wp[1], wp[2], wp[3], wp[4]
                pose = self.make_pose(x, y, yaw)
                if self.send_and_wait_nav(pose):
                    self.get_logger().info(f'Reached waypoint {name}. Waiting for {wait} seconds.')
                    time.sleep(wait)
                else:
                    self.get_logger().error(f'Failed to reach waypoint {name}.')
                return
        self.get_logger().error(f'Waypoint {name} not found.')

    def goal_from_joints(self, joints: List[float]) -> MoveGroup.Goal:
        goal = MoveGroup.Goal()
        req = MotionPlanRequest()
        req.group_name = self.planning_group
        req.num_planning_attempts = 10
        req.allowed_planning_time = 5.0
        req.max_velocity_scaling_factor = 0.5
        req.max_acceleration_scaling_factor = 0.5

        cs = Constraints()
        for name, val in zip(self.joint_names, joints):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = val
            jc.tolerance_above = 0.01
            jc.tolerance_below = 0.01
            jc.weight = 1.0
            cs.joint_constraints.append(jc)

        req.goal_constraints.append(cs)
        goal.request = req
        goal.planning_options.plan_only = False  # plan + execute
        return goal

    def send_and_wait_arm(self, name: str) -> bool:
        for position in self.arm_positions:
            if position[0] == name:
                joints = position[1]
                break
        else:
            self.get_logger().error(f'Arm position {name} not found.')
            return False
        
        self.get_logger().info(f'Sending waypoint: {joints}')

        goal = self.goal_from_joints(joints)

        send_fut = self.moveit_client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_fut)

        handle = send_fut.result()

        if not handle:
            self.get_logger().error('No response received from MoveIt.')
            return False

        if not handle.accepted:
            self.get_logger().error('MoveIt rejected the goal.')
            return False

        self.get_logger().info('Goal accepted. Waiting for execution...')

        res_fut = handle.get_result_async()
        rclpy.spin_until_future_complete(self, res_fut)

        res = res_fut.result()

        if not res:
            self.get_logger().error('No result received.')
            return False

        self.get_logger().info(f'Action status: {res.status}')
        self.get_logger().info(
            f'MoveIt error code: {res.result.error_code.val}'
        )

        if res.status == 4 and res.result.error_code.val == 1:
            self.get_logger().info('Arm pose reached.')
            return True

        self.get_logger().error('Arm pose failed.')
        return False    

    def go_home(self):
        self.robot_active = True
        self.get_logger().info('Going home...')
        self.go_to_waypoint('home')
        self.send_and_wait_arm('carry')
        self.robot_active = False

    def go_pickup_A(self):
        # print to console
        self.robot_active = True
        self.get_logger().info('Going to pickup A...')
        self.send_and_wait_arm('carry')
        self.go_to_waypoint('pickup_A')
        self.send_and_wait_arm('pick')
        self.robot_active = False

    def go_pickup_B(self):
        # print to console
        self.robot_active = True
        self.get_logger().info('Going to pickup B...')
        self.send_and_wait_arm('carry')
        self.go_to_waypoint('pickup_B')
        self.send_and_wait_arm('pick')
        self.robot_active = False

    def go_pickup_C(self):
        # print to console
        self.robot_active = True
        self.get_logger().info('Going to pickup C...')
        self.send_and_wait_arm('carry')
        self.go_to_waypoint('pickup_C')
        self.send_and_wait_arm('pick')
        self.robot_active = False

    def go_dropoff(self):
        # print to console
        self.robot_active = True
        self.get_logger().info('Going to dropoff...')
        self.send_and_wait_arm('carry')
        self.go_to_waypoint('dropoff')
        self.send_and_wait_arm('place')
        self.robot_active = False

    # State machine
    def run(self):
        while rclpy.ok():
            rclpy.spin_once(self)
            
            if self.robot_stuck:
                self.get_logger().warn('Robot is stuck!')
                self.go_home()

            if not self.robot_active:
                if not self.robot_holding_box and self.box_on_conveyor and self.box_zone > 0:
                    if self.box_zone == 1:
                        self.go_pickup_A()
                    elif self.box_zone == 2:
                        self.go_pickup_B()
                    elif self.box_zone == 3:
                        self.go_pickup_C()
                elif self.robot_holding_box:
                    self.go_dropoff()
                else:
                    self.go_home()


def main():
    rclpy.init()
    
    pineapple_navigator = PineappleNavigator()  # Create an instance of the PineappleNavigator node
    try:
        pineapple_navigator.run()
    except KeyboardInterrupt:
        pineapple_navigator.get_logger().info('Interrupted by user.')
    finally:
        pineapple_navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

