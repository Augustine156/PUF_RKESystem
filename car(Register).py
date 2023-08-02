import numpy as np
import random
import pypuf.io
import digitalio
import board
import busio
import adafruit_rfm9x
import time
import pickle


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
    print(f"Sending {message_title} to Key...")
    if isinstance(data, list):
        data = ','.join(map(str, data))  # Convert list to string
    if rfm9x.send_with_ack(bytes(data, "utf-8")):
        print(f"{message_title} has been sent and acknowledged")
    else:
        print(f"Failed to send {message_title}")

# Define function to receive message
def receive_message(message_title):
    print(f"Receiving {message_title} from Key...")
    packet = None
    while packet is None:
        packet = rfm9x.receive(with_ack=True)
        time.sleep(0.1)
    print(f"Received {message_title}")
    return str(packet, 'utf-8')

key_id = receive_message('ID') # Receiving Key ID

challenge = pypuf.io.random_inputs(puf_BITS, puf_SETS, puf_SEED) # Generate Challenge

# Send each sub-list of the challenge individually
for i, sub_challenge in enumerate(challenge):
    send_message(f'Challenge {i+1}', sub_challenge.tolist())

response = receive_message('Response') # Receiving Response

response = np.array(response.split(',')) # Convert received string back to numpy array

Ks = bin(random.getrandbits(puf_BITS))[2:].zfill(puf_BITS) #Generate Ks

send_message('Ks', Ks)

values = [key_id, challenge, response]
keys = ['Key_id', 'Challenge', 'Response']

register_output = dict(map(lambda k, v: (k, v), keys, values))

print(register_output)


# Store data
data = {
    'Key_id': key_id,
    'Challenge': challenge,
    'Response': response,
    'Ks': Ks
}

with open('car_data.pkl', 'wb') as f:
    pickle.dump(data, f)
# Clean up
spi.deinit()
