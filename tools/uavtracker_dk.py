from dronekit import connect
import time

class UAVTracker_DK:
    """Class to track the UAV's latitude and longitude in real-time."""
    def __init__(self, drone_address='udpout:192.168.0.4:14540', usb_path = None, sample_time = 0.1):
        self.latitude = 0.0
        self.longitude = 0.0
        self.drone_address = drone_address
        self.logging_enabled = False
        self.usb_path = usb_path
        self.sample_time = sample_time

    def run(self):
        print("Starting UDP connection to Pixhawk")
        vehicle = connect(self.drone_address)
        print("Pixhawk connected")

        while True:
            self.latitude = vehicle.location.global_frame.lat
            self.latitude = vehicle.location.global_frame.lon
            self.logging_enabled = vehicle.armed
            time.sleep(self.sample_time)