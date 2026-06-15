import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():

    # Get the package directory
    pkg_dir = get_package_share_directory('obstacle_avoidance')

    # Path to our world and urdf files
    world_file = os.path.join(pkg_dir, 'worlds', 'obstacle_world.world')
    urdf_file = os.path.join(pkg_dir, 'urdf', 'robot.urdf')

    # Read the urdf file
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    return LaunchDescription([

        # Start Gazebo with our world
        ExecuteProcess(
            cmd=['gazebo', '--verbose', world_file, '-s', 'libgazebo_ros_factory.so'],
            output='screen'
        ),

        # Publish the robot's description
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_description}]
        ),

        # Spawn the robot into Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=['-topic', 'robot_description', '-entity', 'obstacle_bot'],
            output='screen'
        ),

    ])
