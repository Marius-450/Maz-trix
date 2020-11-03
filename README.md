# Maz-trix
A little maze game for MatrixPortal M4 with a 64x32 RGB matrix, driven by the accelerometer.
<img src="https://raw.githubusercontent.com/Marius-450/screenshots/master/DSCF1901.JPG" width="450" align="right">

## Requirements 

### material

* MatrixPortal M4
* 64x32 RGB matrix

### libs

* adafruit_display_text
* adafruit_display_shapes
* adafruit_matrixportal
* adafruit_imageload
* adafruit_lis3dh
<img src="https://raw.githubusercontent.com/Marius-450/screenshots/master/maztrix.1.gif" align="right">

## Buttons

* UP : toggle demo mode. default : off
* DOWN : change color theme.

## Auto-demo mode

After 5 minutes of inactivity, demo mode is activated.
During demo mode, moving the matrix deactivate the demo mode.

## Todo

* Use nvm to store config : demo mode, color theme.
* Change color theme randomly in demo mode.
* Animate the goal and the ball.

