"""
    Simple Controller that shows how to read sensor values and set motor commands

    This script is expected to run as a webots controller. It will wait for a connection and as soon as the connection
    is established it reads the messages as interprets them as join values.

    For testing start the simple_python_client.py script after this. The robot should turn its head back and forth.
"""
import sys, math
from PrefixMessagePackSocket import PrefixMessagePackSocket
from Nao import Nao
from timeit import default_timer as timer

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1412  # Port to listen on (non-privileged ports are > 1023)


if __name__ == "__main__":
    
    # init a nao robot
    nao = Nao()

    with PrefixMessagePackSocket() as s:
        
        # open a soccet and wait for the connection of the controller
        s.bind((HOST, PORT))
        s.listen()
            
        while(True):
            
            print('Listen for connection at port ', PORT)
            nao.step(nao.timestep)
            
            conn, addr = s.accept()
            conn = PrefixMessagePackSocket(conn)

            print(type(conn))
            
            try:
                with conn:
                    
                    print('Connected by', addr)
                    nao.step(nao.timestep)
                    
                    # read an initializer message: for now it's just a placeholder
                    in_data = conn.receive()
                    #print(f"in message: {in_data}")
                    
                    conn.send(nao.getSensors())
                    
                    # run simulation
                    while nao.step(nao.timestep) != -1:
                        
                        #start = timer()
                        
                        nao.setActuators(conn.receive())
                        
                        conn.send(nao.getSensors())
                        
                        #end = timer()
                        #print((end - start)*1000)
                        
            except Exception as e:
                print("Connection interrupted")
                print(e)
                continue
                
                
                
