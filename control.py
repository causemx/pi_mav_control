from pymavlink import mavutil
import argparse
import time



def connection(host, port, retry=3):
    _retry = 0
    while True:
        try:
            master = mavutil.mavlink_connection('udpin:{}:{}'.format(host, port))
            master.wait_heartbeat()
            print('connected')
            return master
        except:
            print('retry')
            _retry = _retry + 1
            if _retry > retry:
                print('Can not connected to uav.')
                raise ConnectionError
            time.sleep(0.3)

def main(args) -> int:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()
    
    parser_arm = subparser.add_parser("arm", help="Arming/Disarm UAV throttle.")
    parser_arm.add_argument('--isarm', type=int, default=1, help="1: arm, 0: disarm.")
    parser_arm.set_defaults(func=arm)

    parser_takeoff = subparser.add_parser("takeoff", help="Takeoff UAV to expect height.")
    parser_takeoff.add_argument('height', type=int, default=2, help="Expect height for UAV takeoff.")
    parser_takeoff.set_defaults(func=takeoff)

    parser_mode = subparser.add_parser("mode", help="Get current UAV mode.")
    parser_mode.set_defaults(func=mode)

    parser_setmode = subparser.add_parser("setmode", help="Set UAV mode.")
    parser_setmode.add_argument("mode", type=str, help="Enter expected mode here.")
    parser_setmode.set_defaults(func=set_mode)
    
    parser_move = subparser.add_parser("move", help="Make UAV moving [North, East, Up]")
    parser_move.add_argument("movement", type=int, help="Move North n meters.")
    parser_move.set_defaults(func=move)

    try:
        args = parser.parse_args(args)
        args.func(args)
    except:
        pass
    return 0

def arm(args):
    master.mav.command_long_send(master.target_system, master.target_component, \
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, args.isarm, 0, 0, 0, 0, 0, 0)

    while True:
        master.motors_armed_wait()
        print('Ack!')
        break


def takeoff(args):
    master.mav.command_long_send(master.target_system, master.target_component, \
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, args.height)

    while True:
        msg = master.recv_match(type='STATUSTEXT', blocking=True)
        print(msg)
        break

def mode(args):
    while True:
        msg = master.recv_match(type='HEARTBEAT', blocking = True)
        if msg:
            mode = mavutil.mode_string_v10(msg)
            print(mode)
            break

def set_mode(args):
    if args.mode not in master.mode_mapping():
        print('Unknown mode : {}'.format(args.mode))
        print('Try:', list(master.mode_mapping().keys()))
        pass # in application could be sys.exit(1)

        # Get mode ID
    mode_id = master.mode_mapping()[args.mode]

    master.mav.set_mode_send(master.target_system, \
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,mode_id)

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

def move(args):
    master.mav.send(mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, master.target_system, \
        master.target_component, mavutil.mavlink.MAV_FRAME_LOCAL_NED, \
            int(0b010111111000), args.movement, 0, -10, 0, 0, 0, 0, 0, 0, 0, 0))
    
    while True:
        msg = master.recv_match(
            type='LOCAL_POSITION_NED', blocking=True)
        print(msg)
        break


if __name__ == "__main__":
    try:
        master = connection("127.0.0.1", 14551)
    except ConnectionError as err:
        exit(err.errno)
    
    while True:
        msg = input(" -> ")
        error_code = main(msg.split())
        if error_code != 0:
            break
