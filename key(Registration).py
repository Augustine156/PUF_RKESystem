import numpy as np
import random
import pypuf.io
import pypuf.simulation
import digitalio
import board
import busio
import adafruit_rfm9x
import time


puf_BITS = 64
puf_SEED = 1
puf_SETS = 8

RADIO_FREQ_MHZ = 433.0
CS = digitalio.DigitalInOut(board.CE1)
RESET = digitalio.DigitalInOut(board.D25)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Adjust ACK parameters
rfm9x.ack_delay = 0.1
rfm9x.ack_retries = 5
rfm9x.ack_wait = 0.2

# Define function to send message
def send_message(message_title, data):
    print(f"Sending {message_title} to Car...")
    if isinstance(data, list):
        data = ','.join(map(str, data))  # Convert list to string
    if rfm9x.send_with_ack(bytes(data, "utf-8")):
        print(f"{message_title} has been sent and acknowledged")
    else:
        print(f"Failed to send {message_title}")

# Define function to receive message
def receive_message(message_title):
    print(f"Receiving {message_title} from Car...")
    packet = None
    while packet is None:
        packet = rfm9x.receive(with_ack=True)
        time.sleep(0.1)
    print(f"Received {message_title}")
    return str(packet, 'utf-8')

# Generate key id
key_id = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS)

send_message("Key ID", key_id) # Sending Key ID

# Receive each sub-list of the challenge individually
challenge = []
for i in range(puf_SETS):
    sub_challenge = receive_message(f"Challenge {i+1}") # Receiving Challenge
    challenge.append(list(map(int, sub_challenge.split(','))))

challenge = np.array(challenge) # Convert list to numpy array

puf = pypuf.simulation.XORArbiterPUF(puf_BITS, puf_SEED)

response = puf.eval(challenge) # produce response

response = ','.join(map(str, response.tolist())) # Convert numpy array to string for sending

send_message("Response", response) # Sending Response

received_Ks = receive_message('Ks') # Receiving Ks

print(f"Received Ks: {received_Ks}")
