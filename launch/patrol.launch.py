from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim',
            output='screen',
            parameters=[{
                'background_r': 255,
                'background_g': 209,
                'background_b': 220,
            }]
        ),
        TimerAction(
            period=1.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'service', 'call',
                        '/turtle1/set_pen', 'turtlesim_msgs/srv/SetPen',
                        "{r: 185, g: 45, b: 95, width: 3, 'off': 0}"
                    ],
                    output='screen'
                )
            ]
        ),
        Node(
            package='patrol_boundary_controller',
            executable='patrol_fsm_node',
            name='patrol_boundary_controller',
            output='screen',
            parameters=[{
                'min_bound': 1.5,
                'max_bound': 9.5,
                'linear_speed': 1.8,
                'angular_speed': 2.2,
            }]
        ),
    ])
