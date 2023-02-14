# Import mavutil

from pymavlink import mavutil

# Create the connection
master = mavutil.mavlink_connection('udpin:localhost:14551')
# Wait a heartbeat before sending commands
master.wait_heartbeat()

print(f"Heartbeat from system (system {master.target_system}, component {master.target_component}")

master.mav.command_long_send(master.target_system, master.target_component,
                                     mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0, 1, 0, 0, 0, 0, 0, 0)

while 1:
    master.motors_armed_wait()
    print('Armed!')
    break
# msg = master.recv_match(type='COMMAND_ACK', blocking=True)
# print(msg)

master.mav.command_long_send(master.target_system, master.target_component,
                                     mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0, 30)

msg = master.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)
