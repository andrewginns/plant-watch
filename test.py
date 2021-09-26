import time
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import date, timedelta

"""
## Data Flow
1. Load historical data and default sensor
2. Sensors send updated data
3. Add data to relevant datframe
4. Dynamic update of relevant chart
5. Write update to historical file

"""

data_path = Path('data')
image_path = Path('images')

def sensor_demo():
    return np.random.randint(0, 1000)

def load_latest_data(file_path: Path):
    # Load data from the file used to store historical readings
    df = pd.read_csv(file_path).drop("Unnamed: 0", axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Using timestamps as an index seems to break add_rows
    # df.set_index('timestamp', inplace=True)
    return df

def store_data(data):
    # Append data to the file used to store historical readings
    pass

def streamlit_init_layout(available_sensors: list) -> pd.DataFrame:
    st.title("Plant Monitoring")
    st.image(Image.open(image_path / 'succulent.png'), width=200)
    column = st.selectbox("Sensor to plot", available_sensors)
    
    # Streamlit expects columns for each sensor
    init_df = load_latest_data(data_path / f"{column}.csv")
    frame = st.dataframe(init_df)
    
    # Plot
    st.text(f"Plot of {column}")
    chart = st.line_chart(init_df[column])

    return frame, chart

def update_data(sensor_str: str, sensor_val, current_date, frame, chart):
    add_df = pd.DataFrame.from_dict({sensor_str: [sensor_val], "timestamp": current_date.strftime("%Y-%m-%d")})
    add_df['timestamp'] = pd.to_datetime(add_df['timestamp'])
    # add_df.set_index('timestamp', inplace=True)

    frame.add_rows(add_df)
    chart.add_rows(add_df[sensor_str])

def add_data(frame, chart, available_sensors):
    today = date.today() - timedelta(days=1)

    # Simulate sensor polling - every x seconds receive data from sensors
    for _ in range(0, 5):
        print("\n\n STEP")
        today += timedelta(days=1)
        sensor_val = np.random.randint(0, 1000)
        
        # Add a row to the dataframe
        update_data('moisture', sensor_val, today, frame, chart)
        
        # plot_df.to_csv(data_path / 'moisture.csv')
        time.sleep(0.1)


def main():
    available_sensors = ['moisture', 'temperature']
    frame, chart = streamlit_init_layout(available_sensors)
    # add_data(frame, chart, available_sensors)
    
    # if 'key' not in st.session_state:
    #     st.session_state['key'] = 'test2'
    # st.write(st.session_state.key)
    
if __name__ == "__main__":
    main()
