"""
    
"""

import socket

# https://docs.python.org/2/library/struct.html#struct.pack
import struct

# https://github.com/msgpack/msgpack-python
import msgpack


# extend the socket
class PrefixMessagePackSocket():
  def __init__(self, connection=None):
    if connection is None:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.socket = connection
    
  def send(self, message):
    packed_message = msgpack.packb(message)
    message_size = len(packed_message)
    
    # convert the message size to binary
    # (struct pack is faster than to_bytes)
    # ! - Byte order: network (= big-endian); Size: standard
    # I - C Type: unsigned int; Standard size: 4
    message_size_packed = struct.pack("!I", message_size)
    
    # send the size of the message in 4bytes
    self.socket.send(message_size_packed)
    
    # send the message itself
    self.socket.send(packed_message)
    
  def receive(self):
    # read the size of the incomming message
    in_size_packed = self.socket.recv(4)

    # note: unwrap the touple that is returned by the unpack
    (in_size,) = struct.unpack("!I", in_size_packed)
    # read the rest of the data
    in_message_packed = self.socket.recv(in_size)
    
    unpacked = msgpack.unpackb(in_message_packed)
    
    return unpacked
  
  def __getattr__(self, attr):
    return getattr(self.socket, attr)
  
  def __enter__(self):
    self.socket.__enter__()
    return self

  def __exit__(self, type, value, traceback):
    self.socket.__exit__(type, value, traceback)

