import bluetooth
import json
import numpy as np
import random
import pypuf.io
import pypuf.simulation
import time

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


# Define function to send message
def send_message(message_title, data):
    print(f"Sending {message_title} to Car...")
    #print(f"Checking messsage: {data}")
    json_str = json.dumps(data)
    sock.sendall(json_str.encode("utf-8"))
    print(f"{message_title} has been sent")
 

def receive_message(message_title):
    print(f"Receiving {message_title} from Car...")
    buffer_size = 1024
    chunks = []
    bytes_received = 0
    while True:
        chunk = sock.recv(buffer_size)
        if not chunk:
            break
        chunks.append(chunk)
        bytes_received += len(chunk)
        if bytes_received >= buffer_size:
            break
    json_str = b''.join(chunks).decode('utf-8')
    data = json.loads(json_str)
    print(f"Received {message_title}")
    return data

#simple version of receive_message
"""
def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    data = sock.recv(1024)
    print(f"Received {key}: {data.decode('utf-8')} ")

    return data.decode('utf-8')
"""

#Initialize socket
sock = connect_to_server(SERVER_ADDRESS, PORT)


# Generate key id
key_id = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS)

key_id_dict = {'ID': key_id}

send_message("Key ID", key_id_dict) # Sending Key ID

challenge_dict = receive_message("Challenge") # Receiving Challenge

challenge = challenge_dict['Challenge']

challenge = np.array(challenge_dict['Challenge'])

puf = pypuf.simulation.XORArbiterPUF(puf_BITS, puf_SEED)

response = puf.eval(challenge) # produce response

response = response.tolist() # Translate numpy.ndarray to list in order to transmit

respoonse_dict = {"Response":response}

send_message("Response", respoonse_dict) # Sending Response

#Ks_dict = receive_message('Ks')

#Ks = Ks_dict['Ks']
data = sock.recv(1024)
received_Ks = data.decode('utf-8') # Receiving Ks
print(f"Received Ks: {received_Ks}")

# Clean up
sock.close()

