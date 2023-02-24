from ctl import control
import argparse

def main(args) -> int:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers()

    parser_connect = subparser.add_parser("connect", help="Connect to UAV.")
    parser_connect.add_argument("connect_info", nargs='+', help="For serial port connect, input: 'serial' [device] [baudrate]; \
        For UDP input connect, input: 'udp' [host] [port].") 
    parser_connect.set_defaults(func=control.connect)
    
    parser_arm = subparser.add_parser("arm", help="Arming/Disarm UAV throttle.")
    parser_arm.add_argument('--isarm', type=int, default=1, help="1: arm, 0: disarm.")
    parser_arm.set_defaults(func=control.arm)

    parser_takeoff = subparser.add_parser("takeoff", help="Takeoff UAV to expect height.")
    parser_takeoff.add_argument('height', type=int, default=2, help="Expect height for UAV takeoff.")
    parser_takeoff.set_defaults(func=control.takeoff)

    parser_mode = subparser.add_parser("mode", help="Get current UAV mode.")
    parser_mode.set_defaults(func=control.mode)

    parser_setmode = subparser.add_parser("setmode", help="Set UAV mode.")
    parser_setmode.add_argument("mode", type=str, help="Enter expected mode here.")
    parser_setmode.set_defaults(func=control.set_mode)
    
    parser_move = subparser.add_parser("move", help="Make UAV moving [East, North, Down] in local coord.")
    parser_move.add_argument("movement", type=int, nargs='+', help="Move [east/west] [north/south] [down/up] for meters")
    parser_move.add_argument("-e", "--east", type=int, default=0, help="Move east/west for n meters.")
    parser_move.add_argument("-n", "--north", type=int, default=0, help="Move north/south for n meters.")
    parser_move.add_argument("-d", "--down", type=int, default=0, help="Move down/Up for n meters.")
    parser_move.set_defaults(func=control.move)

    try:
        args = parser.parse_args(args)
        args.func(args)
    except:
        pass
    return 0


if __name__ == "__main__":
    while True:
        msg = input(" -> ")
        error_code = main(msg.split())
        if error_code != 0:
            break

