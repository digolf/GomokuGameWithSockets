import json
import socket
import sys
from cmath import log

board = [[0] * 15 for _ in range(15)]

ROOT_LOG = "\033[1;33mROOT: \033[0;0m"
ERROR_LOG = "\033[1;31mERROR: \033[0;0m"
RUNTIME_LOG = "\033[0;32mRUNTIME: \033[0;0m"
FUNCTION_LOG = "\033[0;35mFUNCTION: \033[0;0m"
FUNCTION_ARGS_LOG = "\033[0;35mFUNCTION_ARGS: \033[0;0m"

class gerenciaTabuleiro :
    def __init__(self) :
        self.board = [[0] * 15 for _ in range(15)]
    def setTabuleiro(self, board):
        self.board = board
    def getTabuleiro(self):
        return self.board
    def resetTabuleiro(self):
        self.board = [[0] * 15 for _ in range(15)]

# INÍCIO - MÉTODOS PRIVADOS SERVIDOR

def verificar_tabuleiro(i, j, jogador, board):
    if verificar_linha(i, jogador_atual=jogador, board=board):
        return True
    if verificar_coluna(j, jogador_atual=jogador, board=board):
        return True
    if verificar_diagonal(jogador, board=board):
        return True

    return False

def verificar_linha(i, jogador_atual, board):
    b = 0
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

def verificar_coluna(j, jogador_atual, board):
    b = 0
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

def verificar_diagonal(jogador, board):
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

# FIM - MÉTODOS PRIVADOS SERVIDOR

# INÍCIO - MÉTODOS ROOT CLIENTE

def resetGame():
    boardManager.resetTabuleiro()

# FIM - MÉTODOS ROOT CLIENTE

# INÍCIO - LÓGICA TCP SERVIDOR

if (len(sys.argv) != 2):
    print(ERROR_LOG, '%s <porta>' % (sys.argv[0]))
    sys.exit(0)

ip = '127.0.0.1' #localhost
porta = int(sys.argv[1])
nr_clientes = 0
id_clientes = []

end_game = False
jogo_iniciado = False
primeiro_jogador_aguardando = 0
boardManager = gerenciaTabuleiro()

soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soquete.bind((ip, porta))
soquete.listen()

while True:
    s, cliente = soquete.accept()
    dados_recv = s.recv(1024)
    dados_recv = json.loads(dados_recv.decode())
    clientId = dados_recv.get("clientId")

    if not clientId in id_clientes:
        nr_clientes+=1
        id_clientes.append(clientId)
        print(ROOT_LOG, f"Cliente {clientId} conectado.")
        print(ROOT_LOG, "Clientes conectados:", nr_clientes)
        dados = json.dumps({"nro_jogador": nr_clientes})

    if dados_recv.get("message") == 'get_board':
        dados = json.dumps({"board": boardManager.getTabuleiro()})

    if dados_recv.get("message") == "aguardando" or dados_recv.get("message") == "posso_jogar":
        if nr_clientes < 2 and jogo_iniciado == True:
            jogo_iniciado = False
            dados = json.dumps({"player_left": True, "board": boardManager.getTabuleiro()})

    if nr_clientes <= 2:
        if nr_clientes > 1:
            if dados_recv.get("message") == None:
                i = dados_recv.get("i")
                j = dados_recv.get("j")
                jogador = dados_recv.get("jogador")
                boardTemp = [[0] * 15 for _ in range(15)]
                boardTemp = boardManager.getTabuleiro()
                
                if (i != None):
                    jogo_iniciado = True

                    if dados_recv.get("jogador") == 1:
                        primeiro_jogador_aguardando = 1
                    else:
                        primeiro_jogador_aguardando = 0

                    boardTemp[i][j] = jogador

                    if verificar_tabuleiro(i, j, jogador, board=boardTemp):
                        dados = json.dumps({"response": True})
                        end_game = True
                    else:
                        jogador = id_clientes.index(clientId) + 1
                        dados = json.dumps({"response": False})

                boardManager.setTabuleiro(board=boardTemp)

            elif dados_recv.get("message") == "aguardando":
                if end_game:
                    dados = json.dumps({"end_game": end_game, "nro_jogador": jogador})
                else:
                    dados = json.dumps({"board": boardManager.getTabuleiro()})

            elif dados_recv.get("message") == "nro_jogador":
                jogador = id_clientes.index(clientId) + 1
                dados = json.dumps({"nro_jogador": jogador})

            elif dados_recv.get("message") == "posso_jogar":
                jogador = id_clientes.index(clientId) + 1
                if primeiro_jogador_aguardando == 1:
                    if jogador == 1:
                        dados = json.dumps({"response": False})
                    else: 
                        dados = json.dumps({"response": True})
                else:
                    if jogador == 2:
                        dados = json.dumps({"response": False})
                    else: 
                        dados = json.dumps({"response": True})

            elif dados_recv.get("message") == "saindo":
                id_clientes.remove(clientId)
                nr_clientes = nr_clientes - 1 if nr_clientes > 0 else 0
                print(ROOT_LOG, f'Cliente {clientId} desconectado.')
                print(ROOT_LOG, "Clientes conectados:", nr_clientes)

            
            if nr_clientes < 2:
                print(ROOT_LOG, f'Limpando dados de jogo...')
                primeiro_jogador_aguardando = 0
                end_game = False
                resetGame()

        else:
            if dados_recv.get("message") == "saindo":
                id_clientes.remove(clientId)
                nr_clientes = nr_clientes - 1 if nr_clientes > 0 else 0
                print(ROOT_LOG, f'Cliente {clientId} desconectado.')
                print(ROOT_LOG, "Clientes conectados:", nr_clientes)

        s.send(dados.encode())
        s.close()
    else:
        print(ERROR_LOG, 'Número máximo de jogadores atingido para este servidor.')
        break

# FIM - LÓGICA TCP SERVIDOR
