import os
from pathlib import Path

# Find the root path of the project
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

configured_sensors = {"moisture": "cyan", "temperature": "red", "humidity": "yellow"}

data_path = ROOT_DIR / "data"
# data_path = Path("/Volumes/PiShare/data_store") # Example path for a Raspberry pi server share
image_path = ROOT_DIR / "images"


# Dashboard update frequency in seconds
dashboard_update = 10

# Prediction update frequency in loops (e.g. 5 mins per loop, 250 loops ~= 1 day)
prediction_update = 25

# Optional homeassistant integration
homeassistant_integration = False
clientname = "Malfoy"
hostname = ''
port = 1883
timeout = 60
hass_username = ""
hass_password = ""
mqtt_topic_root = "home/plants/malfoy/"

######################################################################################################
# Sensor Config
moisture_pin = 0
temp_humid_pin = 12

sensor_dry = 2000
sensor_wet = 1400

######################################################################################################
# Thresholds
water_threshold_pct = 10
target_water_moisture = 71
