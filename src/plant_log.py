"""

Requires install:
```
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
cd  Adafruit_Python_DHT`
sudo python3 setup.py install
```
"""

import csv
from datetime import datetime

import Adafruit_DHT
import numpy as np
from grove.adc import ADC

from config import data_path, configured_sensors, moisture_pin, temp_humid_pin


class GroveMoistureSensor:
    """
    Grove Moisture Sensor class
    Args:
        pin(int): number of analog pin/channel the sensor connected.
    """

    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def moisture(self):
        """
        Get the moisture strength value/voltage
        Returns:
            (int): voltage, in mV
        """
        value = self.adc.read_voltage(self.channel)
        return value


class GroveHumidityTemperatureSensor:
    """
    Grove Humidity and Temperature (DHT11) Sensor class
    Args:
        pin(int): number of analog pin/channel the sensor connected.
    """
    def __init__(self, channel):
        self.channel = channel
        self.dht = Adafruit_DHT
        self.sensor = Adafruit_DHT.DHT11

    def temperature(self):
        _, temperature = self.dht.read_retry(self.sensor, self.channel)
        return temperature

    def humidity(self):
        humidity, _ = self.dht.read_retry(self.sensor, self.channel)
        return humidity


def main():
    moisture_sensor = GroveMoistureSensor(moisture_pin)
    temp_hum_sensor = GroveHumidityTemperatureSensor(temp_humid_pin)

    print(f"{datetime.now()} - Starting sensors: {', '.join(configured_sensors.keys())}")
    print(moisture_sensor.moisture, temp_hum_sensor.temperature(), temp_hum_sensor.humidity())
    while True:
        moisture_ar = []
        temperature_ar = []
        humid_ar = []
        sensor_interval = 50

        # Loop takes around 11seconds per set of readings
        for _ in range(0, sensor_interval):
            m = moisture_sensor.moisture
            t = temp_hum_sensor.temperature()
            h = temp_hum_sensor.humidity()
            
            # print(f"{m}, {t}, {h}")
            # m = np.random.randint(2000)
            # if 0 <= m and m < 1400:
            #     result = "Wet"
            # elif 1400 <= m and m < 1900:
            #     result = "Moist"
            # else:
            #     result = "Dry"

            moisture_ar.append(m)
            temperature_ar.append(t)
            humid_ar.append(h)

        now = datetime.now()
        
        sensor_readings = []
        sensor_readings.append(moisture_ar)
        sensor_readings.append(temperature_ar)
        sensor_readings.append(humid_ar)

        print("\nCalculating averages:")
        for idx in range(0, len(configured_sensors)):
            sensor_avg = np.median(sensor_readings[idx])
            sensor_name = list(configured_sensors.keys())[idx]
            print(f"{sensor_name.capitalize()} average reading: {sensor_avg}")

            with open(data_path / f"{sensor_name}_log.csv", "a", newline="") as csvfile:
                sensor_writer = csv.writer(
                    csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
                )
                sensor_writer.writerow(
                    [sensor_avg, now.strftime("%Y-%m-%d %H:%M:%S")])


if __name__ == "__main__":
    main()
