from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.interpolate.interpolate import interp1d
from statsmodels.tsa.ar_model import AutoReg

from config import (
    configured_sensors,
    data_path,
    sensor_dry,
    sensor_wet,
    target_water_moisture,
)


def update_data(
    sensor_str: str, sensor_val: float, current_time: datetime, sensor_dict: dict
) -> pd.DataFrame:
    """Add new data from sensor to the streamlit charts"""
    add_df = pd.DataFrame.from_dict(
        {
            sensor_str: [sensor_val],
            "timestamp": pd.to_datetime(str(current_time)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
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


def load_latest_data(file_path: Path) -> pd.DataFrame:
    # Load data from the file used to store historical readings
    df = pd.read_csv(file_path).drop_duplicates().reset_index(drop=True)

    # Explicitly casting data column to float breaks chart updating
    # df[df.columns[0]] = df[df.columns[0]].astype(float)

    # Cast datetime to Timestamp format
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def load_latest_reading(sensor: str) -> float:
    sensor_file = data_path / f"{sensor}_log.csv"
    last_val = pd.read_csv(sensor_file).tail(1)
    last_val["timestamp"] = pd.to_datetime(last_val["timestamp"])
    return last_val


def calc_metrics(sensor_df: pd.DataFrame) -> str:
    last_10 = sensor_df.iloc[-10:].mean(numeric_only=True).values[0]
    last_50 = sensor_df.iloc[-50:].mean(numeric_only=True).values[0]
    all = sensor_df.mean(numeric_only=True).values[0]
    output_df = pd.DataFrame.from_dict(
        {"Last 10 avg.": [last_10], "Last 50 avg.": [last_50], "Charted avg.": [all]}
    )
    return output_df.to_string(index=False)


def convert_cap_to_moisture(
    reading: float, dry_val: int = sensor_dry, wet_val: int = sensor_wet
):
    return interp1d([dry_val, wet_val], [0, 100], fill_value="extrapolate")(reading)


def poll_sensors(sensor_dict: dict, available_sensors: dict) -> dict:
    # For each of the sensors read the value
    fig = px.line()
    new_vals = []
    for sensor in available_sensors:
        print(f"Updating {sensor}")

        if sensor == "moisture":
            last_reading = load_latest_reading(sensor)
            sensor_val = convert_cap_to_moisture(
                last_reading[sensor].values[0]
            ).flatten()[0]
        elif sensor == "temperature":
            last_reading = load_latest_reading(sensor)
            sensor_val = last_reading[sensor].values[0]
        elif sensor == "humidity":
            last_reading = load_latest_reading(sensor)
            sensor_val = last_reading[sensor].values[0]
        else:
            print(f"{sensor} not configured with polling logic")
            continue

        try:
            sensor_time = last_reading["timestamp"].values[0]
        except ValueError as e:
            print(e)
            print(last_reading["timestamp"].values[0])
            sensor_time = sensor_dict[sensor][2].iloc[-1]["timestamp"]

        new_vals.append(sensor_val)
        # Add new readings to visualisations
        added_rows = update_data(sensor, sensor_val, sensor_time, sensor_dict)
        # Add new readings to dataframe
        sensor_dict[sensor][2] = sensor_dict[sensor][2].append(
            added_rows, ignore_index=True
        )
        # Limit sensor dict to ~1 week of data
        sensor_dict[sensor][2] = sensor_dict[sensor][2].iloc[-2500:]

        # Plot data to scatter
        fig = add_scatter(sensor_dict, sensor, added_rows, fig)

        # Add calculated metrics from latest data
        sensor_dict[sensor][3].text(calc_metrics(sensor_dict[sensor][2]))
        # Write to file
        # plot_df.to_csv(data_path / f'{sensor}.csv')

    # Plot all sensors on a plotly graph
    sensor_dict["all"].plotly_chart(fig)

    return sensor_dict, new_vals, sensor_time


def calc_chart_limits(current_day: datetime) -> list:
    return (
        pd.to_datetime(
            [current_day - timedelta(days=7), current_day + timedelta(days=1)]
        ).astype(int)
        / 10 ** 6
    )


def calc_cycle(last_watered: datetime) -> Tuple[pd.DataFrame, datetime]:
    moisture_df = load_latest_data(data_path / f"moisture_log.csv")
    moisture_df["moisture"] = convert_cap_to_moisture(
        moisture_df["moisture"], sensor_dry, sensor_wet
    )
    # Only check rows after the last event
    if last_watered is not None:
        cycle_df = moisture_df[moisture_df["timestamp"] > last_watered].copy(deep=True)
        return cycle_df, last_watered
    else:
        # Last watering event is unknown we need to check the historical record to filter
        calc_df = moisture_df.copy(deep=True)
        calc_df["diff"] = calc_df["moisture"] - calc_df.shift(1)["moisture"]
        # Return last event if it has occured
        watered_df = calc_df[calc_df["diff"] > 10]
        # If no watering events return the full historical data
        if len(watered_df) == 0:
            return moisture_df, None
        # Return the dateframe after the last identified watering
        watered_date = watered_df["timestamp"].iloc[-1].strftime("%Y-%m-%d")
        cycle_df = calc_df[calc_df["timestamp"] > watered_date].copy(deep=True)
        return cycle_df, watered_date


def determine_last_watered(last_watered: datetime) -> datetime:
    cycle_df, last_watered = calc_cycle(last_watered)
    # Calculate difference
    cycle_df["diff"] = cycle_df["moisture"] - cycle_df.shift(1)["moisture"]
    # Return last event if it has occured
    watered_df = cycle_df[cycle_df["diff"] > 10]["timestamp"]
    if len(watered_df) == 0:
        return last_watered
    return watered_df.iloc[-1].strftime("%Y-%m-%d")


def determine_next_water(last_watered: datetime) -> Tuple[datetime, datetime]:
    print("\n\nPredicting next watering\n\n")
    # Filter the df from the last point it was watered
    cycle_df, last_watered = calc_cycle(last_watered)
    cycle_df["diff"] = cycle_df["moisture"] - cycle_df.shift(1)["moisture"]
    X = cycle_df["moisture"].values
    # If the current reading is below the target moisture
    if X[-1] < target_water_moisture:
        return "Now!", last_watered
    # Possibly implement different windows of training based on watering cycles
    try:
        # Lag with 2 days of data
        model = AutoReg(X, lags=500, old_names=False)
        model_fit = model.fit()
        # Predict 1 week in advanced and return index of values below threshold
        water_idx = np.argmax(model_fit.forecast(steps=2000) < target_water_moisture)
        if water_idx == 0:
            return "Not in the next week", last_watered
        else:
            # TODO: Estimate average time between readings for the last day and use that as the multiplier
            return (
                f"On {(datetime.now() + timedelta(minutes=5*int(water_idx))).strftime('%Y-%m-%d')}",
                last_watered,
            )
    except ValueError as e:
        return "Insufficient time since watering", last_watered
