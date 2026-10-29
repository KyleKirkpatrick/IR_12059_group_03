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

# Copy protected files
sudo cp -r [source-file-path] [destination-file path]
# sudo      : run elevated as root
# cp        : copy
# -r        : recursive (copies all files in the folder and subfolders)

# COPYING THE PLC SOLUTION INTO YOUR DOCKER CONTAINER
# In your irs_world folder there is a folder called "openplc-editor"
# openplc-editor/data has a symbolic link to the "editor-data" folder in the OpenPLC docker container
# Download the PLC solution from our github repo: 
IR_12059_group_03/labs/lab_03/plc_lab_03
# openplc-edit/data is a protected folder. You need root permission to copy there. 
# Adapt the cp command above to copy plc_lab_03 to openplc-edit/data
# Once copied, you can open the PLC solution in OpenPLC editor. 
# In the OpenPLC Open Project dialog, navigate to /editor-data (from root) to find the plc_lab_03 folder. 


#----------------------------------------------------------------------#
# Docker commands
#----------------------------------------------------------------------#

# Add the local root user to allowed list to connect to X11 display server
xhost +local:root

# Update container
docker compose pull

# Start container
docker compose up

# Start irs_world with alternate Nvidia compose file
docker compose -f compose-nvidia.yaml up

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

# Compose.yaml settings
command: ros2 launch handsolo_ros handsolo.launch.py tm_use_simulation:=true use_arm:=true use_base:=false use_moveit:=true use_nav2:=false use_rviz:=tru
ROS_DOMAIN_ID=3


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

ros2 topic echo /topic_name

ros2 topic echo /joint_states --once

ros2 topic hz /joint_states

ros2 topic info /joint_states -v

ros2 interface show sensor_msgs/msg/JointState

ros2 pkg create --build-type ament_python --license Apache-2.0 --node-name
pineapple_gossip_bot pa_warehouse_status

cd ~/irs_ws
colcon build --packages-select pa_warehouse_status
source install/local_setup.bash
ros2 run pa_warehouse_status pineapple_gossip_bot

cd ~/irs_ws
colcon build --packages-select pa_warehouse_status
source install/local_setup.bash
ros2 run pa_warehouse_status pineapple_gossip_bot

ros2 node list # See all active nodes
ros2 topic info /status_updates # Get topic information
ros2 interface show std_msgs/String # Examine message structure


#----------------------------------------------------------------------#
# Code server commands
#----------------------------------------------------------------------#

# You can connect to the code server on the Omron workspace by either
# using the web portal or by connecting desktop VS Code to the container. 

# Open the web portal (type in browser while container is running)
localhost:8080

# Alternatively, connect to the code server using VS Code desktop. 
# Benefits: 
#   - don't have to sign in to Github every time. 
#   - better contextual auto-complete in terminal
#   - copy & paste easily
#   - full vs code; saved settings
# Issues:
#   - Bash terminal may need additional setup to access ROS commands
#
# Instructions:
# 1. Open VS Code and install 'Dev Containers' extension. 
# 2. Run the docker container
# 3. Use the command palette (Ctrl + Shift + P) and select:
#   Dev Containers: Attach to Running Container
# 4. Select omron-workspace-1
# 5. It will take some time to connect to the container. 
# 6. Open the workspace folder /workspace/irs_ws
# 7. [Optional] Go to File > Add Folder to Workspace...
#   Select the group repo IR_12059_group_03
#   This lets you push/pull from git in the same workspace. 
# 8. Open a terminal (Ctrl + Shift + `). 
#   Select "irs_ws" as the source. 
# 9. Add ROS commands to the bash environment. 
source /opt/ros/jazzy/setup.bash

# To have those commands available in every new terminal 
# (in this context), add the ros source to bashrc
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc

# If you haven't yet, run colcon build to build the scripts
cd ~/irs_ws
colcon build

# and 