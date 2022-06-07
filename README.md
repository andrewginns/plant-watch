# Plant Watch
A client and server python application to enable monitoring of plants through a raspberry pi-powered sensor suite.

UI is powered through Streamlit hosted on the local network on port 8501.

![UI Hero](/images/ui_hero.png)

## Hardware
* Raspberry Pi 3B+ running Raspbian OS Lite on Debian Bullseye
* [Grove Base HAT for Raspberry Pi Zero](https://thepihut.com/products/grove-base-hat-for-raspberry-pi-zero)
    * [Grove DHT11 Temperature and Humidity Sensor](https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/)
    * [Grove Capacitive Moisture Sensor](https://wiki.seeedstudio.com/Grove-Capacitive_Moisture_Sensor-Corrosion-Resistant/)

## QuickStart
tba

## Data Flow
1. Load historical data for configured sensors
2. Display most up to date data
3. Dynamic update of relavant tables
4. Dynamic update of relevant chart
## Features
1. Detct time since last watering
    * Some % change in the moisture level
2. Estimate time till next watering is required
    * Some threshold % of moisture
3. Display most up to date information from sensors