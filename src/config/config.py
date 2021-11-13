import os
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

configured_sensors = {"moisture": "cyan", "temperature": "red"}

data_path = Path("data")
image_path = Path("images")

######################################################################################################
# Sensor Config
moisture_pin = 0
