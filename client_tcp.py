import json
import socket
import sys
import threading
import time
import tkinter as tk
import uuid
from tkinter.messagebox import showinfo

#### ROTAS GLOBAIS - CLIENTE
nro_jogador = 1

counter = 0
root = tk.Tk()
teste = False
board = [[0] * 15 for _ in range(15)]

clientId = uuid.uuid4().hex

ROOT_LOG = "\033[1;33mROOT: \033[0;0m"
ERROR_LOG = "\033[1;31mERROR: \033[0;0m"
RUNTIME_LOG = "\033[0;32mRUNTIME: \033[0;0m"
FUNCTION_LOG = "\033[0;35mFUNCTION: \033[0;0m"
FUNCTION_ARGS_LOG = "\033[0;35mFUNCTION_ARGS: \033[0;0m"

#soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#### ROTAS GLOBAIS - CLIENTE

# INÍCIO - MÉTODOS PRIVADOS CLIENTE

def inserir_grid():
    global gameframe
    global i, j

    gameframe = tk.Frame(root)
    gameframe.pack()

    renderizar_grid()

def on_click_grid(i, j, event):
    global counter
    localBoard = boardManager.getTabuleiro()

    pode_jogar = obter_retorno_servidor(json.dumps({"clientId": clientId, "message": "posso_jogar"}))
    response_pode_jogar = pode_jogar.get("response")

    if bool(response_pode_jogar):
        if localBoard[i][j] == 0:
            retorno = obter_retorno_servidor(json.dumps({"clientId": clientId, "message": "nro_jogador"}))
            nro_jogador = retorno.get("nro_jogador")
            
            color = "gray" if nro_jogador % 2 else "black"  # Famoso ternário do PYTHON :)
            event.widget.config(bg=color)

            localBoard[i][j] = nro_jogador

            dados = obter_retorno_servidor(json.dumps({"clientId": clientId, "i": i, "j": j, "jogador": nro_jogador}))

            if dados != None:
                response = dados.get("response")
                message = dados.get("message")

                if (message != None):
                    showinfo("Aviso!", message)

                if bool(response):
                    showinfo("FIM DE JOGO!", "Jogador " + str(nro_jogador) + " venceu!")
                    fechar_janela(True)

                if not interval.getStatus():
                    interval.restartInterval()

        elif localBoard[i][j] != nro_jogador:
            showinfo("Aviso!", "Essa posição já foi selecionada!")

    else:
        showinfo("Aviso!", "Aguarde a sua vez de jogar.")
        return


def verificar_status_jogada_servidor():
    dados_rcv = obter_retorno_servidor(json.dumps({"clientId": clientId, "message": "aguardando"}))
    new_board = dados_rcv.get("board")
    end_game = dados_rcv.get("end_game")

    if end_game != None:
        if bool(end_game):
            nro_jogador = dados_rcv.get("nro_jogador")
            showinfo("FIM DE JOGO!", "Jogador " + str(nro_jogador) + " venceu!")
            fechar_janela(True)

    if new_board != None:
        if new_board != boardManager.getTabuleiro():
            boardManager.setTabuleiro(board=new_board)
            renderizar_grid(new_board)
            if interval.getStatus():
                interval.cancel()

            return True

    return False

def renderizar_grid(board_in = None):
    board_temp = boardManager.getTabuleiro()
    if board_in != None: board_temp = board_in

    linhas = len(board_temp)
    colunas = len(board_temp[0])

    for i in range(linhas):
        for j in range(colunas):
            labels_grid = tk.Label(gameframe, text="      ", bg= "white" if board_temp[i][j] == 0 else "gray" if board_temp[i][j] == 1 else "black")
            labels_grid.grid(row=i, column=j, padx='6', pady='6')
            labels_grid.bind('<Button-1>', lambda e, i=i, j=j: on_click_grid(i, j, e))

def imprimir_grid():
    linhas = len(board)
    colunas = len(board[0])

    for i in range(linhas):
        for j in range(colunas):
            if (j == colunas - 1):
                print("%d" % board[i][j])
            else:
                print("%d" % board[i][j], end=" ")

# FIM - MÉTODOS PRIVADOS CLIENTE

# INÍCIO - MÉTODOS ROOT CLIENTE

def conexao_servidor():
    retorno = obter_retorno_servidor(json.dumps({"clientId": clientId, "message": None}))

    nro_jogador = retorno.get("nro_jogador")
    print("Conectado ao servidor com sucesso!")

    if nro_jogador == 1:
        print("Você é o primeiro a jogar.")
        interval.cancel()
    else:
        print("Você é o segundo a jogar.")

def sucesso_conexao_servidor():
    return obter_retorno_servidor(json.dumps({"clientId": clientId, "message": ""}))

def configurar_janela():
    label_nro_jogador = tk.Label(root, text=f"Jogador nº: ", textvariable = nro_jogador, relief=tk.RAISED)
    label_nro_jogador.pack(side="bottom", pady="30")

    btn = tk.Button(root, text='Imprimir matriz no console', command=imprimir_grid)
    btn.pack(side="bottom", pady="20")

    btn = tk.Button(root, text='FecharTESTE', command=on_window_closing)
    btn.pack(side="bottom", pady="10")


    #root.iconbitmap(bitmap='themes/icons/Gomoku.ico')
    root.winfo_toplevel().title("Socket's Gomoku")

def fechar_janela(confirmar_saida = False, evento_fechamento = False):
    showinfo("Aviso!", "O jogo (cliente) será encerrado.")

    if confirmar_saida:
        if sucesso_conexao_servidor():
            obter_retorno_servidor(json.dumps({"clientId": clientId, "message": "saindo"}))

    root.destroy()

def on_window_closing():
    fechar_janela(True, True)

def configurar_mainloop_calls():
    #root.protocol("WM_DELETE_WINDOW", on_window_closing())
    root.geometry("700x700")
    root.mainloop()

StartTime=time.time()

def action() :
    verificar_status_jogada_servidor()
    #print('action ! -> time : {:.1f}s'.format(time.time()-StartTime))

class gerenciaTabuleiro :
    def __init__(self) :
        self.board = [[0] * 15 for _ in range(15)]
    def setTabuleiro(self, board):
        self.board = board
    def getTabuleiro(self):
        return self.board

class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.status=False
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.status = True
            self.action()
            
    def getStatus(self):
        return self.status

    def cancel(self) :
        self.stopEvent.set()
        self.status = False

    def restartInterval(self):
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

# FIM - MÉTODOS ROOT CLIENTE

# INÍCIO - LÓGICA TCP CLIENTE

def obter_retorno_servidor(dados_send):
    try:
        if dados_send:
            soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soquete.connect((ip, porta))
            soquete.send(dados_send.encode())
            dados_rcv = soquete.recv(1024)
            dados_rcv = json.loads(dados_rcv.decode())
            soquete.close()

            return dados_rcv
    except:
        showinfo("Aviso!", "Ocorreu um erro ao tentar obter dados do servidor.")
        fechar_janela()

if len(sys.argv) != 3:
    print('%s <ip> <porta>' % (sys.argv[0]))
    sys.exit(0)

ip = sys.argv[1]
porta = int(sys.argv[2])
interval = setInterval(0.5, action)
boardManager = gerenciaTabuleiro()

configurar_janela()
conexao_servidor()
inserir_grid()

configurar_mainloop_calls()

# FIM - LÓGICA TCP CLIENTE
