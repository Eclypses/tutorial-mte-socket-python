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

sys.path.append('..\include')
import MTEHelper
import SocketManager

#This tutorial uses Sockets for communication.
#It should be noted that the MTE can be used with any type of communication. (SOCKETS are not required!)

def main():
    #Create Instances of MTEHelper and SocketManager.
    mte = MTEHelper.MTEHelper()
    sock = SocketManager.SocketManager()

    print ("Starting Python Socket Server.")
    print("Using MTE Version: ", mte.get_mte_version(mte.encoder))

    #Check MTE license.
    mte.initMte() 

    #Create Socket for Client to connect to.
    sock.create_socket()

    ret = mte.exchangeServerMteInfo(sock)
    if ret == False:
        print("Error exchanging MTE info with the Client.")
        sock.close_socket(sock.connection)
        quit()

    # Create instances of MTE.
    mte.create_encoder()
    mte.create_decoder()

    runDiagnosticTest(mte,sock)

    while True:
        print ("\nListening for messages from Client...")

        (rcv_bytes,header) = sock.listen_socket(sock.connection)
        
        if len(rcv_bytes) > 0:
            # Decode incoming message and check for non-error response.
            # When checking the status on decode use "status_is_error"
            # Only checking if status is success can be misleading, there may be a
            # warning returned that the user can ignore.
            # See MTE Documentation for more details.
            (decoded_text, decoder_status) = mte.decode_message(bytes(rcv_bytes))
            if decoder_status == False:
                sock.close_socket(sock.connection)
                print("Socket server closed due to decoding error.")
                quit()

            # For demonstration purposes only to show packets.
            print("Base64 encoded representation of the received packet: ", base64.encodebytes(rcv_bytes))
            print("Decoded data: ", decoded_text)

            # Encode returning text and check to ensure successful result.
            (encoded_return, encoder_status) = mte.encode_message(decoded_text)
            if encoder_status == False:
                sock.close_socket(sock.connection)
                print("Socket server closed due to encoding error.")
                quit()

            # Send the actual message.
            sock.send_message(sock.connection,"m",encoded_return)

        else:
            break            

    sock.close_socket(sock.connection)
    print("Program stopped.")    

def runDiagnosticTest(mte,sock):
    #Receive and decode the message.
    (rcv_bytes,header) = sock.listen_socket(sock.connection)
    if header != "m" and header != "M":
        print("Failure")
        sock.close_socket(sock.connection)
        quit()
    (decoded_text, decoder_status) = mte.decode_message(bytes(rcv_bytes))
    if decoded_text.decode('utf8') == "ping":
        print("Server Decoder decoded the message from the client Encoder successfully.\n")
    else:
        print("Server Decoder DID NOT decode the message from the client Encoder successfully.\n")
        return False
    
    #Encode and send the message.
    (encoded_bytes, encoder_status) = mte.encode_message("ack")
    sock.send_message(sock.connection,"m",encoded_bytes)

    return True

main()
