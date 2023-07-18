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
import uuid

sys.path.append('..\include')
import MTEHelper
import SocketManager

#This tutorial uses Sockets for communication.
#It should be noted that the MTE can be used with any type of communication. (SOCKETS are not required!)

def main():
    #Create Instances of MTEHelper and SocketManager.
    mte = MTEHelper.MTEHelper()
    sock = SocketManager.SocketManager()
    
    print ("Starting Python Socket Client.")
    print("Using MTE Version: ", mte.get_mte_version(mte.encoder))

    #Check MTE license.
    mte.initMte()

    #Connect to the socket created by the Server.
    sock.bind_socket()
    
    ret = mte.exchangeClientMteInfo(sock)
    if ret == False:
        print("Error exchanging MTE info with the Server.")
        sock.close_socket(sock.sock)
        quit()

    # Create instances of MTE.
    mte.create_decoder()
    mte.create_encoder()
    
    runDiagnosticTest(mte,sock)

    while True:
        # Enter text to send to server.
        text_to_send = input("\nPlease enter text to send : (To end please type 'quit')\n")

        # Check if text is 'quit' so we can terminate loop if needed.
        if text_to_send.lower() == "quit":
            # Break out of the loop to send messages.
            break              
 
        # Encode text to send and check for successful result.
        (encoded_bytes, encoder_status) = mte.encode_message(text_to_send)
        if encoder_status == False:
            sock.close_socket(sock.sock)
            print("Socket client closed due to encoding error.")
            quit()

        sock.send_message(sock.sock,"m",encoded_bytes)

        print ("Listening for messages from Client...")

        (rcv_bytes,header) = sock.listen_socket(sock.sock)

        # Decode incoming message.
        (returned_text, decoder_status) = mte.decode_message(bytes(rcv_bytes))
        if decoder_status == False:
            sock.close_socket(sock.sock)
            print("Socket client closed due to decoding error.")
            quit()

        # Convert byte array to string to view in console (this step is for display purposes)
        print("Base64 encoded representation of the received packet: " , base64.encodebytes(rcv_bytes))

        if returned_text.decode('utf8') == text_to_send:
            print("Decoded Data from the Server matches the Original Data.")
        else:
            print("\nDecoded Data and Original Data do NOT match.")
            sock.close_socket(sock.sock)
            quit()

    sock.close_socket(sock.sock)
    
    print("Program stopped.")

def runDiagnosticTest(mte,sock):
    #Encode and send the message.
    (encoded_bytes, encoder_status) = mte.encode_message("ping")
    sock.send_message(sock.sock,"m",encoded_bytes)

    #Receive and decode the message.
    (rcv_bytes,header) = sock.listen_socket(sock.sock)
    if header != "m" and header != "M":
        print("Failure")
        sock.close_socket(sock.connection)
        quit()
    (decoded_text, decoder_status) = mte.decode_message(bytes(rcv_bytes))
    if decoded_text.decode('utf8') == "ack":
        print("Client Decoder decoded the message from the server Encoder successfully.\n")
    else:
        print("Client Decoder DID NOT decode the message from the server Encoder successfully.\n")
        return False
    
    return True

main()
