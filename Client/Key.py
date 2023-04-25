import bluetooth

# Set up Bluetooth connection
target_bluetooth_address = "XX:XX:XX:XX:XX:XX"  # Replace with the target device's Bluetooth address
port = 1
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((target_bluetooth_address, port))

# Define ID
remote_key_id = "12345"

# Send ID to server
sock.send(remote_key_id.encode())

# Close the Bluetooth socket
sock.close()
