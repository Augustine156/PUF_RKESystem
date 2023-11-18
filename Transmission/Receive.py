
# Define function to receive message
def receive_message(message_title):
    print(f"Receiving {message_title} from Car...")
    packet = None
    while packet is None:
        packet = rfm9x.receive(with_ack=True)
        time.sleep(0.1)
    print(f"Received {message_title}")
    return str(packet, 'utf-8')



# Replace receive_message with LoRa reception
def receive_message(key):
    print(f"Receiving {key} from Key to Car...")
    while True:
        data = rfm9x.receive(with_ack=True)
        if data is not None:
            print(f"Received {key}")
            return data
        time.sleep(1)  # Add a small delay before checking again

# For larger message the cant send and receive in one packet
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