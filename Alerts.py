from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
import configparser
import io

config = configparser.ConfigParser()
config.read('pimotiondetector.cfg')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt=config['output']['time_stamp_format'])
log = logging.getLogger("pimotiondetector")

def send_alert(picture_stream):
    SMTP_USERNAME = config['alert_settings']['SMTP_USERNAME']	#Mail id of the sender
    SMTP_PASSWORD = config['alert_settings']['SMTP_PASSWORD']	#Pasword of the sender
    SMTP_RECIPIENT = config['alert_settings']['SMTP_RECIPIENT']	#Mail id of the reciever
    SMTP_SERVER = config['alert_settings']['SMTP_SERVER']	#Address of the SMTP server
    SSL_PORT = 465

    # Create the container (outer) email message.
    TO = SMTP_RECIPIENT.split(',')
    FROM = SMTP_USERNAME
    msg = MIMEMultipart()
    msg.preamble = config['alert_settings']['preamble']

    #Attach the image
    # fp = open(image_name_after_event, 'rb')
    img = MIMEImage(picture_stream.getvalue(), _subtype=config['output']['image_format'])
    # fp.close()
    msg.attach(img)

    # Send the email via Gmail.
    log.info("Sending the mail")
    server = smtplib.SMTP_SSL(SMTP_SERVER, SSL_PORT)
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    server.sendmail(FROM, TO, msg.as_string())
    server.quit()