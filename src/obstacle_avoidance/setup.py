from setuptools import setup
import os
from glob import glob

package_name = 'obstacle_avoidance'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Register launch files
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        # Register world files
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.world')),

        # Register urdf files
        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*.urdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@email.com',
    description='Obstacle avoidance robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'obstacle_avoidance_node = obstacle_avoidance.obstacle_avoidance_node:main',
        ],
    },
)
