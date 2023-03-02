from socket import socket, AF_INET, SOCK_STREAM
import select


class Client:
    def __init__(self, buffer=1024) -> None:
        self.client = socket(AF_INET, SOCK_STREAM)
        self.bufer = buffer 

    def start(self, host, port):
        self.client.connect((host, port)) 


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

if __name__ == "__main__":
    _client = Client()
    _client.start("127.0.0.1", 5566)
    _client.receive()