import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, timedelta


data_path = Path('data')

def add_data(number: int, chart: st.line_chart, day: int) -> None:
    today = date.today() + timedelta(days=day)

    # add_df = pd.DataFrame.from_dict({"moisture": [number]})
    add_df = pd.DataFrame.from_dict({"moisture": [number], "timestamp": today.strftime("%Y-%m-%d")})
    add_df['timestamp'] = pd.to_datetime(add_df['timestamp'])
    add_df.set_index('timestamp', inplace=True)
    chart.add_rows(add_df['moisture'])

df = pd.read_csv(data_path / "moisture.csv").drop("Unnamed: 0", axis=1)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)
print(df.index)

chart = st.line_chart(df['moisture'])

# chart = st.vega_lite_chart(df, {
#     'mark': 'circle',
#     'encoding': {
#         'x': {
#             'field': 'timestamp', 
#             'type': 'temporal'
#             },
#         'y': {
#             'field': 'moisture', 
#             'type': 'quantitative'
#             },
#     }
# }
# )

add_data(999, chart, 0)
add_data(0, chart, 1)





# today = date.today() + timedelta(days=0)
# add_df = pd.DataFrame.from_dict({"moisture": [813], "timestamp": today.strftime("%Y-%m-%d")})
# add_df['timestamp'] = pd.to_datetime(add_df['timestamp'])
# add_df.set_index('timestamp', inplace=True)
# print(add_df.index)
# print(add_df)

# chart.add_rows(add_df['moisture'])

# today = date.today() + timedelta(days=1)
# add_df2 = pd.DataFrame.from_dict({"moisture": [127], "timestamp": today.strftime("%Y-%m-%d")})
# add_df2['timestamp'] = pd.to_datetime(add_df2['timestamp'])
# add_df2.set_index('timestamp', inplace=True)
# print(add_df2.index)
# print(add_df2)

# chart.add_rows(add_df2['moisture'])


# Check types
# Sanity check with int index