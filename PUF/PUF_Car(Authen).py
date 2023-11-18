import json
import numpy as np
import random
import pypuf.io
import pypuf.simulation
import time
import hashlib
import busio
import board
import digitalio
import pickle
import adafruit_rfm9x
import zlib
import time
from digitalio import DigitalInOut


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
rfm9x.node = 1
rfm9x.destination = 2
rfm9x.ack_retries = 5
rfm9x.ack_wait = 2.0  # 2 seconds

puf_BITS = 32
puf_SEED = 1
puf_SETS = 8



def send_message(key, value):
    print(f"Sending {key} from Key to Car...")
    if not isinstance(value, bytes):
        value = bytes(value, 'utf-8')
    
    MAX_CHUNK_SIZE = 170  # Adjusted chunk size
    num_chunks = (len(value) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE
    for i in range(num_chunks):
        chunk = value[i * MAX_CHUNK_SIZE: (i + 1) * MAX_CHUNK_SIZE]
        rfm9x.send_with_ack(chunk)  # Send data as bytes
        if i < num_chunks - 1:  # If there are more chunks to send, add a delay
            time.sleep(0.1)  # Adjust this delay as needed
    print(f"{key} has been sent")


# Replace receive_message with LoRa reception
def receive_message(key):
    print(f"Receiving {key} from Key to Car...")
    while True:
        data = rfm9x.receive(with_ack=True)
        if data is not None:
            print(f"Received {key}")
            return data
        time.sleep(1)  # Add a small delay before checking again

while True:
    with open('car_data.pkl', 'rb') as f:
        data = pickle.load(f)

    key_id = data['Key_id']
    challenge_ndarray = data['Challenge']

    response_str = data['Response']
    Ks = data['Ks']

    # Process Ks to get Ks_ndarray
    Ks_ndarray = np.array([int(c) for c in Ks], dtype=np.int8)

    """
    Receive MA1
    """

    received_data = receive_message('MA1_data').decode('utf-8')
    start_time = time.time()
    message_data = json.loads(received_data)

    # Extract the individual parts
    key_id = message_data['ID']
    Ni_encrypted = bytes.fromhex(message_data['Encrypted_Ni'])  # Convert hex string back to bytes

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
    Nc_encryptedz_compressed = zlib.compress(Nc_encrypted.tobytes())
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
    challenge_encrypted_compressed = zlib.compress(challenge_encrypted.tobytes())
    challenge_new_encrypted_compressed = zlib.compress(challenge_new_encrypted.tobytes())

    """
    send MA2
    """
    # Group the data into a dictionary
    message_data = {
        "A0": A0_hex_dig,
        "Encrypted_Nc": Nc_encryptedz_compressed.hex(),
        "Encrypted_Challenge": challenge_encrypted_compressed.hex(),
        "Encrypted_Challenge_New": challenge_new_encrypted_compressed.hex()
    }

    # Convert the dictionary to a JSON string and send
    message_json = json.dumps(message_data).encode('utf-8')

    send_message("Combined_Data", zlib.compress(message_json))

    """
    receive MA3
    """


    compressed_data = receive_message("Compressed_MA3_Data")
    decompressed_data = zlib.decompress(compressed_data)

    # Parse the combined data from JSON
    combined_data = json.loads(decompressed_data.decode('utf-8'))

    # Extract individual components
    A1_hex_dig = combined_data["A1"]
    response_encrypted = bytes.fromhex(combined_data["Encrypted_Response"])
    response_new_encrypted = bytes.fromhex(combined_data["Encrypted_Response_New"])
    cmd = combined_data["Command"]

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
            data = {
                    'Key_id': key_id,
                    'Challenge': challenge_new,
                    'Response': response_new,
                    'Ks': Ks
            }
            # print(data)
            # Serialize the register_output dictionary and write to car_data.pkl
            with open('car_data.pkl', 'wb') as f:
                pickle.dump(data, f)
                    
        else:
            print("Failed Response verified")
    else:
        print("Failed A1 verified")

    print(time.time()- start_time )