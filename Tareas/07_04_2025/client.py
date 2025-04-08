import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('192.168.100.9', 9999))

while True:
    data = client.recv(1024)
    if not data:
        break
    print(data.decode())

client.close()
