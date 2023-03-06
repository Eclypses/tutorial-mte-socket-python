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
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def main():    
	# This tutorial uses Sockets for communication.
	# It should be noted that the MTE can be used with any type of communication. (SOCKETS are not required!)

    print ("Starting Python Socket Client.")

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

    sock.connect((host, port))

    print("Client connected to server.")
      
    while True:
        # Enter text to send to server.
        text_to_send = input("\nPlease enter text to send : (To end please type 'quit')\n")

        # Check if text is 'quit' so we can terminate loop if needed.
        if text_to_send.lower() == "quit":
            # Break out of the loop to send messages.
            break            

        # For demonstration purposes only to show packets.
        print("The packet being sent: ", text_to_send)

        # Get the length of the text we are sending to send length-prefix
        to_send_len = len(text_to_send)
        
        # Big Endian the packet length
        to_send_len = struct.pack('>I', to_send_len)

        # Send the Packet length.
        sock.sendall(bytes(to_send_len))

        # Send the actual message.
        sock.sendall(text_to_send.encode())
        
        # Receive the length of the incoming Packet
        rcv_len_bytes = recv_all(sock, 4)
        rcv_len_bytes = struct.unpack('>I', rcv_len_bytes)[0]        

        # Receive the incoming packet, using the length sent beforehand.
        rcv_bytes = recv_all(sock, rcv_len_bytes)        

        # For demonstration purposes only to show packets.
        print("The received packet: ", rcv_bytes.decode())

    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
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