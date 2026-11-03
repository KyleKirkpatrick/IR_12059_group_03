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

# Robot status flags
robot_holding_box = False
robot_stuck = False
box_on_conveyor = False

class PineappleNavigator(Node):
    def __init__(self):
        super().__init__('pineapple_navigator')

        # Create subscriber: topic_name, message_type, callback_function
        self.subscription = self.create_subscription(
            String,
            'hmi/unified_status',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
            try:
                data = json.loads(msg.data) # parse JSON string into Python dict
                stamp = data["stamp"]
                box = data["box"]
                counts = data["counts"]
    
                print("Received PLC status:")
                print(f" Time: {stamp['sec']}.{stamp['nanosec']}")
                print(f" Box weight raw={box['weight_raw']}")
                print(f" Location: {box['location']}")
                print(f" Counts: big={counts['big']}, medium={counts['medium']}, "f"small={counts['small']}, total={counts['total']}")
                print() # empty line at the end

                if box['weight_raw'] > 0:
                    box_on_conveyor = True
                else:
                    box_on_conveyor = False

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



def main():
    rclpy.init()
    
    pineapple_navigator = PineappleNavigator()  # Create an instance of the PineappleNavigator node
    rclpy.spin(pineapple_navigator)        # Keep the node alive to process callbacks
    try:
        pineapple_navigator.run()
    except KeyboardInterrupt:
        pineapple_navigator.get_logger().info('Interrupted by user.')
    finally:
        pineapple_navigator.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

