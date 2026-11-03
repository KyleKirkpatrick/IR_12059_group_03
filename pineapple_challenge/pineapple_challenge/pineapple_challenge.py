import math
from platform import node
import time

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

    # Robot status flags 
    global robot_holding_box, robot_stuck, box_on_conveyor, box_zone
    robot_holding_box = False
    robot_stuck = False
    box_on_conveyor = False
    box_zone = 0

    def __init__(self):
        super().__init__('pineapple_navigator')

        # Create subscriber: topic_name, message_type, callback_function
        self.subscription = self.create_subscription(
            String,
            'hmi/unified_status',
            self.listener_callback,
            10)

        # Run the state machine
        self.run()

    def listener_callback(self, msg):
        global box_on_conveyor, box_zone

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

        except Exception as e:
            self.get_logger().error(f"Failed to parse JSON: {e}\nRaw msg={msg.data}")

        if box_weight > 0:
            if not box_on_conveyor:
                self.get_logger().info('Box detected on conveyor.')
            box_on_conveyor = True
        else:
            if box_on_conveyor:
                self.get_logger().info('Box removed from conveyor.')
            box_on_conveyor = False

        # Determine box zone based on location
        if box_location == "A":
            box_zone = 1
        elif box_location == "B":
            box_zone = 2
        elif box_location == "C":
            box_zone = 3
        else:
            box_zone = 0

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

    def send_and_wait(self, pose: PoseStamped) -> bool:
        pose.header.stamp = self.get_clock().now().to_msg()
        goal = NavigateToPose.Goal()
        goal.pose = pose

    def feedback_cb(self, fb):
        self.get_logger().info(
            f'Distance remaining: {fb.feedback.distance_remaining:.2f} m',
            throttle_duration_sec=2.0)

    def go_home(self):
        # print to console
        self.get_logger().info('Going home...')

    def go_pickup_A(self):
        # print to console
        self.get_logger().info('Going to pickup A...')

    def go_pickup_B(self):
        # print to console
        self.get_logger().info('Going to pickup B...')

    def go_pickup_C(self):
        # print to console
        self.get_logger().info('Going to pickup C...')

    def go_dropoff(self):
        # print to console
        self.get_logger().info('Going to dropoff...')

    # State machine
    def run(self):
        global robot_holding_box, robot_stuck, box_on_conveyor, box_zone
        while rclpy.ok():
            rclpy.spin_once(self)
            if robot_stuck:
                self.get_logger().warn('Robot is stuck!')
                self.go_home()
            if not robot_holding_box and box_on_conveyor and box_zone > 0:
                if box_zone == 1:
                    self.go_pickup_A()
                elif box_zone == 2:
                    self.go_pickup_B()
                elif box_zone == 3:
                    self.go_pickup_C()
            elif robot_holding_box:
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

