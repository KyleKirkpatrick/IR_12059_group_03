import math
import time

import rclpy
from rclpy.action import ActionClient
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, JointConstraint


def make_pose(x: float, y: float, yaw: float) -> PoseStamped:
    """x, y in metres, yaw in RADIANS, all in the 'map' frame."""
    ps = PoseStamped()
    ps.header.frame_id = 'map'
    ps.pose.position.x = x
    ps.pose.position.y = y
    half = yaw * 0.5
    ps.pose.orientation.z = math.sin(half)
    ps.pose.orientation.w = math.cos(half)
    return ps

def send_and_wait(pose: PoseStamped) -> bool:
        pose.header.stamp = node.get_clock().now().to_msg()
        goal = NavigateToPose.Goal()
        goal.pose = pose

def feedback_cb(fb):
            node.get_logger().info(
                f'Distance remaining: {fb.feedback.distance_remaining:.2f} m',
                throttle_duration_sec=2.0)

def go_home():
    # print to console
    node.get_logger().info('Going home...')

def main():
    go_home()


if __name__ == '__main__':
    main()

