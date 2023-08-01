
import digitalio
import board
import busio
import adafruit_rfm9x
import json
import numpy as np
import random
import pypuf.io
import pypuf.simulation
import time
import hashlib


RADIO_FREQ_MHZ = 433.0
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

rfm9x.tx_power = 23
rfm9x.ack_delay = 0.2  # 200 ms delay
rfm9x.ack_retries = 10
rfm9x.ack_wait = 2.0  # 2 seconds

puf_BITS = 64
puf_SEED = 1
puf_SETS = 8

def send_message(key, value):
    print(f"Sending {key} from Key to Car...")
    if isinstance(value, str):
        value = value.encode('utf-8')
    rfm9x.send_with_ack(value)
    print(f"{key} has been sent")

def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    packets = []
    while True:
        packet = rfm9x.receive(timeout=5)
        if packet is None:
            print("Timeout! No response received.")
            return None
        packets.append(packet)
        if len(packet) < 252:  # The last packet will be shorter
            break
    data = b"".join(packets)
    print(f"Received {key}")
    return data

with open('data.txt', 'r') as f:
    register_output = {}
    for line in f:
        key, value = line.strip().split(': ')
        register_output[key] = value
        
#Initialize socket
Ks = register_output['Ks'] #type: string
key_id = register_output['key_id'] #type: string
Ks_ndarray = np.array([int(c) for c in Ks], dtype= np.int8) #type: string-> numpy array

"""
Generate & XOR Ni
"""
Ni = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS) #type: string

Ni_ndarray = np.array([int(c) for c in Ni], dtype= np.int8) #type: string-> numpy array

Ni_encrypted = Ks_ndarray ^ Ni_ndarray #type: numpy array

"""
#Send MA1
"""
send_message('ID',key_id)
send_message('Encrypted Ni',Ni_encrypted.tobytes())

# Receive MA2
A0_hex_dig = receive_message("A0")
Nc_encrypted = receive_message("Encrypted Nc")
challenge_encrypted = receive_message("Encrypted Challenge")
challenge_new_encrypted = receive_message("Encrypted Challenge New")

# Print the sizes of the received data
print("Size of A0:", len(A0_hex_dig))
print("Size of Nc_encrypted:", len(Nc_encrypted))
print("Size of challenge_encrypted:", len(challenge_encrypted))
print("Size of challenge_new_encrypted:", len(challenge_new_encrypted))

"""
#Decode Nc
"""
Nc_encrypted = np.frombuffer(Nc_encrypted, dtype=np.int8).reshape(puf_BITS) # byte-> numpy array

Nc = Nc_encrypted ^ Ks_ndarray # decode(XOR)

Nc = np.array2string(Nc, separator='', prefix='', suffix='')[1:-1] # remove brackets and whitespace, type: numpy array-> string


"""
Verify A0
"""

A0_hex_dig = A0_hex_dig.decode('utf-8')
#pritn(A0)
A0_verified = key_id + Ni + Ks + Nc

A0_verified_hash_object = hashlib.sha256(A0_verified.encode('utf-8'))

A0_verified_hex_dig = A0_verified_hash_object.hexdigest()

"""
How to verified? Cannot verified by hash the same value, since the output changes every time
"""
if(A0_hex_dig == A0_verified_hex_dig):
    print("yes")
else:
    print('NO')


"""
Decode Challenge & Challenge_new
"""


challenge_encrypted = np.frombuffer(challenge_encrypted, dtype=np.int8).reshape(puf_SETS, puf_BITS) # byte-> numpy array

challenge = challenge_encrypted ^ Ks_ndarray # decode(XOR)

challenge_new_encrypted = np.frombuffer(challenge_new_encrypted, dtype=np.int8).reshape(puf_SETS, puf_BITS) # byte-> numpy array

challenge_new = challenge_new_encrypted ^ Ks_ndarray # decode(XOR)

"""
Compute Response, Response_new
"""
puf = pypuf.simulation.XORArbiterPUF(puf_BITS, puf_SEED)

response = puf.eval(challenge) # produce response, type: numpy array

response_new = puf.eval(challenge_new) # produce response_new, type: numpy array

"""
XOR Response, Response_new
"""

response_encrypted = response ^ Ks_ndarray[0:8] #type: numpy array

response_new_encrypted = response_new ^ Ks_ndarray[0:8]

"""
Hash A1
"""

response_str = np.array2string(response, separator='', prefix='', suffix='')[1:-1] #type: numpy array-> string

response_new_str = np.array2string(response_new, separator='', prefix='', suffix='')[1:-1] #type: numpy array-> string

A1 = key_id + Nc + Ks + response_str + response_new_str

A1_hash_object = hashlib.sha256(A1.encode('utf-8'))

A1_hex_dig = A1_hash_object.hexdigest()

"""
send MA3
"""
cmd = "Wish me happy birthday"
send_message("A1", A1_hex_dig)
send_message("Encrypted Response",response_encrypted.tobytes())
send_message("Encrypted Response new",response_new_encrypted.tobytes())
send_message("Command", cmd)

# Clean up
spi.deinit()
