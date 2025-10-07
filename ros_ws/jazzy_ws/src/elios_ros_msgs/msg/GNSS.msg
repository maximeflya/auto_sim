# GNSS data message combining position, velocity and their respective covariance matrices

uint8 STATUS_NO_VALID_FIX = 0 # unable to fix position
uint8 STATUS_VALID_2D_FIX = 1 # altitude is invalid
uint8 STATUS_VALID_3D_FIX = 2 # all data are valid

std_msgs/Header header
uint8 status
float64 lat                     # Latitude [deg] in the WGS84 ellipsoid
float64 lon                     # Longitude [deg] in the WGS84 ellipsoid
float32 altitude                # Height above ellipsoid [m]
float32[9] position_covariance  # Covariance matrix for the position in NED frame [m^2]
bool is_pos_cov_valid           # Boolean flag indicating if the covariance matrix is valid
geometry_msgs/Vector3 vel_ned   # Velocity in NED frame [m/s]
float32[9] velocity_covariance  # Covariance matrix for the velocity in NED frame [m^2/s^2]
bool is_vel_cov_valid           # Boolean flag indicating if the covariance matrix is valid
uint8 n_sat                     # Number of satellites
float32 pdop                    # Position dilution of precision
