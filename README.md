Pimotiondetector
================

Motion detection using the PiCam with storage of videos and images on a network share. Also email/mms a copy of the image.

Goals
==========

1. Explore the capabilities of the Pi B+ model with the NOIR camera. 

2. Build rudimentary capabilities similar to some of the commerically available security cameras, such as upload videos to a network drive, receive alerts when the neighborhood cat decides to pay a visit to the door

3. Explore the wonderful picamera library

Credits
=======

1. This utilizes several of the recipes listed here - http://picamera.readthedocs.org/en/latest/recipes2.html

2. Learnt how to gracefully handle keyboard interrupts from https://github.com/cleesmith/picamera_motion_socket_flask/blob/master/run_on_raspberry_pi/detect_motion_socket_send.py


What's unique
=============

1. Does not save any files locally on the pi and instead writes to a network drive

2. Due to latencies involved with writing remotely, it does all of the i/o on a backgroud theread

Limitations
===========

1. Does not allow streaming live video at the time of the initial commit

2. Does not provide any facility to view the stored videos from outside the network

3. Does not implement any kind of thread pooling so can potentially end up creating several threads 

4. Lest I forget, not suitable for real time production use :)
