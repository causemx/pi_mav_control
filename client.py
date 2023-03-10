import select
import sys
import arg_parse
import time
import const
from socket import socket, AF_INET, SOCK_STREAM
from ctl import control


class Client:
    def __init__(self, buffer=1024) -> None:
        self.client = socket(AF_INET, SOCK_STREAM)
        self.bufer = buffer 

    def start(self, host, port):
        try:
            self.client.connect((host, port)) 
        except control.ControlError:
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
    
    def handle_recv(self, recv, delay=0):
        print('received: {}, dalay: {}s'.format(recv, delay))
        time.sleep(delay)
        rs = recv.split()
        args = None
        if rs[0] == "mf":
            args = arg_parse.parse(const.CLIENT_MOVE_FORWORD)
            args.func(args)
        elif rs[0] == "mo":
            args = arg_parse.parse(const.CLIENT_MOVE_ORIGIN)
            args.func(args)
        elif rs[0] == "mb":
            args = arg_parse.parse(const.CLIENT_MOVE_BACK)
            args.func(args)
        else:
            try:
                args = arg_parse.parse(recv.split())
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

    #control.connect(["udp", "127.0.0.1", "14551"])

    try:
        _client = Client()
        _client.start(const.CLIENT_HOST, const.CLIENT_PORT)
        _client.receive()
    except ConnectionRefusedError:
        print("connection_refused.")