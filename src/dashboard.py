import time
from datetime import datetime

from config.config import configured_sensors, dashboard_update, prediction_update
from sensor_calculations import (
    determine_last_watered,
    determine_next_water,
    poll_sensors,
)
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


def create_info_string(last_watered: datetime, next_water: datetime):
    s1 = f"<h6 style='margin-left: 1em'>Last watered: {last_watered}</h6>"
    s2 = f"<h6 style='margin-left: 1em'>Water next: {next_water}</h6>"
    return "".join([s1, s2])


def monitor_plants(curr_time: datetime):
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

        info_string = create_info_string(last_watered, next_water)
        info.markdown(info_string, unsafe_allow_html=True)

        # Update senso
        for _ in range(0, prediction_update):
            # time_now = datetime.now()
            updated_sensor_dict, new_vals, sensor_time = poll_sensors(
                sensor_dict, available_sensors
            )
            hero_string = create_hero_string(available_sensors, new_vals, sensor_time)
            hero.markdown(
                f"<h2 style='text-align: left; color: White;'>{hero_string}</h2>",
                unsafe_allow_html=True,
            )

            time.sleep(dashboard_update)


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
