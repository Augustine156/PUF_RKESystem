import bluetooth
import json
import numpy as np
import random
import pypuf.io
import pypuf.simulation
import time
import hashlib
PORT = 1  
SERVER_ADDRESS = "DC:A6:32:4A:67:A8"  # MAC address of Key (Naked Raspberry Pi)
puf_BITS = 64
puf_SEED = 1
puf_SETS = 8
# Define function to set up Bluetooth socket and connect to server
def connect_to_server(server_address, port):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((server_address, port))
    return sock

def send_message(key, value):
    print(f"Sending {key} from Key to Car...")
    sock.sendall(value)
    print(f"{key} has been sent")

#simple version of receive_message

def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    data = sock.recv(1024)
    print(f"Received {key} ")
    return data

with open('data.txt', 'r') as f:
    register_output = {}
    for line in f:
        key, value = line.strip().split(': ')
        register_output[key] = value
        
#Initialize socket
sock = connect_to_server(SERVER_ADDRESS, PORT)
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
send_message('ID',key_id.encode('utf-8'))

send_message('Encrypted Ni',Ni_encrypted.tobytes())

"""
#Receive MA2
"""

A0_hex_dig = receive_message("A0")
Nc_encrypted = receive_message("Encrypted Nc")
challenge_encrypted = receive_message("Encrypted Challenge")
challenge_new_encrypted = receive_message("Encrypted Challenge New")

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
send_message("A1", A1_hex_dig.encode('utf-8'))
send_message("Encrypted Response",response_encrypted.tobytes())
send_message("Encrypted Response new",response_new_encrypted.tobytes())
send_message("Command", cmd.encode('utf-8'))

# Clean up
sock.close()

