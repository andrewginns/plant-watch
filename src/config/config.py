import os
from pathlib import Path

ROOT_DIR = Path(
    os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
)

configured_sensors = {"moisture": "cyan",
                      "temperature": "red", "humidity": "yellow"}

data_path = ROOT_DIR / "data"
image_path = ROOT_DIR / "images"

# Dashboard update frequency in seconds
dashboard_update = 10

######################################################################################################
# Sensor Config
moisture_pin = 0
temp_humid_pin = 12

sensor_dry = 2000
sensor_wet = 1400
