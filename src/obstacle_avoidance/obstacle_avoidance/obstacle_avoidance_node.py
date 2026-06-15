import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import math
import random

# Robot states
FORWARD  = 'FORWARD'
BACKUP   = 'BACKUP'
TURNING  = 'TURNING'

class ObstacleAvoider(Node):

    def __init__(self):
        super().__init__('obstacle_avoider')

        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.danger_distance  = 0.35
        self.warning_distance = 0.7

        # State machine variables
        self.state            = FORWARD
        self.locked_direction = 1.0   # 1.0 = left, -1.0 = right
        self.state_counter    = 0     # how many callbacks in current state

        self.get_logger().info('Obstacle Avoider Started!')

    def get_valid_min(self, ranges):
        valid = [r for r in ranges
                 if not math.isinf(r) and not math.isnan(r) and r > 0.05]
        return min(valid) if valid else 10.0

    def scan_callback(self, msg):
        ranges = msg.ranges
        total  = len(ranges)

        front = list(ranges[0:30])       + list(ranges[total-30:total])
        left  = list(ranges[30:120])
        right = list(ranges[total-120:total-30])

        front_dist = self.get_valid_min(front)
        left_dist  = self.get_valid_min(left)
        right_dist = self.get_valid_min(right)

        move = Twist()
        self.state_counter += 1

        # ── STATE: FORWARD ──────────────────────────────────────
        if self.state == FORWARD:
            if front_dist < self.danger_distance:
                # Too close — switch to BACKUP
                self.state         = BACKUP
                self.state_counter = 0
                # Lock direction NOW based on which side is more open
                if left_dist >= right_dist:
                    self.locked_direction =  1.0
                else:
                    self.locked_direction = -1.0
                self.get_logger().info(
                    f'→ BACKUP | front:{front_dist:.2f} L:{left_dist:.2f} R:{right_dist:.2f} | dir:{"LEFT" if self.locked_direction > 0 else "RIGHT"}')

            elif front_dist < self.warning_distance:
                # Getting close — switch to TURNING
                self.state         = TURNING
                self.state_counter = 0
                if left_dist >= right_dist:
                    self.locked_direction =  1.0
                else:
                    self.locked_direction = -1.0
                self.get_logger().info(
                    f'→ TURNING | front:{front_dist:.2f} L:{left_dist:.2f} R:{right_dist:.2f} | dir:{"LEFT" if self.locked_direction > 0 else "RIGHT"}')

            else:
                move.linear.x  = 0.5
                move.angular.z = 0.0
                self.get_logger().info(f'FORWARD | {front_dist:.2f}m')

        # ── STATE: BACKUP ───────────────────────────────────────
        elif self.state == BACKUP:
            # Back up for 20 callbacks then switch to TURNING
            if self.state_counter < 20:
                move.linear.x  = -0.3
                move.angular.z = 0.0
                self.get_logger().info(f'BACKING UP | {front_dist:.2f}m')
            else:
                self.state         = TURNING
                self.state_counter = 0
                self.get_logger().info('→ TURNING after backup')

        # ── STATE: TURNING ──────────────────────────────────────
        elif self.state == TURNING:
            if front_dist > self.warning_distance:
                # We're clear! Go back to FORWARD
                self.state         = FORWARD
                self.state_counter = 0
                self.get_logger().info('→ FORWARD — path is clear!')
            else:
                # Keep turning in the LOCKED direction — no flipping!
                move.linear.x  = 0.0
                move.angular.z = self.locked_direction * 5.0
                self.get_logger().info(
                    f'TURNING {"LEFT" if self.locked_direction > 0 else "RIGHT"} | front:{front_dist:.2f}m | count:{self.state_counter}')

                # If turning for too long — force re-evaluate direction
                if self.state_counter > 80:
                    self.locked_direction = random.choice([1.0, -1.0])
                    self.state_counter    = 0
                    self.get_logger().info('FORCE DIRECTION CHANGE!')

        self.publisher.publish(move)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
