import bluetooth
import os

# Define the RFCOMM port for Bluetooth communication
port = 1

# Define the maximum number of allowed remote key IDs
max_num_remote_key_ids = 2

# Create a list to store the registered remote key IDs
remote_key_ids = []

# Read the registered remote key IDs from the file, if it exists
if os.path.exists('remote_key_ids.txt'):
    with open('remote_key_ids.txt', 'r') as f:
        remote_key_ids = f.read().splitlines()

# Function to handle new remote key IDs
def handle_new_remote_key_id(remote_key_id):
    # Check if the maximum number of allowed remote key IDs has been reached
    if len(remote_key_ids) >= max_num_remote_key_ids:
        print("Cannot register new remote key ID. Maximum limit reached.")
        return

    # Add the new remote key ID to the list
    remote_key_ids.append(remote_key_id)

    # Write the updated remote key IDs to the file
    with open('remote_key_ids.txt', 'w') as f:
        for key_id in remote_key_ids:
            f.write("%s\n" % key_id)

    # Do something with the new remote key ID
    print(f"New remote key ID registered: {remote_key_id}")
    # Add your desired action here
    new_id_action()

# Set up Bluetooth connection
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", port))
server_sock.listen(1)
print(f"Waiting for connection on RFCOMM channel {port}")

while True:
    # Wait for a client to connect
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    # Receive ID from remote key
    remote_key_id = client_sock.recv(1024).decode()
    print(f"Received ID: {remote_key_id}")

    # Check if the ID has been registered before
    if remote_key_id in remote_key_ids:
        print(f"Remote key ID {remote_key_id} already registered")
        # Add your desired action here
        registered_id_action()
    else:
        handle_new_remote_key_id(remote_key_id)

    # Close the Bluetooth socket
    client_sock.close()

# Close the server socket
server_sock.close()
