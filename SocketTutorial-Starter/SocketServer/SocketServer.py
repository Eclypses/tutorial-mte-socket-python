#!/usr/bin/env python3
#THIS SOFTWARE MAY NOT BE USED FOR PRODUCTION. Otherwise,
#The MIT License (MIT)
#
#Copyright (c) Eclypses, Inc.
#
#All rights reserved.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import socket
import sys
import struct
import base64

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    # This tutorial uses Sockets for communication.
	# It should be noted that the MTE can be used with any type of communication. (SOCKETS are not required!)

    print ("Starting Python Socket Server.")
    
    port = 27015
    # Prompt for port so user can change it at runtime.
    newPort = input("Please enter port to use, press Enter to use default: " + str(port) + "\n")
    if newPort:
        port = int(newPort)    
    
    sock.bind(('localhost', port))

    print ("Listening for new Client connection...")

    sock.listen()
    connection, addr = sock.accept()
    print("Socket Server is listening on ", addr, " : port", port)
                
    while True:

        print ("Listening for messages from Client...")
        # Get the length of bytes coming in.
        rcv_len_bytes = bytearray(4)    
        rcv_len_bytes = recv_all(connection, 4)
        if rcv_len_bytes == None:
            break
        
        rcv_len_bytes = struct.unpack('>I', rcv_len_bytes)[0]

        #
        # Get the full message based on length of bytes coming in.        
        rcv_bytes = recv_all(connection, rcv_len_bytes)
        if len(rcv_bytes) > 0:
            # Convert byte data so we can view it in console (this step is for display purposes).          

            #
            # For demonstration purposes only to show packets.
            print("The packet received packet: ", rcv_bytes.decode())          

            #
            # This puts the bytes of the send length.
            to_send_len = len(rcv_bytes)

            # Big Endian the packet length
            to_send_len = struct.pack('>I', to_send_len)

            #
            # For demonstration purposes only to show packets.
            print("The packet being sent: ", rcv_bytes.decode())

            # Send the length of the message.
            connection.sendall(bytes(to_send_len))

            # Send the actual message.
            connection.sendall(rcv_bytes)

        else:
            break            

    connection.shutdown(socket.SHUT_RDWR)
    connection.close()
    print("Program stopped.")    

def recv_all(sock, n):
    
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
        
main()
