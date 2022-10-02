import socket
import sys

if (len(sys.argv) != 2):
    print('%s <porta>' % (sys.argv[0]))
    sys.exit(0)

ip = '127.0.0.1'
porta = int(sys.argv[1])

soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete.bind((ip, porta))
soquete.listen(10)

while True:
    s, cliente = soquete.accept()
    dados = '-pong'
    s.send(dados)
    s.close()

soquete.close()
