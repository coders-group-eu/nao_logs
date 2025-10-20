"""
    Start this after the NaoServer script is started as a webots controller. This script will receive current joint
    positions, modify them and send them back
"""

from PrefixMessagePackSocket import PrefixMessagePackSocket
import math as m

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 1412  # The port used by the server


with PrefixMessagePackSocket() as s:
    s.connect((HOST, PORT))
    
    # send an initialization message (fake for now)
    message = "Hello World"
    s.send(message)
    
    while True:
        data = s.receive()
        #print(data)
        
        # unpack
        time = data['Time']
        
        sine_factor = m.radians(119.5)
        new_head_yaw = sine_factor * m.sin(time)

        joints = [0]*25
        joints[0] = new_head_yaw
        
        motor_commands = {'Position':joints}
        
        s.send(motor_commands)
        
