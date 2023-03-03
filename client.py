import select, sys, argparse
from socket import socket, AF_INET, SOCK_STREAM
from ctl import control



class Client:
    def __init__(self, buffer=1024) -> None:
        self.client = socket(AF_INET, SOCK_STREAM)
        self.bufer = buffer 

    def start(self, host, port):
        try:
            self.client.connect((host, port)) 
        except:
            raise ConnectionRefusedError 


    def receive(self):
        while True:
            try:
                ready_to_read, ready_to_write, in_error = \
                select.select([self.client,], [self.client,], [], 5)
            except select.error:
                self.client.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
                self.client.close()
                # connection error event here, maybe reconnect
                print('connection error')
                break
            if len(ready_to_read) > 0:
                recv = self.client.recv(self.bufer).decode("utf8")
                if not recv:
                    print("server was disconnect")
                    self.client.close()
                    break
                # do stuff with received data
                self.handle_recv(recv)
                
                
            if len(ready_to_write) > 0:
                pass
    
    def handle_recv(self, recv):
        print('received: {}'.format(recv))
        args = recv.split()

        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
       
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

    print("Please connect to UAV first.")
    while True:
        msg = input(" -> ")
        try:
            ret = control.connect(msg.split())
            if ret == 'connected':
                break
        except ConnectionError:
            print("connection_error")
            sys.exit(1)

    try:
        _client = Client()
        _client.start("127.0.0.1", 5566)
        _client.receive()
    except ConnectionRefusedError:
        print("connection_refused.")