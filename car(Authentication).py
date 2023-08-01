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

# Function to split data into smaller packets
def chunk_data(data, chunk_size):
    return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]


def send_message(key, value):
    print(f"Sending {key} from Car to Key...")
    packet = bytearray(value)
    rfm9x.send_with_ack(packet)
    print(f"{key} has been sent")

def receive_message(key):
    print(f"Receiving {key} from Key to Car...")
    packet = rfm9x.receive(timeout=5)
    if packet is None:
        print("Timeout! No response received.")
        return None
    print(f"Received {key}")
    return packet

with open('register_output.txt', 'r') as f:
    register_output = {}
    for line in f:
        key, value = line.strip().split(': ')
        register_output[key] = value
    
challenge = register_output['Challenge'] #type: string

challenge = challenge.replace('[', '').replace(']', '').replace(' ', '')

# split string by ',' and convert each element to int64
challenge_ndarray = np.array([np.int8(x) for x in challenge.split(',')])

# reshape to desired dimensions
challenge_ndarray = challenge_ndarray.reshape(puf_SETS, puf_BITS)

Ks = register_output['Ks']        #type: string
Ks_ndarray = np.array([int(c) for c in Ks], dtype= np.int8)    #type: string -> numpy array


"""
Receive MA1
"""
key_id = receive_message('ID').decode('utf-8')

Ni_encrypted = receive_message('Encrypted Ni')

"""
Decode Ni
"""
Ni_encrypted = np.frombuffer(Ni_encrypted, dtype=np.int8).reshape(puf_BITS) # byte-> numpy array

Ni = Ni_encrypted ^ Ks_ndarray # decode(XOR)

Ni = np.array2string(Ni, separator='', prefix='', suffix='')[1:-1] # remove brackets and whitespace, type: numpy array-> string


"""
Generate & XOR Nc
"""
Nc = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS) #type: string

Nc_ndarray = np.array([int(c) for c in Nc], dtype= np.int8) #type: string -> numpy array

Nc_encrypted = Nc_ndarray ^ Ks_ndarray #type: numpy array

"""
XOR challenge
"""
challenge_encrypted = challenge_ndarray ^ Ks_ndarray #type: numpy array

"""
Generate hash
"""
A0 = key_id + Ni + Ks + Nc

A0_hash_object = hashlib.sha256(A0.encode('utf-8'))

A0_hex_dig = A0_hash_object.hexdigest()
"""
Generate & XOR challenge new
"""
challenge_new = pypuf.io.random_inputs(puf_BITS, puf_SETS, puf_SEED) # Generate Challenge, type: numpy array

challenge_new_encrypted = challenge_new ^ Ks_ndarray #type: numpy array

"""
send MA2
"""

# For sending messages, update like this:
send_message("A0", A0_hex_dig.encode('utf-8'))
send_message("Encrypted Nc", Nc_encrypted.tobytes())

# Split the challenge_encrypted into smaller packets and send them
for packet in chunk_data(challenge_encrypted.tobytes(), 200):
    send_message("Encrypted Challenge", packet)

# Split the challenge_new_encrypted into smaller packets and send them
for packet in chunk_data(challenge_new_encrypted.tobytes(), 200):
    send_message("Encrypted Challenge New", packet)

# For receiving messages, update like this:
A1_hex_dig = receive_message("A1").decode('utf-8')
response_encrypted = receive_message("Encrypted Response")
response_new_encrypted = receive_message("Encrypted Response new")
cmd = receive_message("Command").decode('utf-8')


"""
Decode Response & Response new
"""

response_encrypted = np.frombuffer(response_encrypted, dtype=np.int8) # byte-> numpy array

response = response_encrypted ^ Ks_ndarray[0:8] # decode(XOR)

response_new_encrypted = np.frombuffer(response_new_encrypted, dtype=np.int8) # byte-> numpy array

response_new = response_new_encrypted ^ Ks_ndarray[0:8] # decode(XOR)

"""
Verify Response and A1
"""

puf = pypuf.simulation.XORArbiterPUF(puf_BITS, puf_SEED)

response_verified = puf.eval(challenge_ndarray) # produce response, type: numpy array
#Above should compare with response


response_str = np.array2string(response, separator='', prefix='', suffix='')[1:-1] #type: numpy array-> string

response_new_str = np.array2string(response_new, separator='', prefix='', suffix='')[1:-1] #type: numpy array-> string

A1_verified = key_id + Nc + Ks + response_str + response_new_str

A1_verified_hash_object = hashlib.sha256(A1_verified.encode('utf-8'))

A1_verified_hex_dig = A1_verified_hash_object.hexdigest()

if(A1_verified_hex_dig == A1_hex_dig):
	if(np.array_equal(response, response_verified)):
		print(cmd)
		
		values = [key_id, challenge_new, response_new, Ks]
		keys = ['Key_id', 'Challenge', 'Response', 'Ks']
		register_output = dict(map(lambda k, v: (k, v), keys, values))
		print(register_output)
		"""
		with open('register_output.txt', 'w') as f:
			for key, value in register_output.items():
				f.write(f'{key}: {value}\n')
		"""
	else:
		print("Failed Response verified")
else:
	print("Failed A1 verified")



# Clean up
spi.deinit()
