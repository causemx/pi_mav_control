from enum import Enum
import math
from pymavlink import mavutil

import time


class ControlError(Exception):
 
    # Constructor or Initializer
    def __init__(self, value):
        self.value = value
 
    # __str__ is to print() the value
    def __str__(self):
        return(repr(self.value))
    
class Movement(Enum):
    NORTH = 1,
    SOUTH = 2,
    WEST = 3,
    EAST = 4 
    

def connect(args, retry=3) -> str:
    global master
    # _args = args.connect_info
    _retry = 0
    while True:
        try:
            #master = mavutil.mavlink_connection('/dev/serial0', baud=921600)
            #master = mavutil.mavlink_connection('udpin:{}:{}'.format(host, port))
            if args[1] == "serial":
                master = mavutil.mavlink_connection(args[2], baud=int(args[3]))
            elif args[1] == "udp":
                master = mavutil.mavlink_connection('udpin:{}:{}'.format(args[2], args[3]))
            else:
                return 'unknown_connection_type'

            master.wait_heartbeat()
            return 'connected'
        except ControlError:
            print("retry...:{}".format(_retry))
            _retry = _retry + 1
            if _retry > retry:
                print('fail_to_connect_uav')
                raise ConnectionError
            time.sleep(0.3)


def arm(args) -> None:
    master.mav.command_long_send(master.target_system, master.target_component, \
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, args.isarm, 0, 0, 0, 0, 0, 0)

    while True:
        master.motors_armed_wait()
        print('Ack!')
        break


def takeoff(args) -> None:
    master.mav.command_long_send(master.target_system, master.target_component, \
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, args.height)

    _retry = 0
    while True:
        _retry = _retry + 1
        # msg = master.recv_match(type='STATUSTEXT', blocking=True)
        msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        if msg: 
            print(msg)
            break
        if _retry > 3:
            print("Time out, can not recive ACK.")
            break


def mode(args) -> None:
    while True:
        msg = master.recv_match(type='HEARTBEAT', blocking = True)
        mode = mavutil.mode_string_v10(msg)
        print(mode)
        break

def set_mode(args) -> None:
    if args.mode not in master.mode_mapping():
        print('Unknown mode : {}'.format(args.mode))
        print('Try:', list(master.mode_mapping().keys()))
        pass # in application could be sys.exit(1)

        # Get mode ID
    mode_id = master.mode_mapping()[args.mode]

    master.mav.set_mode_send(master.target_system, \
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,mode_id)

    while True:
        try:
            ack_msg = master.recv_match(type='COMMAND_ACK', blocking=True, timeout=1)
        except ControlError:
            print("can not receive ack")
            break
        
        time.sleep(0.3)
        ack_msg = ack_msg.to_dict()

        # Continue waiting if the acknowledged command is not `set_mode`
        if ack_msg['command'] != mavutil.mavlink.MAV_CMD_DO_SET_MODE:
            continue

        # Print the ACK result !
        print(mavutil.mavlink.enums['MAV_RESULT'][ack_msg['result']].description)
        break

def move(args) -> None:
    
    loc = master.location()
    
    # Local
    """master.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, master.target_system, \
        master.target_component, mavutil.mavlink.MAV_FRAME_LOCAL_NED, \
            int(0b010111111000), args.movement[0], args.movement[1], args.movement[2], 0, 0, 0, 0, 0, 0, 0, 0))"""
    # Global
    # move to north
    
    if args.movement == 0:
            master.mav.send(mavutil.mavlink.MAVLink_set_position_target_global_int_message(
        10, 
        master.target_system, master.target_component, 
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
        int(0b110111111000),
        int(loc.lat*1e7)+5000,
        int(loc.lng*1e7),
        10, 
        0, 0, 0,
        0, 0, 0,
        1.57, 0.5
        ))
    elif args.movement == 1:
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
        ))

  
        
    
    while True:
        msg = master.recv_match(
            type='LOCAL_POSITION_NED', blocking=True)
        print(msg)
        break

def stop_all(args):
    master.mav.set_mode_send(master.target_system, \
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 17)
