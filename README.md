# Plant Watch
A client and server python application to enable monitoring of plants through a raspberry pi-powered sensor suite.

UI is powered through Streamlit hosted on the local network on port 8501.

![UI Hero](/images/ui_hero.jpg)

## Hardware
* Raspberry Pi (tested on a 3B+ running Raspbian OS Lite on Debian Bullseye)
* [Grove Base HAT for Raspberry Pi Zero](https://thepihut.com/products/grove-base-hat-for-raspberry-pi-zero)
    * [Grove DHT11 Temperature and Humidity Sensor](https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/)
        * Plugged into port labelled A0
    * [Grove Capacitive Moisture Sensor](https://wiki.seeedstudio.com/Grove-Capacitive_Moisture_Sensor-Corrosion-Resistant/)
        * Plugged into port labelled PWM

## Pre-requisites
1. Raspberry Pi (server) with Python installed and additional hardware attached
    * SMB share configured to enable file sharing over a network
2.  Secondary machine (client) with Anaconda installed and an env created from the [environment file](environment/plant_watch.yml)

n.b. It may be possible to run both server and client code on a single device such as a Raspberry Pi 4.
## QuickStart
1. Clone this repository to both the server and client machines
2. On the server start [`plant_log.py`](src/plant_log.py)
    * This start the sensor logging
3. On the client start [`plant_watch.py`](src/plant_watch.py)
    * This starts the streamlit UI on http://localhost:8501

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