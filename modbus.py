import rclpy
from rclpy.node import node
from std_msgs.msg import Bool
from pyModbusTCP.client import ModbusClient

class PLCNode(Node):
    def__init__(self):
        super().__init__('plc_node')
        self.publisher_ = self.create_publisher(Bool, 'door_status', 10)
        self.timer = self.create_timer(1.0, self.read_coil)
        self.client = ModbusClient(host=137.92.208.168, port=502, auto_open=True)

    def read_coil(self):
        coil = self.client.read_coils(1,1)
        if coil:
            msg = Bool()
            msg.data = coil[0]
            self.publisher_.publish(msg)
            self.get.logger().info(f"Door status: {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = PLCNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='main':
    main()

