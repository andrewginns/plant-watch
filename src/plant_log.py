import csv
import time
from datetime import datetime

import numpy as np

# from grove.adc import ADC

from config.config import data_path, moisture_pin


# class GroveMoistureSensor:
#     """
#     Grove Moisture Sensor class
#     Args:
#         pin(int): number of analog pin/channel the sensor connected.
#     """

#     def __init__(self, channel):
#         self.channel = channel
#         self.adc = ADC()

#     @property
#     def moisture(self):
#         """
#         Get the moisture strength value/voltage
#         Returns:
#             (int): voltage, in mV
#         """
#         value = self.adc.read_voltage(self.channel)
#         return value


def main():
    # moisture_sensor = GroveMoistureSensor(moisture_pin)

    print("Detecting moisture...")
    while True:
        moisture_ar = []
        moisture_interval = 30

        for _ in range(0, moisture_interval):
            # m = moisture_sensor.moisture
            m = np.random.randint(2000)
            if 0 <= m and m < 1400:
                result = "Wet"
            elif 1400 <= m and m < 1900:
                result = "Moist"
            else:
                result = "Dry"
            print(f"Moisture value: {m}, {result}")
            moisture_ar.append(m)
            time.sleep(0.1)

        now = datetime.now()
        avg_reading = np.median(moisture_ar)
        print(f"Average reading: {avg_reading}")

        with open(data_path / "moisture_log.csv", "a", newline="") as csvfile:
            sensor_writer = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            sensor_writer.writerow([avg_reading, now.strftime("%Y-%m-%d %H:%M:%S")])


if __name__ == "__main__":
    main()
