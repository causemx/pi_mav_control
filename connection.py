from pymavlink import mavutil
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
                break
            time.sleep(0.3)
            


if __name__ == "__main__":
    master = connection("127.0.0.1", 14551)

    