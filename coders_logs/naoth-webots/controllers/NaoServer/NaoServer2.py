"""
    Server which prefixes the messages with the size of the rest of the message
    This is currently used for testing the integration with the NaoTHSoccer Code
"""
import sys
import socket

# https://docs.python.org/2/library/struct.html#struct.pack
import struct

# https://github.com/msgpack/msgpack-python
import msgpack

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1412  # Port to listen on (non-privileged ports are > 1023)

if __name__ == "__main__":
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        
        # wait for connection
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            
            # read the size of the incomming message
            in_size_packed = conn.recv(4)
            # note: unwrap the touple that is returned by the unpack
            (in_size,) = struct.unpack("!I", in_size_packed)
            print(f"in size: {in_size}")
            
            # read the rest of the data
            in_message_packed = conn.recv(in_size)
            print(f"in message: {in_message_packed}")

            # pack the message
            message = "Hello World"
            print(f"out message: {message}")
            packed_message = msgpack.packb(message)
            
            # send the size of the message in 4bytes
            message_size = len(packed_message)
            
            # convert the message size to binary
            # (struct pack is faster than to_bytes)
            # ! - Byte order: network (= big-endian); Size: standard
            # I - C Type: unsigned int; Standard size: 4
            message_size_packed = struct.pack("!I", message_size)
            
            print(f"out size: {message_size}, binary: {message_size_packed}")
            conn.send(message_size_packed)

            # send the message itself
            conn.send(packed_message)

            
