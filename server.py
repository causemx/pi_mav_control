import argparse
import sys
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from ctl import control



class Server:
    def __init__(self, buffer=1024) -> None:
        self.server = socket(AF_INET, SOCK_STREAM)
        self.buffer = buffer
        self.clients = {}
        self.addresses = {}

    def start(self, host="localhost", port=5566):
        try:
            self.server.bind((host, port))
        except:
            raise ConnectionError

        self.server.listen(5)
        print("Waiting for connection...")
  
        self.accept_thread = Thread(target=self.accept_incoming_connections)
        self.accept_thread.start()
        self.accept_thread.join()
        self.stop()

    def stop(self):
        print('Server stop')
        self.server.close()

    def accept_incoming_connections(self):
        while True:
            client, client_addr = self.server.accept()
            msg = "{}:{} has connected".format(*client_addr)
            print(msg)
            client.send(bytes(msg, "utf8"))
            
            self.addresses[client] = client_addr
            Thread(target=self.handle_recv, args=(client,)).start()
            Thread(target=self.handle_send, args=(client,)).start()

    def handle_recv(self, client):
        name = self.addresses[client]
        msg = "{} has joined!".format(name)
        print(msg)
        self.broadcast(bytes(msg, "utf8"))
        self.clients[client] = name

    def handle_send(self, client):
        while True:
            msg = input(" [Server]: -> ")
            self.broadcast(bytes(msg, "utf8"))
            error_code = self.handle_args(msg.split())
            if error_code != 0:
                break

    def handle_args(self, args):
        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
        """parser_connect = subparser.add_parser("connect", help="connect to UAV")
        parser_connect.add_argument("connect_info", nargs='+', help="For serial port connect, input: 'serial' [device] [baudrate]; \
            For UDP input connect, input: 'udp' [host] [port].") 
        parser_connect.set_defaults(func=control.connect)"""

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

    def broadcast(self, msg, prefix="") -> None:  # prefix is for name identification.
        for sock in list(self.clients.keys()): # using list to avoid arise RuntimeError: dictionary changed size during iteration.
            try:
                sock.send(bytes(prefix, "utf8")+msg)
            except:
                # print(f"{clients[sock]} was disconnected")
                sock.close()
                del self.clients[sock]
 
if __name__ == "__main__":
    print("Please connect to UAV first.")
    while True:
        msg = input(" -> ")
        try:
            ret = control.connect(msg.split())
            if ret is 'connected':
                break
        except ConnectionError:
            print("connection_error")
            sys.exit(1)
        
    server = Server()
    server.start("0.0.0.0", 5566)