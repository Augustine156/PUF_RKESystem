# Define function to send message
def send_message(message_title, data):
    print(f"Sending {message_title} to Car...")
    if isinstance(data, list):
        data = ','.join(map(str, data))  # Convert list to string
    if rfm9x.send_with_ack(bytes(data, "utf-8")):
        print(f"{message_title} has been sent and acknowledged")
    else:
        print(f"Failed to send {message_title}")



# For large size message that cant transmit in ine packet
def send_message(key, value):
    print(f"Sending {key} from Car to Key...")
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
