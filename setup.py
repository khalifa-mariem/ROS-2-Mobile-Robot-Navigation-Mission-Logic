import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'patrol_boundary_controller'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mariem Khalifa',
    maintainer_email='khalifa.mariem@example.com',
    description='Autonomous Robot Patrol & Boundary Avoidance FSM Controller in ROS 2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'patrol_fsm_node = patrol_boundary_controller.patrol_fsm_node:main',
        ],
    },
)
