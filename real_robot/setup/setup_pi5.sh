#!/usr/bin/env bash
# One-time setup of a Raspberry Pi 5 (or any Ubuntu computer) for the HospitalNav-v1 ROS 2
# package: ROS 2, SLAM Toolbox, Nav2 and the Python packages the controller needs.
#
#   bash setup_pi5.sh            # Ubuntu 24.04 + ROS 2 Jazzy (as in the paper's trials)
#   bash setup_pi5.sh humble     # Ubuntu 22.04 + ROS 2 Humble
set -e
DISTRO="${1:-jazzy}"
PIP_FLAGS=""
# Ubuntu 24.04 protects the system Python; allow pip to install next to the ROS packages.
if [ "$(lsb_release -rs 2>/dev/null)" = "24.04" ]; then PIP_FLAGS="--break-system-packages"; fi

echo "[1/5] locale + apt sources"
sudo apt update
sudo apt install -y locales curl gnupg lsb-release
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
     -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | \
     sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

echo "[2/5] ROS 2 ${DISTRO} + SLAM + Nav2"
sudo apt update
sudo apt install -y ros-${DISTRO}-ros-base python3-colcon-common-extensions \
     ros-${DISTRO}-slam-toolbox ros-${DISTRO}-navigation2 ros-${DISTRO}-nav2-bringup \
     ros-${DISTRO}-tf-transformations ros-${DISTRO}-rviz2
# Optional off-the-shelf LiDAR driver (skip if using our self-contained lidar_node)
sudo apt install -y ros-${DISTRO}-ldlidar-stl-ros2 || true

echo "[3/5] python deps"
python3 -m pip install $PIP_FLAGS torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install $PIP_FLAGS stable-baselines3 numpy pillow pyserial

echo "[4/5] environment"
grep -q "source /opt/ros/${DISTRO}/setup.bash" ~/.bashrc || \
     echo "source /opt/ros/${DISTRO}/setup.bash" >> ~/.bashrc
grep -q 'ROS_DOMAIN_ID' ~/.bashrc || echo 'export ROS_DOMAIN_ID=17' >> ~/.bashrc
grep -q 'ROS_LOCALHOST_ONLY' ~/.bashrc || echo 'export ROS_LOCALHOST_ONLY=0' >> ~/.bashrc

echo "[5/5] done. Open a NEW terminal, then:"
echo "   cd ~/hn_ws && colcon build && source install/setup.bash"
