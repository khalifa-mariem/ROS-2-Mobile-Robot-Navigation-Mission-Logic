#!/usr/bin/env python3
import math
import random
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim_msgs.msg import Pose


class RobotState(Enum):
    PATROL = auto()
    AVOID_BOUNDARY = auto()
    RECOVER = auto()


class PatrolBoundaryController(Node):
    def __init__(self):
        super().__init__('patrol_boundary_controller')

        self.declare_parameter('min_bound', 1.5)
        self.declare_parameter('max_bound', 9.5)
        self.declare_parameter('linear_speed', 1.8)
        self.declare_parameter('angular_speed', 2.2)

        self.min_bound = self.get_parameter('min_bound').value
        self.max_bound = self.get_parameter('max_bound').value
        self.linear_speed = self.get_parameter('linear_speed').value
        self.angular_speed = self.get_parameter('angular_speed').value

        self.center_x = 5.54
        self.center_y = 5.54

        self.state = RobotState.PATROL
        self.current_pose = None
        self.patrol_turn_bias = 0.0
        self.tick_counter = 0
        self.recover_ticks = 0

        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10
        )

        self.control_timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info('Patrol & Boundary Avoidance FSM Node started at 10 Hz.')

    def pose_callback(self, msg: Pose):
        self.current_pose = msg

    def is_outside_geofence(self) -> bool:
        if self.current_pose is None:
            return False
        x, y = self.current_pose.x, self.current_pose.y
        return (
            x <= self.min_bound
            or x >= self.max_bound
            or y <= self.min_bound
            or y >= self.max_bound
        )

    @staticmethod
    def normalize_angle(angle: float) -> float:
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def transition_to(self, new_state: RobotState):
        if self.state != new_state:
            self.get_logger().info(f'FSM Transition: {self.state.name} -> {new_state.name}')
            self.state = new_state

    def control_loop(self):
        if self.current_pose is None:
            return

        cmd = Twist()
        self.tick_counter += 1

        if self.state == RobotState.PATROL:
            if self.is_outside_geofence():
                self.transition_to(RobotState.AVOID_BOUNDARY)
            else:
                if self.tick_counter % 20 == 0:
                    self.patrol_turn_bias = random.uniform(-0.8, 0.8)

                cmd.linear.x = self.linear_speed
                cmd.angular.z = self.patrol_turn_bias

        elif self.state == RobotState.AVOID_BOUNDARY:
            dx = self.center_x - self.current_pose.x
            dy = self.center_y - self.current_pose.y
            target_theta = math.atan2(dy, dx)
            heading_error = self.normalize_angle(target_theta - self.current_pose.theta)

            if abs(heading_error) > 0.15:
                cmd.linear.x = 0.0
                cmd.angular.z = math.copysign(self.angular_speed, heading_error)
            else:
                self.recover_ticks = 8
                self.transition_to(RobotState.RECOVER)

        elif self.state == RobotState.RECOVER:
            if self.recover_ticks > 0:
                cmd.linear.x = self.linear_speed
                cmd.angular.z = 0.0
                self.recover_ticks -= 1
            else:
                self.patrol_turn_bias = 0.0
                self.transition_to(RobotState.PATROL)

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = PatrolBoundaryController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop_msg = Twist()
        node.cmd_pub.publish(stop_msg)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
