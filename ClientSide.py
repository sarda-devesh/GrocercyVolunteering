import socket

HOST = '18.233.60.28'  # Public Elastic IP
PORT = 6666 
timeout = 2

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(timeout)
    client_socket.connect((HOST,PORT))
    while(True):
        number = str(input("Please enter a number: "))
        data = str(input("Enter a message: ")) + ";"
        if "close" in data.lower():
            client_socket.sendall("quit".encode())
            break
        data = str(number) + "/" + str(data)
        client_socket.sendall(data.encode())
    client_socket.close()
except socket.timeout:
    print("Couldn't connect to server")
