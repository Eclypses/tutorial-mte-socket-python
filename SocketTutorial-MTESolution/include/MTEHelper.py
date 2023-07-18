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
import EcdhP256
from dataclasses import dataclass

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

def getPublicKey(ecdhInst):
        pub_key = bytearray(EcdhP256.SzPublicKey)
        res = ecdhInst.create_keypair(pub_key)
        if res < 0:
            return res
        return pub_key
    
class MTEHelper():
    @dataclass
    class encoderInfo:
        ecdhManager = EcdhP256.EcdhP256()
        personal = None
        public_key = getPublicKey(ecdhManager)
        peer_public = None
        nonce = None
    @dataclass
    class decoderInfo:
        ecdhManager = EcdhP256.EcdhP256()
        personal = None
        public_key = getPublicKey(ecdhManager)
        peer_public = None
        nonce = None

    def __init__(self):
        #--------------------------------------------
        # The fixed length, only needed for MTE FLEN
        #--------------------------------------------
        self.fixed_bytes = 8

        #----------------------------------------------------------
        # Create the MTE Decoder and MTE Encoder, uncomment to use MTE core OR FLEN
        #----------------------------------------------------------
        self.decoder = MteDec.fromdefault()
        self.encoder = MteEnc.fromdefault()
        #---------------------------------------------------
        # Create the Mte MKE Decoder and MKE Decoder, uncomment to use MKE
        #---------------------------------------------------
        #decoder = MteMkeDec.fromdefault()
        #encoder = MteMkeEnc.fromdefault()
        #---------------------------------------------------------------
        # Create the Mte Fixed length Encoder, uncomment to use MTE FLEN
        #---------------------------------------------------------------
        #encoder = MteFlenEnc.fromdefault(fixed_bytes)

        self.encoder_status = MteStatus.mte_status_success
        #decoder_status = MteStatus.mte_status_success

    def initMte(self):
      # Initialize MTE license. If a license code is not required (e.g., trial mode), this can be skipped.
        if not MteBase.init_license("LicenseCompanyName", "LicenseKey"):
            self.encoder_status = MteStatus.mte_status_license_error
            print("License init error ({0}): {1}.".format(
                MteBase.get_status_name(self.encoder_status),
                MteBase.get_status_description(self.encoder_status)),
                file=sys.stderr)
            return self.encoder_status.value

        return self.encoder_status.value

    def create_encoder(self):
        # Print MTE and ECDH values
        print("\nNonce: " + str(self.encoderInfo.nonce))
        print("Personal: " + str(self.encoderInfo.personal))
        print("Public Key: " + str(self.encoderInfo.public_key))
        print("Peer Public Key: " + str(self.encoderInfo.peer_public) + "\n")
        
        # Set MTE values for the Encoder.
        secret = bytearray(EcdhP256.SzSecretData)
        ret = self.encoderInfo.ecdhManager.get_shared_secret(self.encoderInfo.peer_public,secret)
        if ret != 0:
            print("Failure to get Shared Secret")
            print("Error Code: " + str(ret))
            quit()
        self.encoder.set_entropy(secret)
        self.encoder.set_nonce(self.encoderInfo.nonce)

        # Instantiate the MTE Encoder.
        encoder_status = self.encoder.instantiate(self.encoderInfo.personal)
        if encoder_status != MteStatus.mte_status_success:
            print("Failed to initialize the MTE Encoder ({0}): {1}".format(
                MteBase.get_status_name(encoder_status),
                MteBase.get_status_description(encoder_status)),
                file=sys.stderr)
            quit()

    def create_decoder(self):
        # Print MTE and ECDH values
        print("\nNonce: " + str(self.decoderInfo.nonce))
        print("Personal: " + str(self.decoderInfo.personal))
        print("Public Key: " + str(self.decoderInfo.public_key))
        print("Peer Public Key: " + str(self.decoderInfo.peer_public) + "\n")
        
        # Set MTE values for the Decoder.
        secret = bytearray(EcdhP256.SzSecretData)
        ret = self.decoderInfo.ecdhManager.get_shared_secret(self.decoderInfo.peer_public,secret)
        if ret != 0:
            print("Failure to get Shared Secret")
            print("Error Code: " + str(ret))
            quit()
        self.decoder.set_entropy(secret)
        self.decoder.set_nonce(self.decoderInfo.nonce)

        # Instantiate the MTE decoder.
        decoder_status = self.decoder.instantiate(self.decoderInfo.personal)
        if decoder_status != MteStatus.mte_status_success:
            print("Failed to initialize the MTE decoder ({0}): {1}".format(
                MteBase.get_status_name(decoder_status),
                MteBase.get_status_description(decoder_status)),
                file=sys.stderr)
            quit()

    def encode_message(self,message):
        # Encode text to send and check for successful result.
        (encoded_bytes, encoder_status) = self.encoder.encode(message)
        if encoder_status != MteStatus.mte_status_success:
            print("Error encoding: Status: ({0}): {1}".format(
                MteBase.get_status_name(encoder_status),
                MteBase.get_status_description(encoder_status)),
                file=sys.stderr)
            return ("Failed",False)

        return (encoded_bytes, True)

    def decode_message(self, encoded):
        # Decode incoming message and check for non-error response.
        # When checking the status on decode use "status_is_error".
        # Only checking if status is success can be misleading, there may be a
        # warning returned that the user can ignore.
        # See MTE Documentation for more details.
        (returned_text, decoder_status) = self.decoder.decode(encoded)
        if self.decoder.status_is_error(decoder_status):
            print("Error decoding: Status: ({0}): {1}".format(
            MteBase.get_status_name(decoder_status),
            MteBase.get_status_description(decoder_status)),
            file=sys.stderr)
            return ("Failed",False)

        return (returned_text,True)

    # Get MTE version and type string
    def get_mte_version(self,encoder):
        s = MteBase.get_version() + "-"
        if type(self.encoder).__name__ == "MteEnc":
            s += "Core"
        elif type(self.encoder).__name__ == "MteMkeEnc":
            s += "MKE"
        elif type(self.encoder).__name__ == "MteFlenEnc":
            s += "FLEN"
        return s
    
    def exchangeServerMteInfo(self,sock):
        # The client Encoder and the server Decoder will be paired.
        # The client Decoder and the server Encoder will be paired.

        # Processing incoming messages, all 4 will be needed.
        recvCount = 0

        # Loop until all 4 data are received from client, can be in any order.
        while (recvCount < 4):
            # Receive the next message from the client.
            (recvData,header) = sock.listen_socket(sock.connection);

            # Evaluate the header.
            # 1 - server Decoder public key (from client Encoder)
            # 2 - server Decoder personalization string (from client Encoder)
            # 3 - server Encoder public key (from client Decoder)
            # 4 - server Encoder personalization string (from client Decoder)
            match (header):
                case '1':
                    if self.decoderInfo.peer_public == None:
                        recvCount += 1
                    self.decoderInfo.peer_public = recvData
                case '2':
                    if self.decoderInfo.personal == None:
                        recvCount += 1
                    self.decoderInfo.personal = bytes(recvData)
                case '3':
                    if self.encoderInfo.peer_public == None:
                        recvCount += 1
                    self.encoderInfo.peer_public = recvData
                case '4':
                    if self.encoderInfo.personal == None:
                        recvCount += 1
                    self.encoderInfo.personal = bytes(recvData)
                case _:
                    # Unknown message, abort here, send an ‘E’ for error.
                    sock.send_message(sock.connection,'E', bytes("ERR",encoding='utf8'))
                    return False

        # Now all values from client have been received, send an 'A' for acknowledge to client.
        sock.send_message(sock.connection,'A', bytes("ACK",encoding='utf8'))

        #Prepare to send server information now.

        # Create nonces.
        minNonceBytes = MteBase.get_drbgs_nonce_min_bytes(self.encoder.get_drbg())
        if minNonceBytes == 0:
            minNonceBytes = 1

        serverEncoderNonce = bytearray(minNonceBytes)

        res = self.encoderInfo.ecdhManager.get_random(serverEncoderNonce);
        if res < 0:
            return False

        self.encoderInfo.nonce = serverEncoderNonce

        serverDecoderNonce = bytearray(minNonceBytes)

        res = self.decoderInfo.ecdhManager.get_random(serverDecoderNonce);
        if res < 0:
            return False

        self.decoderInfo.nonce = serverDecoderNonce
        
        #Send out information to the client.
        #1 - server Encoder public key (to client Decoder)
        #2 - server Encoder nonce (to client Decoder)
        #3 - server Decoder public key (to client Encoder)
        #4 - server Decoder nonce (to client Encoder)
        sock.send_message(sock.connection,'1', self.encoderInfo.public_key)
        sock.send_message(sock.connection,'2', self.encoderInfo.nonce)
        sock.send_message(sock.connection,'3', self.decoderInfo.public_key)
        sock.send_message(sock.connection,'4', self.decoderInfo.nonce)

        #Wait for ack from client.
        (recvData,header) = sock.listen_socket(sock.connection)
        if header != 'A':
            return False
        
        return True
    
    def exchangeClientMteInfo(self,sock):
        # The client Encoder and the server Decoder will be paired.
        # The client Decoder and the server Encoder will be paired.

        # Prepare to send client information.
        
        # Create personalization strings.
        clientEncoderPersonal = uuid.uuid4()
        self.encoderInfo.personal = bytes(str(clientEncoderPersonal),encoding='utf8')
        clientDecoderPersonal = uuid.uuid4()
        self.decoderInfo.personal = bytes(str(clientDecoderPersonal),encoding='utf8')

        # Send out information to the server.
        # 1 - client Encoder public key (to server Decoder)
        # 2 - client Encoder personalization string (to server Decoder)
        # 3 - client Decoder public key (to server Encoder)
        # 4 - client Decoder personalization string (to server Encoder)
        
        sock.send_message(sock.sock,'1', self.encoderInfo.public_key)
        sock.send_message(sock.sock,'2', self.encoderInfo.personal)
        sock.send_message(sock.sock,'3', self.decoderInfo.public_key)
        sock.send_message(sock.sock,'4', self.decoderInfo.personal)

        # Wait for ack from server.
        (recvData,header) = sock.listen_socket(sock.sock);
        if header != 'A':
            return False

        #Processing incoming messages, all 4 will be needed.
        recvCount = 0

        #Loop until all 4 data are received from server, can be in any order.
        while recvCount < 4:
            #Receive the next message from the server.
            (recvData,header) = sock.listen_socket(sock.sock);

            #Evaluate the header.
            #1 - client Decoder public key (from server Encoder)
            #2 - client Decoder nonce (from server Encoder)
            #3 - client Encoder public key (from server Decoder)
            #4 - client Encoder nonce (from server Decoder)
            match (header):
                case '1':
                    if self.decoderInfo.peer_public == None:
                        recvCount+=1
                    self.decoderInfo.peer_public = recvData
                case '2':
                    if self.decoderInfo.nonce == None:
                        recvCount+=1
                    self.decoderInfo.nonce = recvData
                case '3':
                    if self.encoderInfo.peer_public == None:
                        recvCount+=1
                    self.encoderInfo.peer_public = recvData
                case '4':
                    if self.encoderInfo.nonce == None:
                        recvCount+=1
                    self.encoderInfo.nonce = recvData
                case _:
                    sock.send_message(sock.connection,'E', bytes("ERR",encoding='utf8'))
                    return False

        #Now all values from server have been received, send an 'A' for acknowledge to server.
        sock.send_message(sock.sock,'A', bytes("ACK",encoding='utf8'))

        return True
