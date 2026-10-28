# Clipping out
1. Go to shelves where you deposit boxes.
2. Drive into corner. 
3. Manipulate arm to 45 degree angle so it pulls you up the wall. Keep driving into the corner.
4. Clip through the windows. The windows have no collison. 

# Easter Eggs
## Rocket ship
There is a large pineapple themed rocket ship on the left side of the warehouse
Hitting it with the robot causes it to float off with 0 gravity

## Han shot first
The topic */virtual_hand_solo/han_shot_first* publishes data from the virtual camera sensors
This data is a *sensor_msgs/msg/Image* type, with 2097152 rows of numbers between 0 and 255, parsable as an RGBa image
Reading and displaying this data using *ros2 run rqt_image_view rqt_image_view* gives an image of Han Solo which randomly flashes different hues every half second
