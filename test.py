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

"""

data_path = Path('data')
image_path = Path('images')


def load_latest_data(file_path: Path):
    # Load data from the file used to store historical readings
    df = pd.read_csv(file_path).drop("Unnamed: 0", axis=1)
    # Explicitly casting data column to float breaks chart updating
    # df[df.columns[0]] = df[df.columns[0]].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Using timestamps as an index seems to break add_rows
    # df.set_index('timestamp', inplace=True)
    return df


def store_data(data):
    # Append data to the file used to store historical readings
    pass


def streamlit_init_layout(available_sensors: list, today: date) -> pd.DataFrame:
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

        domain_pd = pd.to_datetime(
            [today - timedelta(days=30), today]).astype(int) / 10 ** 6

        # Plot (Plotly would be preferred but is not supported by the add_rows function)
        chart = st.altair_chart(alt.Chart(init_df).mark_line(point=True).encode(
            x=alt.X('timestamp',
                    # timeunit='yearmonthday',
                    scale=alt.Scale(domain=list(domain_pd))
                    ),
            y=sensor,
            tooltip=[sensor.__str__(), 'timestamp']
        ).interactive(),
            use_container_width=True)

        sensor_dict[sensor] = [frame, chart]

    st.markdown("## All Sensors")
    sensor_dict['all'] = st.empty()

    return sensor_dict


def update_data(sensor_str: str, sensor_val, current_date, sensor_dict: dict):
    add_df = pd.DataFrame.from_dict(
        {
            sensor_str: [sensor_val],
            "timestamp": current_date.strftime("%Y-%m-%d")
        }
    )
    add_df['timestamp'] = pd.to_datetime(add_df['timestamp'])
    # add_df.set_index('timestamp', inplace=True)

    sensor_dict[sensor_str][0].add_rows(add_df)
    sensor_dict[sensor_str][1].add_rows(add_df)
    return add_df


def add_data(sensor_dict: dict, available_sensors: list, today: date):
    fig = px.line()
    for sensor in available_sensors:
        print(f"Updating {sensor}")
        if sensor == 'moisture':

            # Simulate sensor reading
            sensor_val = np.random.randint(0, 1000)

            # Add a row to the dataframe
            added_rows = update_data(
                sensor, sensor_val, today, sensor_dict)

            # Write to file
            # plot_df.to_csv(data_path / f'{sensor}.csv')

            latest_df = load_latest_data(data_path /
                                         f"{sensor}.csv").append(added_rows, ignore_index=True)
            fig.add_scatter(x=latest_df['timestamp'],
                            y=latest_df[sensor], name=sensor)

        elif sensor == 'temperature':
            # Simulate sensor reading
            sensor_val = np.random.randint(0, 5)

            # Add a row to the dataframe
            added_rows = update_data(
                sensor, sensor_val, today, sensor_dict)

            # Write to file
            # plot_df.to_csv(data_path / f'{sensor}.csv')

            latest_df = load_latest_data(data_path /
                                         f"{sensor}.csv").append(added_rows, ignore_index=True)
            fig.add_scatter(x=latest_df['timestamp'],
                            y=latest_df[sensor], name=sensor)

        else:
            print(f'{sensor} not configured with polling logic')
            continue

    # Plot all sensors on a plotly graph
    sensor_dict['all'].plotly_chart(fig)


def main():
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
