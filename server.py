import arg_parse
import sys
import const
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
        except ConnectionError as err:
            print("Encounting connection error: {}".format(str(err)))

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
            error_code = self.handle_args(msg)
            if error_code != 0:
                break

    def handle_args(self, input):
        if not input:
            return 0
        
        rs = input.split()
        if rs[0] == "mf":
            args = arg_parse.parse(const.SERVER_MOVE_FORWORD)
            args.func(args)
        elif rs[0] == "mo":
            args = arg_parse.parse(const.SERVER_MOVE_ORIGIN)
            args.func(args)
        elif rs[0] == "mb":
            args = arg_parse.parse(const.SERVER_MOVE_BACK)
            args.func(args)
        else:
            try:
                args = arg_parse.parse(rs)
                args.func(args)
            except:
                pass
        return 0


    # prefix is for name identification.
    # using list to avoid arise RuntimeError: dictionary changed size during iteration.
    def broadcast(self, msg, prefix="") -> None:  
        for sock in list(self.clients.keys()): 
            try:
                sock.send(bytes(prefix, "utf8")+msg)
            except ConnectionError:
                # print(f"{clients[sock]} was disconnected")
                sock.close()
                del self.clients[sock]
 
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
    
    control.connect(["udp", "127.0.0.1", "14550"])
        
    server = Server()
    server.start(const.SERVER_HOST_BIND, const.SERVER_PORT)