import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class WarehouseEavesdropper(Node):
    def __init__(self):
        super().__init__('plc_hmi_listener') # Node name
        
        # Create subscriber: topic_name, message_type, callback_function
        self.subscription = self.create_subscription(
            String,
            'warehouse_tea_spill',
            self.listener_callback,
            10)

    def listener_callback(self, msg):
        self.get_logger().info(f'I heard warehouse gossip: "{msg.data}"')

def main(args=None):
    rclpy.init(args=args)
    plc_hmi_listener = WarehouseEavesdropper()
    rclpy.spin(plc_hmi_listener)
    plc_hmi_listener.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

