import socket
import sys
import json


def verifica_linha(i, jogador_atual, board):
    b = 0;
    count = 0
    total = 14
    while b <= total:
        if board[i][b] == jogador_atual:
            count += 1
            if count == 5:
                return True
        else:
            count = 0
        b += 1

    return False

def verifica_tabuleiro(i, j, jogador, board):
    if verifica_linha(i, jogador_atual=jogador, board=board):
        return True
    if verifica_coluna(j, jogador_atual=jogador, board=board):
        return True
    if verifica_diagonal(jogador, board=board):
        return True

    return False

def verifica_coluna(j, jogador_atual, board):
    b = 0;
    count = 0
    total = 14
    while b <= total:
        if board[b][j] == jogador_atual:
            count += 1
            if count == 5:
                return True
        else:
            count = 0
        b += 1
    return False


def verifica_diagonal(jogador, board):
    max_col = len(board[0])
    max_row = len(board)
    fdiag = [[] for _ in range(max_row + max_col - 1)]
    bdiag = [[] for _ in range(len(fdiag))]
    min_bdiag = -max_row + 1

    for x in range(max_col):
        for y in range(max_row):
            fdiag[x + y].append(board[y][x])
            bdiag[x - y - min_bdiag].append(board[y][x])

    count = 0
    for vetor in bdiag:
        for item in vetor:
            if item == jogador:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

    for vetor in fdiag:
        for item in vetor:
            if item == jogador:
                count += 1
                if count == 5:
                    return True
            else:
                count = 0

    return False


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
    #i, j, jogador = s.recv(1024)
    dados_recv = s.recv(1024)
    dados_recv = json.loads(dados_recv.decode())

    board = dados_recv.get("board")
    i = dados_recv.get("i")
    j = dados_recv.get("j")
    jogador = dados_recv.get("jogador")

    if verifica_tabuleiro(i, j, jogador, board=board):
        dados = json.dumps({"i": i, "j": j,  "response": True})
    else:
        dados = json.dumps({"i": i, "j": j, "response": False})

    s.send(dados.encode())
    s.close()

soquete.close()
