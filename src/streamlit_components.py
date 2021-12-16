from datetime import date, datetime

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

from config.config import data_path, image_path, sensor_dry, sensor_wet
from sensor_calculations import (
    calc_metrics,
    convert_cap_to_moisture,
    load_latest_data,
    calc_chart_limits,
)


def add_spacer(spacer_height):
    for _ in range(0, spacer_height):
        st.markdown("#")


def streamlit_init_layout(available_sensors: list, today: date) -> pd.DataFrame:
    """Initialisation of streamlit app"""
    sensor_dict = {}
    st.markdown(
        "<h1 style='text-align: center; color: white;'>Plant Monitoring</h1>",
        unsafe_allow_html=True,
    )
    # Add spacer ###############################################################
    add_spacer(2)

    # Centre the image
    left, mid, right = st.columns([1, 1, 2])
    with mid:
        st.image(Image.open(image_path / "snake.png"), use_column_width=True)
        st.markdown(
            "<h3 style='text-align: center; color: white;'>Malfoy</h3>",
            unsafe_allow_html=True,
        )
    with right:
        # Create a placeholder for sensor readouts
        hero = st.empty()
        hero.markdown(
            "<h2 style='text-align: left; color: white;'>Sensors</h2>",
            unsafe_allow_html=True,
        )

    _, info_mid, _ = st.columns([1, 2, 1])
    with info_mid:
        info = st.empty()
    # Add spacer ###############################################################
    add_spacer(1)

    for sensor in available_sensors:
        # Streamlit expects columns for each sensor
        plot_df = load_latest_data(data_path / f"{sensor}_log.csv")
        if sensor == "moisture":
            plot_df[sensor] = convert_cap_to_moisture(
                plot_df[sensor], sensor_dry, sensor_wet
            )
        sensor_dict = create_sensor_dict(plot_df, sensor, sensor_dict, today)

    st.markdown("## All Sensors")
    sensor_dict["all"] = st.empty()
    return sensor_dict, hero, info


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
