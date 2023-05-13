import time
from datetime import datetime

from config import (configured_sensors, dashboard_update,
                    homeassistant_integration, prediction_update)
from sensor_calculations import (determine_last_watered, determine_next_water,
                                 poll_sensors)
from streamlit_components import streamlit_init_layout

if homeassistant_integration:
    import json

    import paho.mqtt.client as mqtt

    from config import (clientname, hass_password, hass_username, hostname,
                        mqtt_topic_root, port, timeout)


def create_hero_string(available_sensors: list, new_vals: list, sensor_time: datetime) -> str:
    """
    This function creates a string that can be used to display the sensor readings in the hero section of the dashboard.

    Args:
        available_sensors: A list of the names of the available sensors.
        new_vals: A list of the new sensor readings.
        sensor_time: The current time.

    Returns:
        A string that can be used to display the sensor readings in the hero section of the dashboard.
    """
    str_ar = []
    sensor_list = list(available_sensors)
    for idx in range(0, len(sensor_list)):
        str_ar.append(
            "".join(
                [
                    f"<h6>{sensor_list[idx].capitalize()}:</h6>",
                    f"{new_vals[idx]:.2f}",
                    "<h6></h6>",
                ]
            )
        )
    str_ar.append(f"<p>{str(sensor_time).split('T')[-1][:8]}</p>")
    return "".join(str_ar)


def create_info_string(last_watered: datetime, next_water: datetime) -> str:
    """
    This function creates a string that can be used to display the last watered and next water dates in the info section of the dashboard.

    Args:
        last_watered: The last time the plants were watered.
        next_water: The next time the plants should be watered.

    Returns:
        A string that can be used to display the last watered and next water dates in the info section of the dashboard.
    """
    s1 = f"<h6 style='margin-left: 1em'>Last watered: {last_watered}</h6>"
    s2 = f"<h6 style='margin-left: 1em'>Water next: {next_water}</h6>"
    return "".join([s1, s2])


def monitor_plants(curr_time: datetime) -> None:
    """
    This function monitors the plants and updates the dashboard with the latest sensor readings.

    Args:
        curr_time: The current time.
    """
    if homeassistant_integration:
        client = mqtt.Client(clientname)
        client.username_pw_set(hass_username, hass_password)
        client.connect(hostname, port, timeout)

        client.loop_start()

    print(f"\nCurrent Time is {curr_time}")
    # Define the sensors and current time
    available_sensors = configured_sensors.keys()
    # Initialise from saved data
    sensor_dict, hero, info = streamlit_init_layout(available_sensors, curr_time)
    # Initialise variables
    last_watered = None

    # Recieve new data
    while True:
        # Run predictions
        last_watered = determine_last_watered(last_watered)
        next_water, last_watered = determine_next_water(last_watered)

        if homeassistant_integration:
            data = {f"water_next": str(next_water)}
            client.publish(mqtt_topic_root + "water_next", json.dumps(data))
            print(f"Published {data} to {mqtt_topic_root + 'water_next'} on MQTT")
    
            data = {f"water_last": str(last_watered)}
            client.publish(mqtt_topic_root + "water_last", json.dumps(data))
            print(f"Published {data} to {mqtt_topic_root + 'water_last'} on MQTT")

        # Add information readouts
        info_string = create_info_string(last_watered, next_water)
        info.markdown(info_string, unsafe_allow_html=True)

        # Update sensors
        for _ in range(0, prediction_update):
            # time_now = datetime.now()
            updated_sensor_dict, new_vals, sensor_time = poll_sensors(
                sensor_dict, available_sensors
            )
            # Update the 'hero' sensor readouts
            hero_string = create_hero_string(available_sensors, new_vals, sensor_time)
            hero.markdown(
                f"<h2 style='text-align: left; color: White;'>{hero_string}</h2>",
                unsafe_allow_html=True,
            )

            time.sleep(dashboard_update)


def main() -> None:
    time_start = datetime.now()
    monitor_plants(time_start)


if __name__ == "__main__":
    main()
