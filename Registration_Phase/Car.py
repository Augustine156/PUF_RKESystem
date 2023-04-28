import bluetooth
import json
import numpy as np
import random
import pypuf.io
import pypuf.simulation
import time
PORT = 1
puf_BITS = 64
puf_SEED = 1
puf_SETS = 8

# initialize server
def advertise_service(port):
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)
    
    print(f"Waiting for connection on RFCOMM channel {port}...")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info[0]}")
    
    return server_sock, client_sock

    

# Define function to send message
def send_message(message_title, data):
    print(f"Sending {message_title} to Key...")
    #print(f"Checking messsage: {data}")
    json_str = json.dumps(data)
    client_sock.sendall(json_str.encode("utf-8"))
    print(f"{message_title} has been sent")


# Define function to receive message
def receive_message(message_title):
    print(f"Receiving {message_title} from Key...")
    json_str = client_sock.recv(1024)
    json_str = json_str.decode('utf-8')
    data = json.loads(json_str)
    print(f"Received {message_title}")
    return data


# Initalize socket
server_sock, client_sock = advertise_service(PORT)


key_id_dict = receive_message('ID') # Receiving Key ID

key_id = key_id_dict['ID']

challenge = pypuf.io.random_inputs(puf_BITS, puf_SETS, puf_SEED) # Generate Challenge

challenge = challenge.tolist() # numpy.ndarray to list

challenge_dict = {'Challenge':challenge}

send_message('Challenge', challenge_dict) # Sending Challenge

response_dict = receive_message('Response') # Receiving Response

response = response_dict['Response']

response = np.array(response_dict['Response'])

Ks = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS) #Generate Ks


#Ks_dict = {'Ks':Ks}


#Map all ID, Challenge-Response Pair
client_sock.sendall(Ks.encode("utf-8"))

values = [key_id, challenge, response]
keys = ['Key_id', 'Challenge', 'Response']

register_output = dict(map(lambda k, v: (k, v), keys, values))

print(register_output)

client_sock.close()
server_sock.close()
