#THIS SOFTWARE MAY NOT BE USED FOR PRODUCTION. Otherwise,
#The MIT License (MIT)

#Copyright (c) Eclypses, Inc.

#All rights reserved.

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import EcdhP256
import socket
import sys
import struct
import base64

class SocketManager():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.connection = None
        
    def create_socket(self):
        # Called by the Server to create the socket
        # for the Client to connect to.
        port = 27015
        # Prompt for port so user can change it at runtime.
        newPort = input("Please enter port to use, press Enter to use default: " + str(port) + "\n")
        if newPort:
            port = int(newPort)    
        self.sock.bind(('localhost', port))

        print ("Listening for new Client connection...")

        self.sock.listen()
        self.connection, addr = self.sock.accept()
        print("\nSocket Server is listening on ", addr, " : port", port)

    def bind_socket(self):
        # Called by the Client to bind to the socket
        # created by the Server.
        
        # Request Server ip and port.
        host = "localhost"
        newHost = input("Please enter ip address of Server, press Enter to use default: " + host + "\n")
        if newHost:
            host = newHost

        port = 27015
        # Prompt for port so user can change it at runtime.
        newPort = input("Please enter port to use, press Enter to use default: " + str(port) + "\n")
        if newPort:
            port = int(newPort)

        self.sock.connect((host, port))

        print("\nClient connected to server.")

    def listen_socket(self,connection):
        # Get the length of bytes coming in.
        rcv_len_bytes = bytearray(5)    
        rcv_len_bytes = self.recv_all(connection,5)
        if rcv_len_bytes == None:
            return ""

        header = chr(rcv_len_bytes[len(rcv_len_bytes)-1])
            
        rcv_len_bytes = struct.unpack('>I', rcv_len_bytes[:-1])[0]
        
        # Get the full message based on length of bytes coming in.        
        return (self.recv_all(connection,rcv_len_bytes),header)

    def close_socket(self,connection):
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()

    def send_message(self, connection, header, message):
        # This puts the bytes of the send length.
        to_send_len = len(message)

        # Big Endian the packet length
        to_send_len = bytearray(struct.pack('>I', to_send_len))

        #Put the header byte into 5th byte
        to_send_len.extend(header.encode('UTF-8'))

        # Send the length of the message.
        connection.sendall(bytes(to_send_len))
                                
        # Send the actual message.
        connection.sendall(bytes(message))

    def recv_all(self, connection, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = connection.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
