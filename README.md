

<img src="Eclypses.png" style="width:50%;margin-right:0;"/>

<div align="center" style="font-size:40pt; font-weight:900; font-family:arial; margin-top:300px; " >
Python Socket Tutorial</div>

<div align="center" style="font-size:28pt; font-family:arial; " >
MTE Implementation Tutorial (MTE Core, MKE, MTE Fixed Length) </div>
<div align="center" style="font-size:15pt; font-family:arial; " >
Using MTE version 3.0.x</div>





[Introduction](#introduction)

[Socket Tutorial Server and Client](#socket-tutorial-server-and-client)


<div style="page-break-after: always; break-after: page;"></div>

# Introduction


This tutorial is sending messages via a socket connection. This is only a sample, the MTE does NOT require the usage of sockets, you can use whatever communication protocol that is needed.

This tutorial demonstrates how to use Mte Core, Mte MKE and Mte Fixed Length. Depending on what your needs are, these three different implementations can be used in the same application OR you can use any one of them. They are not dependent on each other and can run simultaneously in the same application if needed.

The SDK that you received from Eclypses may not include the MKE or MTE FLEN add-ons. If your SDK contains either the MKE or the Fixed Length add-ons, the name of the SDK will contain "-MKE" or "-FLEN". If these add-ons are not there and you need them please work with your sales associate. If there is no need, please just ignore the MKE and FLEN options.

Here is a short explanation of when to use each, but it is encouraged to either speak to a sales associate or read the dev guide if you have additional concerns or questions.

***MTE Core:*** This is the recommended version of the MTE to use. Unless payloads are large or sequencing is needed this is the recommended version of the MTE and the most secure.

***MTE MKE:*** This version of the MTE is recommended when payloads are very large, the MTE Core would, depending on the token byte size, be multiple times larger than the original payload. Because this uses the MTE technology on encryption keys and encrypts the payload, the payload is only enlarged minimally.

***MTE Fixed Length:*** This version of the MTE is very secure and is used when the resulting payload is desired to be the same size for every transmission. The Fixed Length add-on is mainly used when using the sequencing verifier with MTE. In order to skip dropped packets or handle asynchronous packets the sequencing verifier requires that all packets be a predictable size. If you do not wish to handle this with your application then the Fixed Length add-on is a great choice. This is ONLY an encoder change - the decoder that is used is the MTE Core decoder.

In this tutorial we are creating an MTE Encoder and an MTE Decoder in the server as well as the client because we are sending secured messages in both directions. This is only needed when there are secured messages being sent from both sides, the server as well as the client. If only one side of your application is sending secured messages, then the side that sends the secured messages should have an Encoder and the side receiving the messages needs only a Decoder.

These steps should be followed on the server side as well as on the client side of the program.

**IMPORTANT**
>Please note the solution provided in this tutorial does NOT include the MTE library or supporting MTE library files. If you have NOT been provided an MTE library and supporting files, please contact Eclypses Inc. The solution will only work AFTER the MTE library and MTE library files have been incorporated.
  

# Socket Tutorial Server and Client

<ol>
<li>Add the contents of the  “src/py” directory from the mte-Windows, mte-Darwin (macOS), or mte-Linux package to both the SocketClient and SocketServer directories.</li>
<br>
<li>Add the mte.dll (if using windows from the mte-Windows package), libmte.dylib (if using macOS from the mte-Darwin package), or libmte.so (if using Linux from the mte-Linux package) to the SocketClient AND SocketServer directories. </li>


<br>
<li>Add the relavent import statements to both SocketClient.py (in the SocketClient directory) and SocketServer.py (in the SocketServer directory).</li>

```python
# ------------------------------------------
# Uncomment the following two imports to use
# the MTE Core.
# ------------------------------------------
from MteEnc import MteEnc
from MteDec import MteDec
# ------------------------------------------
# Uncomment the following two imports to use
# the MMK addon-on.
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
```

<li>Create the MTE Decoder and MTE Encoder as well as the accompanying MTE status for each.</li>


```python
#--------------------------------------------
# The fixed length, only needed for MTE FLEN
#--------------------------------------------
fixed_bytes = 8

#----------------------------------------------------------
# Create the MTE decoder, uncomment to use MTE core OR FLEN
# Create the Mte Fixed length decoder (SAME as MTE Core)
#----------------------------------------------------------
decoder = MteDec.fromdefault()
#---------------------------------------------------
# Create the Mte MKE decoder, uncomment to use MKE
#---------------------------------------------------
#decoder = MteMkeDec.fromdefault()
decoder_status = MteStatus.mte_status_success

#---------------------------------------------------
# Create the Mte encoder, uncomment to use MTE core
#---------------------------------------------------
encoder = MteEnc.fromdefault()
#---------------------------------------------------
# Create the Mte MKE encoder, uncomment to use MKE
#---------------------------------------------------
#encoder = MteMkeEnc.fromdefault()
#---------------------------------------------------------------
# Create the Mte Fixed length encoder, uncomment to use MTE FLEN
#---------------------------------------------------------------
#encoder = MteFlenEnc.fromdefault(fixed_bytes)
encoder_status = MteStatus.mte_status_success

```


<li>Next, we need to be able to set the entropy, nonce, and personalization/identification values.</li>
These values should be treated like encryption keys and never exposed. For demonstration purposes in the tutorial we are setting these values in the code. In a production environment these values should be protected and not available to outside sources. For the entropy, we have to determine the size of the allowed entropy value based on the drbg we have selected. A code sample below is included to demonstrate how to get these values.

To set the entropy in the tutorial we are simply getting the minimum bytes required and creating a byte array of that length that contains all zeros.
```python
entropy_min_bytes = MteBase.get_drbgs_entropy_min_bytes(drbgs)
```

```python
# Check how long entropy we need and change if we need more, set default entropy to 0's
entropy = bytes(entropy_min_bytes)
```
To set the nonce and the personalization/identifier string we are simply adding our default values as global variables.
```python
encoder_nonce = 0

# OPTIONAL!!! adding 1 to decoder nonce so return value changes (the nonce can be used for encoder and decoder)
# on client side values will be switched so they match up encoder to decoder and vice versa 
decoder_nonce = 1
identifier = "demo"
```

<li>To ensure the MTE library is licensed correctly, run the license check. To ensure the DRBG is set up correctly, run the DRBGS self test. The LicenseCompanyName, and LicenseKey below should be replaced with your company’s MTE license information provided by Eclypses. If a trial version of the MTE is being used any value can be passed into those fields and it will work.</li>

```python


# Check mte license
# Initialize MTE license. If a license code is not required (e.g., trial mode), this can be skipped.
if not MteBase.init_license("LicenseCompanyName", "LicenseKey"):
    encoder_status = MteStatus.mte_status_license_error
    print("License init error ({0}): {1}.".format(
        MteBase.get_status_name(encoder_status),
        MteBase.get_status_description(encoder_status)),
        file=sys.stderr)
    return encoder_status.value
```

<li>Create MTE Decoder Instances and MTE Encoder Instances in a small number of functions.</li>

Here is a sample function that creates the MTE Decoder.

```python
def create_decoder():
    global decoder
   
    # Set MTE values for the Decoder.
    decoder.set_entropy(entropy)
    decoder.set_nonce(decoder_nonce)

    # Instantiate the MTE decoder.
    decoder_status = decoder.instantiate(identifier)
    if decoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE decoder ({0}): {1}".format(
                MteBase.get_status_name(decoder_status),
                MteBase.get_status_description(decoder_status)),
                file=sys.stderr)
        quit()
```
*(For further information on Decoder constructor review the DevelopersGuide)*

Here is a sample function that creates the MTE Encoder.

```python
def create_encoder():
    global encoder
    
    # Set MTE values for the Encoder.
    encoder.set_entropy(entropy)
    encoder.set_nonce(encoder_nonce)

    # Instantiate the MTE Encoder.
    encoder_status = encoder.instantiate(identifier)
    if encoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE Encoder ({0}): {1}".format(
                MteBase.get_status_name(encoder_status),
                MteBase.get_status_description(encoder_status)),
                file=sys.stderr)
        quit()

```
*(For further information on Encoder constructor review the DevelopersGuide)*

Instantiate the MTE Decoder and MTE Encoder by calling that function at the start of your main function:

```python
create_decoder()
create_encoder()
```
<li>Finally, we need to add the MTE calls to encode and decode the messages that we are sending and receiving from the other side. (Ensure on the client side the Encoder is used to encode the outgoing text, then the Decoder is used to decode the incoming response.)</li>

<br>
Here is a sample of how to do this on the Client Side.

```python
# 
# Encode text to send and check for successful result.
(encoded_bytes, encoder_status) = encoder.encode(text_to_send)
if encoder_status != MteStatus.mte_status_success:
  # Throw an error here.
  print("Error encoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(encoder_status),
    MteBase.get_status_description(encoder_status)),
    file=sys.stderr)

  
# 
# Decode incoming message and check to ensure successful result.
(returned_text, decoder_status) = decoder.decode(bytes(rcv_bytes))
if decoder_status != MteStatus.mte_status_success:
  # Throw an error here.
  print("Error decoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(decoder_status),
    MteBase.get_status_description(decoder_status)),
    file=sys.stderr)
```
<br>
Here is a sample of how to do this on the Server Side.

```python
# 
# Decode received bytes and check to ensure successful result.
(decoded_text, decoder_status) = decoder.decode(bytes(rcv_bytes))
if decoder_status != MteStatus.mte_status_success:
  # Throw an error here.
  print("Error decoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(decoder_status),
    MteBase.get_status_description(decoder_status)),
    file=sys.stderr)

# 
# Encode returning text and check to ensure successful result.
(encoded_return, encoder_status) = encoder.encode(decoded_text)
if encoder_status != MteStatus.mte_status_success:
  # Throw an error here.
  print("Error encoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(encoder_status),
    MteBase.get_status_description(encoder_status)),
    file=sys.stderr)
```
</ol>

***The Server side and the Client side of the MTE Sockets tutorial should now be ready for use on your device.***


<div style="page-break-after: always; break-after: page;"></div>

# Contact Eclypses

<img src="Eclypses.png" style="width:8in;"/>

<p align="center" style="font-weight: bold; font-size: 22pt;">For more information, please contact:</p>
<p align="center" style="font-weight: bold; font-size: 22pt;"><a href="mailto:info@eclypses.com">info@eclypses.com</a></p>
<p align="center" style="font-weight: bold; font-size: 22pt;"><a href="https://www.eclypses.com">www.eclypses.com</a></p>
<p align="center" style="font-weight: bold; font-size: 22pt;">+1.719.323.6680</p>

<p style="font-size: 8pt; margin-bottom: 0; margin: 300px 24px 30px 24px; " >
<b>All trademarks of Eclypses Inc.</b> may not be used without Eclypses Inc.'s prior written consent. No license for any use thereof has been granted without express written consent. Any unauthorized use thereof may violate copyright laws, trademark laws, privacy and publicity laws and communications regulations and statutes. The names, images and likeness of the Eclypses logo, along with all representations thereof, are valuable intellectual property assets of Eclypses, Inc. Accordingly, no party or parties, without the prior written consent of Eclypses, Inc., (which may be withheld in Eclypses' sole discretion), use or permit the use of any of the Eclypses trademarked names or logos of Eclypses, Inc. for any purpose other than as part of the address for the Premises, or use or permit the use of, for any purpose whatsoever, any image or rendering of, or any design based on, the exterior appearance or profile of the Eclypses trademarks and or logo(s).
</p>
This tutorial is sending messages via a socket connection. This is only a sample, the MTE does NOT require the usage of sockets, you can use whatever communication protocol that is needed.

This tutorial demonstrates how to use Mte Core, Mte MKE and Mte Fixed Length. Depending on what your needs are, these three different implementations can be used in the same application OR you can use any one of them. They are not dependent on each other and can run simultaneously in the same application if needed.

The SDK that you received from Eclypses may not include the MKE or MTE FLEN add-ons. If your SDK contains either the MKE or the Fixed Length add-ons, the name of the SDK will contain "-MKE" or "-FLEN". If these add-ons are not there and you need them please work with your sales associate. If there is no need, please just ignore the MKE and FLEN options.

Here is a short explanation of when to use each, but it is encouraged to either speak to a sales associate or read the dev guide if you have additional concerns or questions.

***MTE Core:*** This is the recommended version of the MTE to use. Unless payloads are large or sequencing is needed this is the recommended version of the MTE and the most secure.

***MTE MKE:*** This version of the MTE is recommended when payloads are very large, the MTE Core would, depending on the token byte size, be multiple times larger than the original payload. Because this uses the MTE technology on encryption keys and encrypts the payload, the payload is only enlarged minimally.

***MTE Fixed Length:*** This version of the MTE is very secure and is used when the resulting payload is desired to be the same size for every transmission. The Fixed Length add-on is mainly used when using the sequencing verifier with MTE. In order to skip dropped packets or handle asynchronous packets the sequencing verifier requires that all packets be a predictable size. If you do not wish to handle this with your application then the Fixed Length add-on is a great choice. This is ONLY an encoder change - the decoder that is used is the MTE Core decoder.

In this tutorial we are creating an MTE Encoder and an MTE Decoder in the server as well as the client because we are sending secured messages in both directions. This is only needed when there are secured messages being sent from both sides, the server as well as the client. If only one side of your application is sending secured messages, then the side that sends the secured messages should have an Encoder and the side receiving the messages needs only a Decoder.

These steps should be followed on the server side as well as on the client side of the program.

**IMPORTANT**
>Please note the solution provided in this tutorial does NOT include the MTE library or supporting MTE library files. If you have NOT been provided an MTE library and supporting files, please contact Eclypses Inc. The solution will only work AFTER the MTE library and MTE library files have been incorporated.
  

# Socket Tutorial Server and Client

<ol>
<li>Add the contents of the  “src/py” directory from the mte-Windows, mte-Darwin (macOS), or mte-Linux package to both the SocketClient and SocketServer directories.</li>
<br>
<li>Add the mte.dll (if using windows from the mte-Windows package), libmte.dylib (if using macOS from the mte-Darwin package), or libmte.so (if using Linux from the mte-Linux package) to the SocketClient AND SocketServer directories. </li>


<br>
<li>Add the relavent import statements to both SocketClient.py (in the SocketClient directory) and SocketServer.py (in the SocketServer directory).</li>

```python
# ------------------------------------------
# Uncomment the following two imports to use
# the MTE Core.
# ------------------------------------------
from MteEnc import MteEnc
from MteDec import MteDec
# ------------------------------------------
# Uncomment the following two imports to use
# the MMK addon-on.
# ------------------------------------------
#from MteMkeEnc import MteMkeEnc
#from MteMkeDec import MteMkeDec
# ------------------------------------------
# Uncomment the following two imports to use
# the fixed length add-on.
# ------------------------------------------
#from MteFlenEnc import MteFlenEnc
#from MteDec import MteDec

from MteDrbgs import MteDrbgs
from MteVerifiers import MteVerifiers
from MteStatus import MteStatus
from MteBase import MteBase
```

<li>Create the MTE Decoder and MTE Encoder as well as the accompanying MTE status for each.</li>


```python
#--------------------------------------------
# The fixed length, only needed for MTE FLEN
#--------------------------------------------
fixed_bytes = 8

#----------------------------------------------------------
# Create the MTE decoder, uncomment to use MTE core OR FLEN
# Create the Mte Fixed length decoder (SAME as MTE Core)
#----------------------------------------------------------
decoder = MteDec.fromdefault()
#---------------------------------------------------
# Create the Mte MKE decoder, uncomment to use MKE
#---------------------------------------------------
#decoder = MteMkeDec.fromdefault()
decoder_status = MteStatus.mte_status_success

#---------------------------------------------------
# Create the Mte encoder, uncomment to use MTE core
#---------------------------------------------------
encoder = MteEnc.fromdefault()
#---------------------------------------------------
# Create the Mte MKE encoder, uncomment to use MKE
#---------------------------------------------------
#encoder = MteMkeEnc.fromdefault()
#---------------------------------------------------------------
# Create the Mte Fixed length encoder, uncomment to use MTE FLEN
#---------------------------------------------------------------
#encoder = MteFlenEnc.fromdefault(fixed_bytes)
encoder_status = MteStatus.mte_status_success

```


<li>Next, we need to be able to set the entropy, nonce, and personalization/identification values.</li>
These values should be treated like encryption keys and never exposed. For demonstration purposes in the tutorial we are setting these values in the code. In a production environment these values should be protected and not available to outside sources. For the entropy, we have to determine the size of the allowed entropy value based on the drbg we have selected. A code sample below is included to demonstrate how to get these values.

To set the entropy in the tutorial we are simply getting the minimum bytes required and creating a byte array of that length that contains all zeros.
```python
entropy_min_bytes = MteBase.get_drbgs_entropy_min_bytes(drbgs)
```

```python
# Check how long entropy we need and change if we need more, set default entropy to 0's
entropy = bytes(entropy_min_bytes)
```
To set the nonce and the personalization/identifier string we are simply adding our default values as global variables.
```python
encoder_nonce = 0

# OPTIONAL!!! adding 1 to decoder nonce so return value changes (the nonce can be used for encoder and decoder)
# on client side values will be switched so they match up encoder to decoder and vice versa 
decoder_nonce = 1
identifier = "demo"
```

<li>To ensure the MTE library is licensed correctly, run the license check. To ensure the DRBG is set up correctly, run the DRBGS self test. The LicenseCompanyName, and LicenseKey below should be replaced with your company’s MTE license information provided by Eclypses. If a trial version of the MTE is being used any value can be passed into those fields and it will work.</li>

```python

#
# Check mte license
# Initialize MTE license. If a license code is not required (e.g., trial mode), this can be skipped. 
if not MteBase.init_license("LicenseCompanyName", "LicenseKey"):
        encoder_status = MteStatus.mte_status_license_error
        print("License init error ({0}): {1}. Press ENTER to end.".format(
                                MteBase.get_status_name(encoder_status),
                                MteBase.get_status_description(encoder_status)),
                                file=sys.stderr)
        input()
        return encoder_status.value
		
```

<li>Create MTE Decoder Instances and MTE Encoder Instances in a small number of functions.</li>

Here is a sample function that creates the MTE Decoder.

```python
def create_decoder():
    global decoder
   
    # Set MTE values for the decoder.
    decoder.set_entropy(entropy)
    decoder.set_nonce(decoder_nonce)

    # Instantiate the MTE decoder.
    decoder_status = decoder.instantiate(identifier)
    if decoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE decoder ({0}): {1}".format(
                MteBase.get_status_name(decoder_status),
                MteBase.get_status_description(decoder_status)),
                file=sys.stderr)
        quit()
```
*(For further information on Decoder constructor review the DevelopersGuide)*

Here is a sample function that creates the MTE Encoder.

```python
def create_encoder():
    global encoder
    
    # Set MTE values for the encoder.
    encoder.set_entropy(entropy)
    encoder.set_nonce(encoder_nonce)

    # Instantiate the MTE encoder.
    encoder_status = encoder.instantiate(identifier)
    if encoder_status != MteStatus.mte_status_success:
        print("Failed to initialize the MTE encoder ({0}): {1}".format(
                MteBase.get_status_name(encoder_status),
                MteBase.get_status_description(encoder_status)),
                file=sys.stderr)
        quit()

```
*(For further information on Encoder constructor review the DevelopersGuide)*

Instantiate the MTE Decoder and MTE Encoder by calling that function at the start of your main function:

```python
create_decoder()
create_encoder()
```
<li>Finally, we need to add the MTE calls to encode and decode the messages that we are sending and receiving from the other side. (Ensure on the client side the Encoder is used to encode the outgoing text, then the Decoder is used to decode the incoming response.)</li>

<br>
Here is a sample of how to do this on the Client Side.

```python
# 
# Encode text to send and check for successful result.
(encoded_bytes, encoder_status) = encoder.encode(text_to_send)
if encoder_status != MteStatus.mte_status_success:
    # Throw an error here.
    print("Error encoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(encoder_status),
    MteBase.get_status_description(encoder_status)),
    file=sys.stderr)

  
# 
# Decode incoming message and check for non-error response.
# When checking the status on decode use "status_is_error".
# Only checking if status is success can be misleading, there may be a
# warning returned that the user can ignore.
# See MTE Documentation for more details.
(returned_text, decoder_status) = decoder.decode(bytes(rcv_bytes))
if decoder.status_is_error(decoder_status):
    print("Error decoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(decoder_status),
    MteBase.get_status_description(decoder_status)),
    file=sys.stderr)
    sock.shutdown(socket.SHUT_RDWR)
    sock.close()
    print("Socket client closed due to decoding error.")
    return
```
<br>
Here is a sample of how to do this on the Server Side.

```python
# 
# Decode incoming message and check for non-error response.
# When checking the status on decode use "status_is_error".
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
# Encode returning text and check to ensure successful result.
(encoded_return, encoder_status) = encoder.encode(decoded_text)
if encoder_status != MteStatus.mte_status_success:
  # Throw an error here.
  print("Error encoding: Status: ({0}): {1}".format(
    MteBase.get_status_name(encoder_status),
    MteBase.get_status_description(encoder_status)),
    file=sys.stderr)
```
</ol>

***The Server side and the Client side of the MTE Sockets tutorial should now be ready for use on your device.***


<div style="page-break-after: always; break-after: page;"></div>

# Contact Eclypses

<img src="Eclypses.png" style="width:8in;"/>

<p align="center" style="font-weight: bold; font-size: 22pt;">For more information, please contact:</p>
<p align="center" style="font-weight: bold; font-size: 22pt;"><a href="mailto:info@eclypses.com">info@eclypses.com</a></p>
<p align="center" style="font-weight: bold; font-size: 22pt;"><a href="https://www.eclypses.com">www.eclypses.com</a></p>
<p align="center" style="font-weight: bold; font-size: 22pt;">+1.719.323.6680</p>

<p style="font-size: 8pt; margin-bottom: 0; margin: 300px 24px 30px 24px; " >
<b>All trademarks of Eclypses Inc.</b> may not be used without Eclypses Inc.'s prior written consent. No license for any use thereof has been granted without express written consent. Any unauthorized use thereof may violate copyright laws, trademark laws, privacy and publicity laws and communications regulations and statutes. The names, images and likeness of the Eclypses logo, along with all representations thereof, are valuable intellectual property assets of Eclypses, Inc. Accordingly, no party or parties, without the prior written consent of Eclypses, Inc., (which may be withheld in Eclypses' sole discretion), use or permit the use of any of the Eclypses trademarked names or logos of Eclypses, Inc. for any purpose other than as part of the address for the Premises, or use or permit the use of, for any purpose whatsoever, any image or rendering of, or any design based on, the exterior appearance or profile of the Eclypses trademarks and or logo(s).
</p>
