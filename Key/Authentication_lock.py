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
import pickle
import zlib
from digitalio import DigitalInOut, Direction, Pull
import adafruit_ssd1306



RADIO_FREQ_MHZ = 433.0
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

rfm9x.tx_power = 23
# enable CRC checking
rfm9x.enable_crc = True
# set delay before transmitting ACK (seconds)
rfm9x.ack_delay = 0.1
# set node addresses
rfm9x.node = 2
rfm9x.destination = 1
rfm9x.ack_retries = 5
rfm9x.ack_wait = 2.0  # 2 seconds


puf_BITS = 32
puf_SEED = 1
puf_SETS = 8

def send_message(key, value):
    msg = f"Sending {key} from Key to Car..."
    print(msg)
    if isinstance(value, str):
        value = value.encode('utf-8')
    rfm9x.send_with_ack(value)
    
    print(f"{key} has been sent")


def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    MAX_CHUNK_SIZE = 170  # Adjusted chunk size to match send_message
    received_data = b''
    while True:
        data = rfm9x.receive(with_ack=True)
        if data is not None:
            received_data += data
            # If we received less than the maximum chunk size, we've received the last chunk
            if len(data) < MAX_CHUNK_SIZE:  
                break
        time.sleep(0.1)  # Add a small delay before checking again
    print(f"Received {key}")
    return received_data


# Load data from pickle file
with open('key_fob_data.pkl', 'rb') as f:
    data = pickle.load(f)

# Access the values
key_id = data['Key_id']#string
Ks = data['Ks']#string
Ks_ndarray = np.array([int(c) for c in Ks], dtype=np.int8) #type: string-> numpy array

"""
Generate & XOR Ni
"""
Ni = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS) #type: string

Ni_ndarray = np.array([int(c) for c in Ni], dtype=np.int8) #type: string-> numpy array

Ni_encrypted = Ks_ndarray ^ Ni_ndarray #type: numpy array

"""
# Send MA1
"""

# Create a dictionary to hold both pieces of data
message_data = {
    'ID': key_id,
    'Encrypted_Ni': Ni_encrypted.tobytes().hex()  # Convert bytes to hex string for JSON serialization
}

# Convert the dictionary to a JSON string
message_json = json.dumps(message_data)

# Send the combined message
send_message('MA1_data', message_json)

"""
# Receive MA2
"""
compressed_data = receive_message("Compressed_Combined_Data")
decompressed_data = zlib.decompress(compressed_data)
# Parse the combined data from JSON
message_data = json.loads(decompressed_data.decode('utf-8'))

# Extract and process individual components
A0_hex_dig = message_data["A0"]

# Convert hex strings back to bytes
Nc_encrypted_compressed = bytes.fromhex(message_data["Encrypted_Nc"])
challenge_encrypted_compressed = bytes.fromhex(message_data["Encrypted_Challenge"])
challenge_new_encrypted_compressed = bytes.fromhex(message_data["Encrypted_Challenge_New"])


"""
#Decode Nc
"""
Nc_encrypted = np.frombuffer(zlib.decompress(Nc_encrypted_compressed), dtype=np.int8).reshape(puf_BITS) # byte-> numpy array

Nc = Nc_encrypted ^ Ks_ndarray # decode(XOR)

Nc = np.array2string(Nc, separator='', prefix='', suffix='')[1:-1] # remove brackets and whitespace, type: numpy array-> string


"""
Verify A0
"""

A0_verified = key_id + Ni + Ks + Nc

A0_verified_hash_object = hashlib.sha256(A0_verified.encode('utf-8'))

A0_verified_hex_dig = A0_verified_hash_object.hexdigest()


#A0_verified = hash(A0_verified) #type: int


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
# Decompress data
challenge_encrypted = np.frombuffer(zlib.decompress(challenge_encrypted_compressed), dtype=np.int8).reshape(puf_SETS, puf_BITS)
challenge_new_encrypted = np.frombuffer(zlib.decompress(challenge_new_encrypted_compressed), dtype=np.int8).reshape(puf_SETS, puf_BITS)
# challenge_encrypted = np.frombuffer(challenge_encrypted, dtype=np.int8).reshape(puf_SETS, puf_BITS) # byte-> numpy array

challenge = challenge_encrypted ^ Ks_ndarray # decode(XOR)

# challenge_new_encrypted = np.frombuffer(challenge_new_encrypted, dtype=np.int8).reshape(puf_SETS, puf_BITS) # byte-> numpy array

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
expiration_time = int(time.time()) + 3  # 例: 0.3秒後まで有効

cmd = "lock"
combined_data = {
    'A1': A1_hex_dig,
    'Encrypted_Response': response_encrypted.tobytes().hex(),
    'Encrypted_Response_New': response_new_encrypted.tobytes().hex(),
    'Command': cmd,
    'ExpirationTime': expiration_time
}
combined_json = json.dumps(combined_data)
compressed_data = zlib.compress(combined_json.encode('utf-8'))

send_message("Compressed_MA3_Data", compressed_data)

# Clean up
spi.deinit()