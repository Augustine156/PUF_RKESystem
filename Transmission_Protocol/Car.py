import bluetooth

PORT = 1

def advertise_service(port):
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)
    
    print(f"Waiting for connection on RFCOMM channel {port}...")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info[0]}")
    
    return server_sock, client_sock
    
def send_message(key, value):
    print(f"Sending {key} from Key to Car...")
    client_sock.sendall(value.encode("utf-8"))
    print(f"{key}: {value} has been sent")


def receive_message(key):
    print(f"Receiving {key} from Car to Key...")
    data = client_sock.recv(1024)
    print(f"Received {key}: {data.decode('utf-8')} ")

    return data.decode('utf-8')

    




server_sock, client_sock = advertise_service(PORT)

ID = receive_message("ID")

send_message("Challenge", "34567")

Response = receive_message("Response")

send_message("Ks", "45678")
    
client_sock.close()
server_sock.close()
