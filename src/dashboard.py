import time
from datetime import date, datetime, timedelta
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

from config.config import configured_sensors, data_path, image_path

# """
# # Data Flow
# 1. Load historical data and default sensor
# 2. Sensors send updated data
# 3. Add data to relevant datframe
# 4. Dynamic update of relevant chart
# 5. Write update to historical file

# # Usage
# This should be configurable based on the plant that is being monitored.

# 1. Detct time since last watering
#     * Some % change in the moisture level
# 2. Estimate time till next watering is required
# 3. Calculate averages over time period
# """


class Sensor:
    def __init__(self, name) -> None:
        self.name = name
        self.df = pd.DataFrame


def load_latest_data(file_path: Path) -> pd.DataFrame:
    # Load data from the file used to store historical readings
    df = pd.read_csv(file_path).drop("Unnamed: 0", axis=1)

    # Explicitly casting data column to float breaks chart updating
    # df[df.columns[0]] = df[df.columns[0]].astype(float)

    # Cast datetime to Timestamp format
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def calc_metrics(sensor_df: pd.DataFrame) -> str:
    last_10 = sensor_df.iloc[-10:].mean(numeric_only=True).values[0]
    last_50 = sensor_df.iloc[-50:].mean(numeric_only=True).values[0]
    all = sensor_df.mean(numeric_only=True).values[0]
    output_df = pd.DataFrame.from_dict(
        {"Last 10 avg.": [last_10], "Last 50 avg.": [last_50], "Alltime avg.": [all]}
    )
    return output_df.to_string(index=False)


def store_data(data):
    # Append data to the file used to store historical readings
    pass


def calc_chart_limits(current_day: datetime) -> list:
    return (
        pd.to_datetime(
            [current_day - timedelta(days=7), current_day + timedelta(days=1)]
        ).astype(int)
        / 10 ** 6
    )


def create_sensor_dict(
    plot_df: pd.DataFrame, sensor: str, sensor_dict: dict, current_day: datetime
) -> dict:
    # Stores objects returned by function
    sensor_dict[sensor] = []

    st.markdown(f"## {sensor.capitalize()}")

    # Calculate metrics from loaded data
    metrics_df = st.empty()
    metrics_df.text(calc_metrics(plot_df))

    # Datframe with historical data
    with st.expander(f"{sensor.capitalize()} dataframe"):
        frame = st.dataframe(plot_df)

    # Set the axis limits dynamically to the last month of data - TODO: Needs to be dynamic with sensor refreshes
    domain_pd = calc_chart_limits(current_day)

    # Plot (Plotly would be preferred but is not supported by the add_rows function)
    with st.expander(f"{sensor.capitalize()} timeseries"):
        chart = st.empty()
        chart.altair_chart(
            alt.Chart(plot_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("timestamp", scale=alt.Scale(domain=list(domain_pd))),
                y=sensor,
                tooltip=[sensor.__str__(), "timestamp"],
            )
            .interactive(),
            use_container_width=True,
        )

    # Assign the ouput streamlit objects to the sensor dict object
    sensor_dict[sensor].append(frame)  # Index 0 - Streamlit df
    sensor_dict[sensor].append(chart)  # Index 1 - Streamlit chart
    sensor_dict[sensor].append(plot_df)  # Index 2 - Initial df
    sensor_dict[sensor].append(metrics_df)  # Index 3 - Metrics df

    return sensor_dict


def streamlit_init_layout(available_sensors: list, today: date) -> pd.DataFrame:
    """Initialisation of streamlit app"""
    sensor_dict = {}
    st.markdown(
        "<h1 style='text-align: center; color: white;'>Plant Monitoring</h1>",
        unsafe_allow_html=True,
    )

    # Centre the image
    _left, mid, _right = st.columns(3)
    with mid:
        st.image(Image.open(image_path / "snake.png"), use_column_width=True)

        # Create a placeholder for sensor readouts
        hero = st.empty()
        hero.markdown(
            "<h1 style='text-align: center; color: white;'>Sensors</h1>",
            unsafe_allow_html=True,
        )

    # Add spacer
    for _ in range(0, 10):
        st.markdown("#")

    for sensor in available_sensors:
        # Streamlit expects columns for each sensor
        plot_df = load_latest_data(data_path / f"{sensor}.csv")
        sensor_dict = create_sensor_dict(plot_df, sensor, sensor_dict, today)

    st.markdown("## All Sensors")
    sensor_dict["all"] = st.empty()
    return sensor_dict, hero


def update_data(
    sensor_str: str, sensor_val: float, current_time: datetime, sensor_dict: dict
) -> pd.DataFrame:
    """Add new data from sensor to the streamlit charts"""
    add_df = pd.DataFrame.from_dict(
        {
            sensor_str: [sensor_val],
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
    )
    print(current_time)
    # Explicitly casting data column to float breaks chart updating
    # add_df[sensor_str] = add_df[sensor_str].astype(float)
    add_df["timestamp"] = pd.to_datetime(add_df["timestamp"])

    # In-place update the sensor's altair dataframe and chart
    sensor_dict[sensor_str][0].add_rows(add_df)  # Index 0 - Streamlit df
    sensor_dict[sensor_str][1].add_rows(add_df)  # Index 1 - Streamlit chart
    return add_df


def add_scatter(
    sensor_dict: dict, sensor: str, added_rows: pd.DataFrame, fig: px.line
) -> px.line:
    # TODO: Should probably be a call to a classes df object
    latest_df = sensor_dict[sensor][2].append(added_rows, ignore_index=True)
    # Add a scatter to the plotly graph objects
    fig.add_scatter(
        x=latest_df["timestamp"],
        y=latest_df[sensor],
        name=sensor,
        marker={"color": configured_sensors[sensor]},
    )
    return fig


def poll_sensors(
    sensor_dict: dict, available_sensors: dict, time_now: datetime
) -> dict:
    # For each of the sensors read the value
    fig = px.line()
    new_vals = []
    for sensor in available_sensors:
        print(f"Updating {sensor}")

        if sensor == "moisture":
            # Simulate sensor reading
            sensor_val = np.random.randint(0, 100)
        elif sensor == "temperature":
            # Simulate sensor reading
            sensor_val = np.random.randint(10, 30)
        else:
            print(f"{sensor} not configured with polling logic")
            continue

        new_vals.append(sensor_val)
        # Add new readings to visualisations
        added_rows = update_data(sensor, sensor_val, time_now, sensor_dict)
        # Add new readings to dataframe
        sensor_dict[sensor][2] = sensor_dict[sensor][2].append(
            added_rows, ignore_index=True
        )

        # Plot data to scatter
        fig = add_scatter(sensor_dict, sensor, added_rows, fig)

        # Add calculated metrics from latest data
        sensor_dict[sensor][3].text(calc_metrics(sensor_dict[sensor][2]))
        # Write to file
        # plot_df.to_csv(data_path / f'{sensor}.csv')

    # Plot all sensors on a plotly graph
    sensor_dict["all"].plotly_chart(fig)

    return sensor_dict, new_vals


def create_hero_string(available_sensors, new_vals):
    str_ar = []
    sensor_list = list(available_sensors)
    for idx in range(0, len(sensor_list)):
        str_ar.append(f"{sensor_list[idx].capitalize()}:<br>{new_vals[idx]}")
    return "\n".join(str_ar)


def monitor_plants(curr_time: datetime):
    print(f"\nCurrent Time is {curr_time}")
    # Define the sensors and current time
    available_sensors = configured_sensors.keys()
    # Initialise from saved data
    sensor_dict, hero = streamlit_init_layout(available_sensors, curr_time)

    # Recieve new data
    while True:
        time_now = datetime.now()
        updated_readings, new_vals = poll_sensors(
            sensor_dict, available_sensors, time_now
        )
        time.sleep(5)
        hero_string = create_hero_string(available_sensors, new_vals)
        hero.markdown(
            f"<h1 style='text-align: center; color: White;'>{hero_string}</h1>",
            unsafe_allow_html=True,
        )

        # print((time_now - curr_time) < timedelta(days=1))

        # if (time_now - curr_time) < timedelta(days=1):
        #     # Update the start date
        #     print("Updating chart lims")

        #     curr_time = time_now + timedelta(days=1)
        #     # Updated the chart axes
        #     new_lims = calc_chart_limits(curr_time)

        #     # for sensor in [key for key in sensor_dict][:-1]:
        #     #     plot_df = load_latest_data(data_path / f"{sensor}.csv")
        #     #     chart = st.empty()
        #     #     chart.altair_chart(
        #     #         alt.Chart(plot_df)
        #     #         .mark_line(point=True)
        #     #         .encode(
        #     #             x=alt.X("timestamp", scale=alt.Scale(domain=list(new_lims))),
        #     #             y=sensor,
        #     #             tooltip=[sensor.__str__(), "timestamp"],
        #     #         )
        #     #         .interactive(),
        #     #         use_container_width=True,
        #     #     )

        # # st.altair_chart(alt.Chart(load_latest_data(data_path / f"moisture.csv")))

        # # This really should work, not sure why it doesn't
        # for sensor in sensor_dict:
        #     updated_readings[sensor][1].altair_chart(
        #         alt.Chart(load_latest_data(data_path / f"{sensor}.csv"))
        #         .mark_line(point=True)
        #         .encode(
        #             x=alt.X(
        #                 "timestamp",
        #                 scale=alt.Scale(
        #                     # domain=list([1635766338263.342, 1635966338263.342])
        #                     domain=list(new_lims)
        #                 ),
        #             ),
        #             y=sensor,
        #             tooltip=[sensor.__str__(), "timestamp"],
        #         )
        #         .interactive(),
        #         use_container_width=True,
        #     )


def main() -> None:
    time_start = datetime.now()
    monitor_plants(time_start)


if __name__ == "__main__":
    main()
