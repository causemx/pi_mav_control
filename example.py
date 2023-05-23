from pymavlink import mavutil


class ControlError(Exception):
    pass


if __name__ == "__main__":
    master = mavutil.mavlink_connection('udpin:{}:{}'.format("127.0.0.1", 14550))
    master.wait_heartbeat()

    
    master.mav.set_mode_send(master.target_system, \
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 17)
    
    # Change global location 
    """loc = master.location()
    master.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(
        10, 
        master.target_system, master.target_component, 
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
        int(0b110111111000),
        int(loc.lat*1e7)-5000,
        int(loc.lng*1e7),
        10, 
        0, 0, 0,
        0, 0, 0,
        1.57, 0.5
        ))"""
