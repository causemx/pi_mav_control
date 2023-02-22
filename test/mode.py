from pymavlink import mavutil
from threading import Thread
import time

MODE = ""

def get_mode(master):
    while True:
        msg = master.recv_match(type = 'HEARTBEAT', blocking = False)
        if msg:
            MODE = mode = mavutil.mode_string_v10(msg)
            # print(mode)

def set_mode(master, mode):
    # Check if mode is available
    if mode not in master.mode_mapping():
        print('Unknown mode : {}'.format(mode))
        print('Try:', list(master.mode_mapping().keys()))
        pass # in application could be sys.exit(1)

    # Get mode ID
    mode_id = master.mode_mapping()[mode]
    # Set new mode
    # master.mav.command_long_send(
    #    master.target_system, master.target_component,
    #    mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
    #    0, mode_id, 0, 0, 0, 0, 0) or:
    # master.set_mode(mode_id) or:
    master.mav.set_mode_send(
        master.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id)

    while True:
        # Wait for ACK command
        # Would be good to add mechanism to avoid endlessly blocking
        # if the autopilot sends a NACK or never receives the message
        ack_msg = master.recv_match(type='COMMAND_ACK', blocking=True)
        ack_msg = ack_msg.to_dict()

        # Continue waiting if the acknowledged command is not `set_mode`
        if ack_msg['command'] != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
            continue

        # Print the ACK result !
        print(mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description)
        break


if __name__ == "__main__":
    # Create the connection
    master = mavutil.mavlink_connection('udpin:localhost:14551')
    # Wait a heartbeat before sending commands
    master.wait_heartbeat()
    # Thread(target=get_mode, args=(master, )).start()
    while True:
        mode = input("->")
        set_mode(master, mode)
        time.sleep(1)