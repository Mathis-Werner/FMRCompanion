import smbus2
import threading
import time
import asyncio
from tools import Logger
from tools import UAVTracker
from threads import sensorReadout

# Sample times (s)
sensorReadout_sample_time = 0.01
logger_sample_time = 1

# Setup I2C port 1 of the RasPi
bus = smbus2.SMBus(1)
# Setup Logger
logger = Logger(sample_time=logger_sample_time)
# Setup drone object for telemetry
drone = UAVTracker()

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
        log_date_time = drone.current_log_datetime
        print("Hello World!")
        logger.create_csv(log_date_time)
        print("log_date_time")
    # Write collected data to csv (sensor data already loaded to buffer)
    if drone.logging_enabled:
        logger.log_data("Latitude", drone.latitude)
        logger.log_data("Longitude", drone.longitude)
        logger.write_data_to_csv()
        
    previous_logging_state = drone.logging_enabled
    time.sleep(logger.sample_time)
