#----------------------------------------------------------------------#
# Common commands for Industrial Robots and Systems (IRS)
#----------------------------------------------------------------------#

# This is a reference list, do not run this file as a script

#----------------------------------------------------------------------#
# Terminal commands
#----------------------------------------------------------------------#

# Search for a file
find [path] [options] [expression]

# Find, in this directory and it's subfolders, a file, with .urdf in the name. 
# (* is a wildcard character)
find ./ -type f -name "*.urdf*"

# Display file contents to terminal
cat [filename]



#----------------------------------------------------------------------#
# Docker commands
#----------------------------------------------------------------------#

# Add the local root user to allowed list to connect to X11 display server
xhost +local:root

# Update container
docker compose pull

# Start container
docker compose up

# Stop running container
# key command [ctrl] + [c]
# wait for the applications to gracefully stop, or do again to force quit

# Close container (frees space)
docker compose down

# List containers
docker ps

# Clear all unused data (frees space)
docker system prune -a

# Step inside omron-handsolo container
docker exec -it omron_handsolo bash

# Add local user to docker group (so you don't need sudo for every command)
sudo usermod -aG docker $USER
newgrp docker   # Refreshes list

#----------------------------------------------------------------------#
# Git commands
#----------------------------------------------------------------------#

# Set user details
git config --global user.name "Your Name"
git config --global user.email "Your Email"



#----------------------------------------------------------------------#
# ROS2 commands
#----------------------------------------------------------------------#

ros2 topic list

ros2 topic echo /joint_states --once

ros2 topic hz /joint_states

ros2 topic info /joint_states -v

ros2 interface show sensor_msgs/msg/JointState


