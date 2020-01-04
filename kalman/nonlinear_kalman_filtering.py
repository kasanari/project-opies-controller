import numpy as np
from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints, ExtendedKalmanFilter
from kalman.EstimatedState import EstimatedState
from kalman.kalman_filtering import float_with_2_decimals
from serial_with_dwm.location_data_handler import LocationData
from arduino_interface.imu import IMUData


def init_extended_kf(loc_data, dt, variance_angular_acc, variance_pos, variance_acc, variance_heading,
                     var_process_acc, var_process_v, var_process_xy):
    ekf = ExtendedKalmanFilter(5, 5, 0)
    ekf.x = np.array([[loc_data.x], [loc_data.y], [0.0], [0.0], [0.0]])
    ekf.F = set_F(ekf.x, dt)
    ekf.P *= 5
    ekf.R = set_R(variance_pos, variance_acc, variance_heading)
    ekf.Q = set_Q(dt, var_ang_acc=variance_angular_acc, var_process_a=var_process_acc,
                  var_process_v=var_process_v, var_process_x=var_process_xy,
                  var_process_y=var_process_xy)
    print(ekf.R)
    print(ekf.Q)

    return ekf


def init_unscented_kf(loc_data, dt, variance_angular_acc, variance_pos,
                      variance_acc, variance_heading):
    points = MerweScaledSigmaPoints(n=5, alpha=.1, beta=2., kappa=-2)
    ukf = UnscentedKalmanFilter(dim_x=5, dim_z=5, dt=dt, hx=hx, fx=fx, points=points)
    ukf.x = np.array([[loc_data.x], [loc_data.y], [0.0], [0.0], [0.0]])
    ukf.P *= 1
    ukf.R = set_R(variance_pos, variance_acc, variance_heading)

    return ukf


def set_F(x, dt):
    cos_heading = np.cos(x[4, 0])
    sin_heading = np.sin(x[4, 0])
    f = np.array([[1., 0., dt*cos_heading, 0.5*dt*dt*cos_heading, -1*sin_heading*(dt*x[2, 0]+0.5*dt*dt*x[3, 0])],
                  [0., 1., dt*sin_heading, 0.5*dt*dt*sin_heading, cos_heading*(dt*x[2, 0]+0.5*dt*dt*x[3, 0])],
                  [0., 0., 1., dt, 0.],
                  [0., 0., 0., 1., 0.],
                  [0., 0., 0., 0., 1.]]
                 )
    return f


def set_Q(dt, var_process_x, var_process_y, var_process_v, var_process_a,
          var_ang_acc):
    q = np.array([[var_process_x, 0., 0., 0., 0.],
                  [0., var_process_y, 0., 0., 0.],
                  [0., 0., var_process_v, 0., 0.],
                  [0., 0., 0., var_process_a, 0.],
                  [0., 0., 0., 0., var_ang_acc],
                  ])
    return q


def HJacobian_of(x):
    jacobian = np.array([[1., 0., 0., 0., 0.],
                  [0., 1., 0., 0., 0.],
                  [0., 0., 0., np.cos(x[4, 0]), -1*x[3, 0]*np.sin(x[4, 0])],
                  [0., 0., 0., np.sin(x[4, 0]), x[3, 0]*np.cos(x[4, 0])],
                  [0., 0., 0., 0., 1.]])
    return jacobian


def fx(x, dt):
    x_out = np.empty_like(x)
    cos_heading = np.cos(x[4, 0])
    sin_heading = np.sin(x[4, 0])

    x_out[0, 0] = x[0, 0] + dt * x[2, 0] * cos_heading + 0.5 * dt * dt * x[3, 0] * cos_heading  # x_(k+1)
    x_out[1, 0] = x[1, 0] + dt * x[2, 0] * sin_heading + 0.5 * dt * dt * x[3, 0] * sin_heading  # y_(k+1)
    x_out[2, 0] = x[2, 0] + dt * x[3, 0]  # v_(k+1)
    x_out[3, 0] = x[3, 0]  # a_(k+1)
    x_out[4, 0] = x[4, 0]  # theta_(k+1)  [theta = heading]
    return x_out


def hx(x):
    z_out = np.zeros([5, 1])
    z_out[0, 0] = x[0, 0]
    z_out[1, 0] = x[1, 0]
    z_out[2, 0] = x[3, 0] * np.cos(x[4, 0])
    z_out[3, 0] = x[3, 0] * np.sin(x[4, 0])
    z_out[4, 0] = x[4, 0]
    return z_out


def set_R(variance_pos, variance_acc, variance_heading):
    r = np.zeros((5, 5))
    r[0, 0] = variance_pos  # var x
    r[1, 1] = variance_pos  # var y
    r[2, 2] = variance_acc  # var acc_x
    r[3, 3] = variance_acc  # var acc_y
    r[4, 4] = variance_heading  # var theta
    return r


def z_update(loc_data: LocationData, imu_data: IMUData):
    z = [[loc_data.x],
         [loc_data.y],
         [imu_data.world_acceleration.x],
         [imu_data.world_acceleration.y],
         [imu_data.rotation.yaw]]
    return z

def residual(a, b):
    y = a - b
    return y

# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def u_kalman_updates(ukf, loc_data: LocationData, imu_data: IMUData, variance_position, variance_acceleration,
                   variance_heading):
    # kf.F =
    # kf.Q =
    if loc_data is not None:
        z = z_update(loc_data, imu_data)
        ukf.R = set_R(variance_position, variance_acceleration, variance_heading)
        loc_quality = loc_data.quality
    else:
        z = ukf.z
        ukf.R = set_R(500, 500, 500)  # High value, prefer process model
        loc_quality = -99

    ukf.predict()
    ukf.update(z)

    # Values for estimated state as floats, showing two decimals
    x_ukf = float_with_2_decimals(ukf.x[0])
    y_ukf = float_with_2_decimals(ukf.x[1])
    velocity = float_with_2_decimals(ukf.x[2])
    acceleration = float_with_2_decimals(ukf.x[3])
    log_likelihood = float_with_2_decimals(ukf.log_likelihood)
    likelihood = float_with_2_decimals(ukf.likelihood)
    heading = float_with_2_decimals(ukf.x[4])

    filtered_loc = LocationData(x=x_ukf, y=y_ukf, z=0, quality=loc_quality)
    estimated_state = EstimatedState(filtered_loc, v_est=velocity, a_est=acceleration,
                                     log_likelihood=log_likelihood, likelihood=likelihood,
                                     heading_est=heading)

    return estimated_state


# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def e_kalman_updates(ekf, loc_data: LocationData, imu_data: IMUData, variance_position, variance_acceleration,
                   variance_heading, dt, variance_angular_acc, var_process_v,
                                   var_process_acc, var_process_xy):
    #ekf.F = set_F(ekf.x, dt)
    #ekf.Q = set_Q(dt, var_process_v=var_process_v, var_ang_acc=variance_angular_acc,
    #              var_process_x=var_process_xy, var_process_y=var_process_xy,
    #              var_process_a=var_process_acc)

    if loc_data is not None:
        z = z_update(loc_data, imu_data)
        ekf.R = set_R(variance_position, variance_acceleration, variance_heading)
        loc_quality = loc_data.quality
    else:
        z = ekf.z
        print("No value from tag")
        ekf.R = set_R(500, 500, 500)  # High value, prefer process model
        loc_quality = -99

    ekf.predict()
    #predict_with_control(ekf)
    ekf.update(z, HJacobian=HJacobian_of, Hx=hx, residual=residual)  # ,residual=residual)
    # Values for estimated state as floats, showing two decimals
    x_ekf = float_with_2_decimals(ekf.x[0, 0])
    y_ekf = float_with_2_decimals(ekf.x[1, 0])
    velocity = float_with_2_decimals(ekf.x[2, 0])
    acceleration = float_with_2_decimals(ekf.x[3, 0])
    log_likelihood = float_with_2_decimals(ekf.log_likelihood)
    likelihood = float_with_2_decimals(ekf.likelihood)
    heading = float_with_2_decimals(ekf.x[4, 0])

    filtered_loc = LocationData(x=x_ekf, y=y_ekf, z=0, quality=loc_quality)
    estimated_state = EstimatedState(filtered_loc, v_est=velocity, a_est=acceleration,
                                     log_likelihood=log_likelihood, likelihood=likelihood,
                                     heading_est=heading)

    return estimated_state
