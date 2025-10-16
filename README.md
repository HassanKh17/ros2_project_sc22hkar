
# 🤖 RGB Box Detection and Autonomous Navigation (ROS2 + Gazebo)

## 📌 Project Overview

This project demonstrates a complete **autonomous robotic system** in a simulated Gazebo environment using **ROS 2**, combining **motion planning** and **computer vision**.
[![Watch the video](https://img.youtube.com/vi/OusBsx283k8/maxresdefault.jpg)](https://youtu.be/OusBsx283k8)

The robot is programmed to:
- **Navigate through predefined waypoints** using the Nav2 stack.
- **Detect RGB boxes (Red, Green, Blue)** using a live camera feed.
- **Identify and prioritize the blue box**: if the robot detects a blue box in view, it will **abort its current path** and instead **navigate directly to the blue box**, stopping within ~1 meter.

> 💡 Each grid block on the ground is 1x1 meter, and each RGB box is 1m³.

---

## 🎯 Project Aim

To apply motion planning and computer vision techniques in ROS2 to solve a real-world robotic perception and navigation task.

---

## ✅ Project Objectives

- Implement and use ROS2 nodes in Python.
- Utilise **Nav2** for autonomous motion planning and goal setting.
- Apply **OpenCV** to process camera images and detect colored objects.
- Integrate **action handling** to dynamically redirect navigation based on visual input.

---

## 🧩 System Components

| Component         | Role                                                     |
|------------------|----------------------------------------------------------|
| `sensor_msgs/Image` | Camera feed topic                                       |
| `cv_bridge`       | Converts ROS image messages to OpenCV format             |
| `OpenCV`          | Processes the image to detect red, green, and blue boxes|
| `nav2_msgs/Action`| Used to send navigation goals to the robot              |
| `Gazebo`          | Simulates the environment                                |
| `rclpy`           | ROS 2 Python client library                              |

---

## 🚦 How It Works

1. **Startup**
   - The robot launches with an active camera and begins navigating through a set of pre-defined goals using Nav2.

2. **Vision Detection**
   - The image from `/camera/image_raw` is processed using OpenCV (HSV filtering).
   - Red, green, and blue boxes are identified and highlighted using contours.

3. **Override Navigation**
   - If a **blue box** is detected:
     - A flag is triggered to override all future navigation goals.
     - The robot immediately navigates toward a **hardcoded location** close to the blue box (`~1m` away).
     - The system then shuts down after reaching the final blue goal.

4. **Live Visualization**
   - A display window shows the detected boxes with bounding rectangles and color labels.

---

