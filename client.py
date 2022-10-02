import socket
import sys

if (len(sys.argv) != 3):
    print('%s <ip> <porta>' % (sys.argv[0]))
    sys.exit(0)

ip = sys.argv[1]
porta = int(sys.argv[2])

soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete.connect((ip, porta))

dados = soquete.recv(1024)
soquete.close()
