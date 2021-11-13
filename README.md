# Plant Watch
## Data Flow
1. Load historical data for configured sensors
2. Read log files for the most up to date data
3. Dynamic update of relavant tables
4. Dynamic update of relevant chart
## Usage
This should be configurable based on the plant that is being monitored.
1. Detct time since last watering
    * Some % change in the moisture level
2. Estimate time till next watering is required
3. Calculate averages over time period