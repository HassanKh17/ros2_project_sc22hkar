import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from cv_bridge import CvBridge
import cv2
import numpy as np
import math
import sys

class ColorDetector(Node):
    def __init__(self):
        super().__init__('color_detector')
        self.bridge = CvBridge() 
        self.sub_image = self.create_subscription(Image, '/camera/image_raw', self.process_image, 10)  # Subscribe to camera
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')  # Create action client

        self.sensitivity = 15  # HSV range tolerance
        self.current_goal = 0  
        self.override_goal = False  # Flag to break navigation if blue is found

        # Waypoints for navigation
        self.goal_list = [
            (-0.966, -5.97, -0.00143),
            (-2.7, -5.55, -0.00143),
            (6.94, -3.92, -0.00143),
            (2.35, -10.6, -0.00143),
        ]

        self.blue_goal = (-2.63, -9.28, -0.00143)  # Final blue override goal

        self.get_logger().info('ColorDetector node started.')
        self.send_next_goal()  # Start navigation

    def send_next_goal(self):
        if self.override_goal or self.current_goal >= len(self.goal_list):
            return
        x, y, theta = self.goal_list[self.current_goal]
        self.current_goal += 1
        self.send_goal(x, y, theta)

    def send_goal(self, x, y, theta):
        if not self.nav_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Nav2 server not available')
            return

        pose = PoseStamped()  # Create pose message
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.orientation.z = math.sin(theta / 2.0)
        pose.pose.orientation.w = math.cos(theta / 2.0)

        goal = NavigateToPose.Goal()
        goal.pose = pose

        self.get_logger().info(f'Sending goal: ({x:.2f}, {y:.2f})')
        self.nav_client.send_goal_async(goal).add_done_callback(self.goal_feedback)

    def goal_feedback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Goal was rejected')
            return
        self.get_logger().info('Goal accepted')
        goal_handle.get_result_async().add_done_callback(self.goal_result)

    def goal_result(self, future):
        if self.override_goal:
            self.get_logger().info('Reached BLUE goal. Exiting.')
            cv2.destroyAllWindows()
            rclpy.shutdown()
            sys.exit(0)
        else:
            self.get_logger().info('Reached goal. Moving to next.')
            self.send_next_goal()

    def process_color_mask(self, mask, color, bgr, check_for_blue=False):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            if area > 500:
                x, y, w, h = cv2.boundingRect(c)
                (cx, cy), radius = cv2.minEnclosingCircle(c)
                cv2.drawContours(self.img_disp, [c], -1, bgr, 2)
                cv2.rectangle(self.img_disp, (x, y), (x + w, y + h), bgr, 2)
                cv2.circle(self.img_disp, (int(cx), int(cy)), int(radius), bgr, 2)
                cv2.putText(self.img_disp, f'{color}', (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, bgr, 2)
                self.get_logger().info(f'{color} detected (area: {int(area)})')
                if color == 'Blue' and not self.override_goal and check_for_blue:
                    self.get_logger().info('Blue detected. Redirecting to BLUE goal.')
                    self.override_goal = True
                    self.send_goal(*self.blue_goal)

    def process_image(self, msg):
        try:
            img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')  # Convert image
        except Exception as e:
            self.get_logger().error(f'CV Bridge Error: {e}')
            return

        self.img_disp = img.copy()  # Copy for drawing
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert to HSV

        # Create masks
        red_mask = cv2.inRange(hsv, (0 - self.sensitivity, 100, 100), (0 + self.sensitivity, 255, 255))
        green_mask = cv2.inRange(hsv, (60 - self.sensitivity, 100, 100), (60 + self.sensitivity, 255, 255))
        blue_mask = cv2.inRange(hsv, (100, 150, 50), (140, 255, 255))

        # Detect and draw contours
        self.process_color_mask(red_mask, 'Red', (0, 0, 255))
        self.process_color_mask(green_mask, 'Green', (0, 255, 0))
        self.process_color_mask(blue_mask, 'Blue', (255, 0, 0), check_for_blue=True)

        cv2.imshow('Detected Colors', self.img_disp)  # Show result
        cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)  
    node = ColorDetector() 
    rclpy.spin(node)  
    node.destroy_node() 
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
