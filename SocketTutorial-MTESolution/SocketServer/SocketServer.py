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

# Step 3
#---------------------------------------------------
# MKE and Fixed length add-ons are NOT in all SDK
# MTE versions. If the name of the SDK includes
# "-MKE" then it will contain the MKE add-on. If the
# name of the SDK includes "-FLEN" then it contains
# the Fixed length add-on.
# ---------------------------------------------------

# ------------------------------------------
# Uncomment the following two imports to use
# the MTE Core.
# ------------------------------------------
from MteEnc import MteEnc
from MteDec import MteDec
# ------------------------------------------
# Uncomment the following two imports to use
# the MKE addon-on.
# ------------------------------------------
#from MteMkeEnc import MteMkeEnc
#from MteMkeDec import MteMkeDec
# ------------------------------------------
# Uncomment the following two imports to use
# the fixed length add-on.
# ------------------------------------------
#from MteFlenEnc import MteFlenEnc
#from MteDec import MteDec

from MteStatus import MteStatus
from MteBase import MteBase

# Step 4
#--------------------------------------------
# The fixed length, only needed for MTE FLEN
#--------------------------------------------
fixed_bytes = 8

#----------------------------------------------------------
# Create the MTE Decoder, uncomment to use MTE core OR FLEN
# Create the Mte Fixed length Decoder (SAME as MTE Core)
#----------------------------------------------------------
decoder = MteDec.fromdefault()
#---------------------------------------------------
# Create the Mte MKE Decoder, uncomment to use MKE
#---------------------------------------------------
#decoder = MteMkeDec.fromdefault()
decoder_status = MteStatus.mte_status_success

#---------------------------------------------------
# Create the Mte Encoder, uncomment to use MTE core
#---------------------------------------------------
encoder = MteEnc.fromdefault()
#---------------------------------------------------
# Create the Mte MKE Encoder, uncomment to use MKE
#---------------------------------------------------
#encoder = MteMkeEnc.fromdefault()
#---------------------------------------------------------------
# Create the Mte Fixed length Encoder, uncomment to use MTE FLEN
#---------------------------------------------------------------
#encoder = MteFlenEnc.fromdefault(fixed_bytes)
encoder_status = MteStatus.mte_status_success

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Step 5
# Set default entropy, nonce and identifier
# Providing Entropy in this fashion is insecure. This is for demonstration purposes only and should never be done in practice. 
entropy_min_bytes = MteBase.get_drbgs_entropy_min_bytes(encoder.get_drbg())
entropy = bytes("0" * entropy_min_bytes, 'utf-8')

encoder_nonce = 0

#
# OPTIONAL!!! adding 1 to Decoder nonce so return value changes -- same nonce can be used for Encoder and Decoder
# on client side values will be switched so they match up Encoder to Decoder and vice versa 

decoder_nonce = 1
identifier = "demo"

def main():
    # This tutorial uses Sockets for communication.
	# It should be noted that the MTE can be used with any type of communication. (SOCKETS are not required!)

    print ("Starting Python Socket Server.")

    print("Using MTE Version: ", get_mte_version())

    # Step 6
    # Check mte license
    # Initialize MTE license. If a license code is not required (e.g., trial mode), this can be skipped.
    if not MteBase.init_license("LicenseCompanyName", "LicenseKey"):
        encoder_status = MteStatus.mte_status_license_error
        print("License init error ({0}): {1}.".format(
            MteBase.get_status_name(encoder_status),
            MteBase.get_status_description(encoder_status)),
            file=sys.stderr)
        return encoder_status.value

    # Step 7
    # Create instances of MTE
    create_decoder()
    create_encoder() 
    
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

            # Step 8
            # Decode incoming message and check for non-error response.
            # When checking the status on decode use "status_is_error"
            # Only checking if status is success can be misleading, there may be a
            # warning returned that the user can ignore.
            # See MTE Documentation for more details.
            (decoded_text, decoder_status) = decoder.decode(bytes(rcv_bytes))
            if decoder_status != MteStatus.mte_status_success:
                print("Error decoding: Status: ({0}): {1}".format(
                    MteBase.get_status_name(decoder_status),
                    MteBase.get_status_description(decoder_status)),
                    file=sys.stderr)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                print("Socket server closed due to decoding error.")
                return

            #
            # For demonstration purposes only to show packets.
            print("Base64 encoded representation of the received packet: ", base64.encodebytes(rcv_bytes))
            print("Decoded data: ", decoded_text)

            # Encode returning text and check to ensure successful result.
            (encoded_return, encoder_status) = encoder.encode(decoded_text)
            if encoder_status != MteStatus.mte_status_success:
                print("Error encoding: Status: ({0}): {1}".format(
                    MteBase.get_status_name(encoder_status),
                    MteBase.get_status_description(encoder_status)),
                    file=sys.stderr)
                connection.shutdown(socket.SHUT_RDWR)
                connection.close()
                print("Socket server closed due to encoding error.")
                return

            #
            # This puts the bytes of the send length.
            to_send_len = len(encoded_return)

            # Big Endian the packet length
            to_send_len = struct.pack('>I', to_send_len)

            #
            # For demonstration purposes only to show packets.
            print("Base64 encoded representation of the packet being sent: ", base64.encodebytes(encoded_return))

            # Send the length of the message.
            connection.sendall(bytes(to_send_len))

            # Send the actual message.
            connection.sendall(encoded_return)

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

# Step 7 Create Decoder.
# Creates the MTE Decoder.
def create_decoder():
    global decoder
    
    # Set MTE values for the Decoder.
    decoder.set_entropy(entropy)
    decoder.set_nonce(decoder_nonce)

    # Instantiate the MTE Decoder.
    decoder_status = decoder.instantiate(identifier)
    if decoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE decoder ({0}): {1}".format(
            MteBase.get_status_name(decoder_status),
            MteBase.get_status_description(decoder_status)),
            file=sys.stderr)
        quit()

# Step 7 Create Encoder.
# Creates the MTE Encoder.
def create_encoder():
    global encoder
    
    # Set MTE values for the Encoder.
    encoder.set_entropy(entropy)
    encoder.set_nonce(encoder_nonce)

    # Instantiate the MTE Encoder.
    encoder_status = encoder.instantiate(identifier)
    if encoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE encoder ({0}): {1}".format(
            MteBase.get_status_name(encoder_status),
            MteBase.get_status_description(encoder_status)),
            file=sys.stderr)
        quit()

# Get MTE version and type string
def get_mte_version():
    global encoder
    s = MteBase.get_version() + "-"
    if type(encoder).__name__ == "MteEnc":
        s += "Core"
    elif type(encoder).__name__ == "MteMkeEnc":
        s += "MKE"
    elif type(encoder).__name__ == "MteFlenEnc":
        s += "FLEN"
    return s
        
main()
