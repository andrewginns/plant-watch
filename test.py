import time
from datetime import date, timedelta
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

"""
# Data Flow
1. Load historical data and default sensor
2. Sensors send updated data
3. Add data to relevant datframe
4. Dynamic update of relevant chart
5. Write update to historical file

# Usage
This should be configurable based on the plant that is being monitored.

1. Detct time since last watering
    * Some % change in the moisture level
2. Estimate time till next watering is required
3. Calculate averages over time period
"""

data_path = Path('data')
image_path = Path('images')


class Sensor():

    def __init__(self) -> None:
        pass
    pass


def load_latest_data(file_path: Path) -> pd.DataFrame:
    # Load data from the file used to store historical readings
    df = pd.read_csv(file_path).drop("Unnamed: 0", axis=1)

    # Explicitly casting data column to float breaks chart updating
    # df[df.columns[0]] = df[df.columns[0]].astype(float)

    # Cast datetime to Timestamp format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df


def store_data(data):
    # Append data to the file used to store historical readings
    pass


def streamlit_init_layout(available_sensors: list, today: date) -> pd.DataFrame:
    """Initialisation of streamlit app"""
    st.title("Plant Monitoring")
    st.image(Image.open(image_path / 'succulent.png'), width=200)
    # column = st.selectbox("Sensor to plot", available_sensors)

    sensor_dict = {}
    for sensor in available_sensors:
        # Streamlit expects columns for each sensor
        init_df = load_latest_data(data_path / f"{sensor}.csv")

        st.markdown(f"## {sensor.capitalize()}")
        with st.expander(f"{sensor.capitalize()} dataframe"):
            frame = st.dataframe(init_df)

        # Set the axis limits dynamically to the last month of data
        domain_pd = pd.to_datetime(
            [today - timedelta(days=30), today]).astype(int) / 10 ** 6

        # Plot (Plotly would be preferred but is not supported by the add_rows function)
        chart = st.altair_chart(alt.Chart(init_df).mark_line(point=True).encode(
            x=alt.X('timestamp',
                    scale=alt.Scale(domain=list(domain_pd))
                    ),
            y=sensor,
            tooltip=[sensor.__str__(), 'timestamp']
        ).interactive(),
            use_container_width=True)

        # Assign the ouput streamlit widgets to the dict object
        sensor_dict[sensor] = [frame, chart]

    st.markdown("## All Sensors")
    sensor_dict['all'] = st.empty()

    return sensor_dict


def update_data(sensor_str: str, sensor_val, current_date, sensor_dict: dict) -> pd.DataFrame:
    add_df = pd.DataFrame.from_dict(
        {
            sensor_str: [sensor_val],
            "timestamp": current_date.strftime("%Y-%m-%d")
        }
    )
    add_df['timestamp'] = pd.to_datetime(add_df['timestamp'])
    # add_df.set_index('timestamp', inplace=True)

    # In-place update the sensor's altair dataframe and chart
    sensor_dict[sensor_str][0].add_rows(add_df)
    sensor_dict[sensor_str][1].add_rows(add_df)
    return add_df


def add_scatter(sensor: str, added_rows: pd.DataFrame, fig: px.line):
    # TODO: Should probably be a call to a classes df object
    latest_df = load_latest_data(data_path /
                                 f"{sensor}.csv").append(added_rows, ignore_index=True)
    # Add a scatter to the plotly graph objects
    fig.add_scatter(x=latest_df['timestamp'],
                    y=latest_df[sensor],
                    name=sensor)
    return fig


def add_data(sensor_dict: dict, available_sensors: list, today: date) -> None:
    fig = px.line()
    for sensor in available_sensors:
        print(f"Updating {sensor}")
        if sensor == 'moisture':
            # Simulate sensor reading
            sensor_val = np.random.randint(0, 100)

            # Add a row to the dataframe
            added_rows = update_data(
                sensor, sensor_val, today, sensor_dict)

            fig = add_scatter(sensor, added_rows, fig)
            # Write to file
            # plot_df.to_csv(data_path / f'{sensor}.csv')

        elif sensor == 'temperature':
            # Simulate sensor reading
            sensor_val = np.random.randint(10, 30)

            # Add a row to the dataframe
            added_rows = update_data(
                sensor, sensor_val, today, sensor_dict)

            fig = add_scatter(sensor, added_rows, fig)
            # Write to file
            # plot_df.to_csv(data_path / f'{sensor}.csv')

        else:
            print(f'{sensor} not configured with polling logic')
            continue

    # Plot all sensors on a plotly graph
    sensor_dict['all'].plotly_chart(fig)


def calc_metrics(df: pd.DataFrame) -> None:
    pass


def main() -> None:
    # Define the current date and sensors
    today = date.today()
    available_sensors = ['moisture', 'temperature']
    sensor_dict = streamlit_init_layout(available_sensors, today)

    for _ in range(0, 5):
        # Simulate sensor polling - every x seconds receive data from sensors
        add_data(sensor_dict, available_sensors, today)
        today += timedelta(days=1)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
