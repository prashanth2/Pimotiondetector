import io
import picamera
import picamera.array
import sys
import signal
import logging
from PIL import Image
import datetime
import configparser
import numpy as np
from BackgroundStreamProcessWrapper import BackgroundStreamProcessWrapper
from Alerts import send_alert

config = configparser.ConfigParser()
config.read('pimotiondetector.cfg')

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("pimotiondetector")

file_output_location = config['output']['file_storage_path']

# frequency of the motion detection analysis, in seconds
motion_detection_sense_interval = config.getint('camera_settings', 'motion_detection_sense_interval')
motion_stop_sense_interval = config.getint('camera_settings', 'motion_stop_sense_interval')

video_format = config['camera_settings']['video_format']

time_stamp_format = config['output']['time_stamp_format']

# TODO: find another way of encapsulating the output of the motion analysis
motion_detected = False

def signal_term_handler(signal, frame):
  log.warning('stopping pimotiondetector...')
  sys.exit(0)

signal.signal(signal.SIGTERM, signal_term_handler)

class DetectMotion(picamera.array.PiMotionAnalysis):

    def analyse(self, a):
        global motion_detected

        # Set the value to false so it is set each time this module runs
        motion_detected = False

        a = np.sqrt(
            np.square(a['x'].astype(np.float)) +
            np.square(a['y'].astype(np.float))
            ).clip(0, 255).astype(np.uint8)

        # TODO: The recipe calls this crude - need to find another way?
        # If there're more than 10 vectors with a magnitude greater
        # than 60, then say we've detected motion
        if (a > 60).sum() > 10:
            motion_detected = True

def write_video(stream, event_id):

    # write the content of the circular buffer leading upto the event
    # it appears that it captures the entire event :)
    for frame in stream.frames:
        if frame.frame_type == picamera.PiVideoFrameType.sps_header:
            stream.seek(frame.position)
            break

    video_name_before_event = '{0}vid{1}.{2}'.format(file_output_location, event_id, video_format)
    with io.open(video_name_before_event, 'wb') as output:
            output.write(stream.getvalue())

def initialize_camera():
    # todo: get tuple from the config file
    camera.resolution = (1280, 720)

    # depending on how the camera is mounted, you may have to invert the image
    camera.vflip = config.getboolean('camera_settings', 'vertical_flip')
    camera.hflip = config.getboolean('camera_settings','horizontal_flip')
    camera.framerate = config.getfloat('camera_settings', 'frame_rate')

def process_picture(picture_stream, event_id):

    image_name_after_event = '{0}img-{1}.{2}'.format(file_output_location, event_id, config['camera_settings']['image_extension'])

    image = Image.open(picture_stream)
    image.save(image_name_after_event, config['output']['image_format'])
    # send_alert(image_name_after_event)
    send_alert(picture_stream)


with picamera.PiCamera() as camera:
    try:

        initialize_camera()

        detection_stream = picamera.PiCameraCircularIO(camera, seconds=config.getint('camera_settings', 'circular_stream_capture_duration'))
        stop_stream = picamera.PiCameraCircularIO(camera, seconds=config.getint('camera_settings', 'circular_stream_capture_duration'))

        with DetectMotion(camera) as motion_detection_output:
            camera.start_recording(detection_stream, format=video_format, motion_output=motion_detection_output)
            while True:
                camera.wait_recording(motion_detection_sense_interval)
                if motion_detected:

                    event_id =  datetime.datetime.now().strftime(time_stamp_format)

                    log.info('Movement sensed!')

                    # take a picture
                    pictureStream = io.BytesIO()
                    camera.capture(pictureStream, format=config['camera_settings']['image_format'], use_video_port=True)

                    # send it off of background processing
                    BackgroundStreamProcessWrapper(process_picture, pictureStream, event_id, True)

                    # once detected, split the recording to record the frames after the event
                    # using a stream since writing to a file is really slow - especially over the network
                    camera.split_recording(stop_stream)

                    file_name = "-before-" + event_id
                    # write the in-memory circular buffer in the background
                    BackgroundStreamProcessWrapper(write_video, detection_stream, file_name)

                    # continue to record until the movement stops
                    while motion_detected:
                        camera.wait_recording(motion_stop_sense_interval)

                    # write this to a file - keep in mind you will only have the last x seconds of video
                    # after movement was detected.
                    file_name = "-after-" + event_id
                    BackgroundStreamProcessWrapper(write_video, stop_stream, file_name)

                    log.info('Movement stopped')
                    camera.split_recording(detection_stream)
    except KeyboardInterrupt as e:
        log.info("Execution being interrupted")
    finally:
            camera.stop_recording()
            log.info("motion detection ended")

