import asyncio
from mavsdk import System

class UAVTracker:
    """Class to track the UAV's latitude and longitude in real-time."""
    def __init__(self, drone_address="udp://192.168.0.4:14540", logging_switch_channel=7):
        self.drone = System()
        self.latitude = 0.0
        self.longitude = 0.0
        self.drone_address = drone_address
        self.logging_switch_channel = logging_switch_channel
        self.logging_enabled = False
        self.current_log_datetime = None
        self._download_trigger = asyncio.Event()
        self.previous_logging_state = False

    async def run(self):
        """Main function to handle communication with UAV."""
        print("Waiting for connection to Drone")
        await self.drone.connect(system_address=self.drone_address)
        print("Drone Mavlink stream connected")

        # Keep all tasks running (Add new communication tasks here)
        await asyncio.gather(
            self.getPosition(),
            self.getLoggingSwitch(),
            self.updateLogDateTime()
        )
    
    async def getPosition(self):
        """Continuously updates latitude and longitude from telemetry."""
        async for position in self.drone.telemetry.position():
            self.latitude = position.latitude_deg
            self.longitude = position.longitude_deg
    
    async def getLoggingSwitch(self):
        """Continuously checks arm status and enables logging flag when armed."""
        async for armed in self.drone.telemetry.armed():
            self.logging_enabled = armed

    async def updateLogDateTime(self):
        """When vehicle gets armed get date time of current log."""
        while True:
            if not self.previous_logging_state and self.logging_enabled:
                entries = await self.drone.log_files.get_entries()
                if entries:
                    newest_entry = entries[-1]  # entries are sorted oldest → newest
                    self.current_log_datetime = newest_entry.date.replace(":", "-")
            self.previous_logging_state = self.logging_enabled
            await asyncio.sleep(0.1)

    def trigger_log_download(self):
        """Call this to trigger download of log."""
        self._download_trigger.set()

    def run_in_thread(self):
        """Setup seperate event loop to run in thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.run())