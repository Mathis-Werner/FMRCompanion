import smbus2
import threading
import time
from tools import Logger
from tools import UAVTracker
from threads import sensorReadout

# Setup I2C port 1 of the RasPi
bus = smbus2.SMBus(1)
# Setup Logger
logger = Logger()
# Setup drone object for telemetry
drone = UAVTracker()

sensorReadoutThread = threading.Thread(target=sensorReadout(logger, bus), daemon=True)
updateDroneThread = threading.Thread(target=drone.run(), daemon=True)

sensorReadoutThread.start()
updateDroneThread.start()

# Setup dummy variable to detect True false transition in logging switch
previous_logging_state = False

while True:
    if not previous_logging_state and drone.logging_enabled:
        logger.create_csv
        previous_logging_state = drone.logging_enabled
    if drone.logging_enabled:
        logger.log_data("Latitude", drone.latitude)
        logger.log_data("Longitude", drone.longitude)
        logger.write_data_to_csv()
    time.sleep(logger.sample_time)
