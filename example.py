import sys
import arg_parse
from ctl import control


class ControlError(Exception):
    pass

def main(input) -> int:
    try:
        args = arg_parse.parse(input)
        args.func(args)
    except ControlError:
        pass
    return 0


if __name__ == "__main__":
    while True:
        msg = input(" -> ")
        try:
            ret = control.connect(msg.split())
            print(ret)
            if ret == 'connected':
                break
        except ConnectionError:
            print("connection_error")
            sys.exit(1)
            
    while True:
        msg = input(" -> ")
        error_code = main(msg.split())
        if error_code != 0:
            break

