# This is a message to hold the flight modes. 
# Make sure to update it when a new flight mode is added to the system!

uint8 FLIGHT_MODE_UNKNOWN = 0
uint8 FLIGHT_MODE_ATTI = 1
uint8 FLIGHT_MODE_ATTI_MAN = 2
uint8 FLIGHT_MODE_SPORT = 3
uint8 FLIGHT_MODE_SPORT_MAN = 4
uint8 FLIGHT_MODE_ASSIST = 5
uint8 FLIGHT_MODE_FORCED_ATTI = 6
uint8 FLIGHT_MODE_EMERGENCY_ASSIST = 7
uint8 FLIGHT_MODE_EMERGENCY_ATTI = 8
uint8 FLIGHT_MODE_ASSIST_LVIO = 9
uint8 FLIGHT_MODE_ASSIST_SPORT = 10
uint8 FLIGHT_MODE_ASSIST_SPORT_LVIO = 11
uint8 FLIGHT_MODE_AUTONOMOUS = 12
uint8 FLIGHT_MODE_EMERGENCY_MAN = 13

std_msgs/Header header
uint8  flight_mode
uint8  desired_flight_mode
