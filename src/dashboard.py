import time
from datetime import datetime

from config.config import configured_sensors, dashboard_update
from sensor_calculations import poll_sensors
from streamlit_components import streamlit_init_layout


def create_hero_string(
    available_sensors: list, new_vals: list, sensor_time: datetime
) -> str:
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
    str_ar.append(f"<p>{str(sensor_time)[-9:]}</p>")
    return "".join(str_ar)


def monitor_plants(curr_time: datetime):
    print(f"\nCurrent Time is {curr_time}")
    # Define the sensors and current time
    available_sensors = configured_sensors.keys()
    # Initialise from saved data
    sensor_dict, hero = streamlit_init_layout(available_sensors, curr_time)

    # Recieve new data
    while True:
        # time_now = datetime.now()
        updated_readings, new_vals, sensor_time = poll_sensors(
            sensor_dict, available_sensors
        )
        time.sleep(dashboard_update)
        hero_string = create_hero_string(available_sensors, new_vals, sensor_time)
        hero.markdown(
            f"<h2 style='text-align: left; color: White;'>{hero_string}</h2>",
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
