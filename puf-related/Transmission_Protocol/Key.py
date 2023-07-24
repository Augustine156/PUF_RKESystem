import bluetooth


PORT = 1  # RFCOMM port number (must match the port used by Raspberry Pi B)
SERVER_ADDRESS = "DC:A6:32:4A:67:A8"  # replace with the Bluetooth MAC address of Raspberry Pi B

possible_data_type = {
	int : 'int',
	str : 'string'
}

# Define function to set up Bluetooth socket and connect to server
def connect_to_server(server_address, port):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((server_address, port))
    return sock

# Define function to send message
def send_message(key, value):
    print(f"Sending {key} from Key to Car...")
    sock.sendall(value.encode("utf-8"))
    print(f"{key}: {value} has been sent")

# Define function to receive message

def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    data = sock.recv(1024)
    print(f"Received {key}: {data.decode('utf-8')} ")

    return data.decode('utf-8')

	


send_message("ID", "12345")

challenge = receive_message("Challenge")

send_message("Response", "23456")

Ks = receive_message("Ks")


# Clean up
sock.close()
