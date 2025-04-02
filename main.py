import smbus2
import threading
import time
import asyncio
from tools import Logger
from tools import UAVTracker
from tools import detect_USB_drive
from threads import sensorReadout

# Sample times (s)
sensorReadout_sample_time = 0.01
logger_sample_time = 1

# Run init functions
usb_path = detect_USB_drive()
# Setup I2C port 1 of the RasPi
bus = smbus2.SMBus(1)
# Setup Logger
logger = Logger(usb_path=usb_path, sample_time=logger_sample_time)
# Setup drone object for telemetry
drone = UAVTracker(usb_path=usb_path)

# Initialise threads
sensorReadoutThread = threading.Thread(target=sensorReadout, args=(logger, bus, sensorReadout_sample_time), daemon=True)
updateDroneThread = threading.Thread(target=drone.run_in_thread, daemon=True)

# Start threads
sensorReadoutThread.start()
updateDroneThread.start()

# Setup dummy variable to detect True False transition in logging switch
previous_logging_state = False

# Main loop (mainly used for logging and to keep threads running)
while True:
    # If logging switch changes from True to False create new csv with the date time of the log created by PX4
    if not previous_logging_state and drone.logging_enabled:
        logger.create_csv()
    # Write collected data to csv (sensor data already loaded to buffer)
    if drone.logging_enabled:
        logger.log_data("Latitude", drone.latitude)
        logger.log_data("Longitude", drone.longitude)
        logger.write_data_to_csv()
        
    previous_logging_state = drone.logging_enabled
    time.sleep(logger.sample_time)
