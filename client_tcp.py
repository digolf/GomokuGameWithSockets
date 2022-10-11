import json
import socket
import sys
import tkinter as tk
import uuid
from ast import arg
from asyncio import CancelledError, get_event_loop, sleep
from email import message
from tkinter.messagebox import showinfo
from typing import Optional

#### ROTAS GLOBAIS - CLIENTE
nro_jogador = 0

counter = 0
root = tk.Tk()
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

    atualizar_grid()

def on_click_grid(i, j, event):
    dados_rcv = obter_retorno_servidor(json.dumps({"clientId": clientId, "message": "posso_jogar"}))    #TODO -> REVISAR ISSO AQUI, FAZER NO PRÓPRIO CLIENTE SE POSSÍVEL USANDO UM BOOLEAN QUANDO ESTIVER AGUARDANDO RESPOSTA.
    response = dados_rcv.get("response")
    if not bool(response):
        showinfo("Aviso!", "Aguarde a sua vez de jogar.")
        return
        
    global counter

    if board[i][j] == 0:
        color = "gray" if counter % 2 else "black"  # Famoso ternário do PYTHON :)
        event.widget.config(bg=color)

        if color == "gray":
            board[i][j] = 1
            jogador = 1
        else:
            board[i][j] = 2
            jogador = 2

        counter += 1

        dados = obter_retorno_servidor(json.dumps({"clientId": clientId, "i": i, "j": j, "jogador": jogador, "board": board}))

        if dados != None:
            response = dados.get("response")
            message = dados.get("message")

            if (message != None):
                showinfo("Aviso!", message)

            if bool(response):
                showinfo("FIM DE JOGO!", "Jogador " + str(jogador) + " venceu!")
                fechar_janela(True)
            elif board[i][j] != jogador:
                showinfo("Aviso!", "Essa posição já foi selecionada!")

        retorno_servidor = False
        timer = 0

        while retorno_servidor == False:
            timer+=1
            if timer == 100000:                                         #TODO -> AJEITAR ESSE "TIMER" PRA UM COMPONENTE NATIVO SE POSSÍVEL (N PESQUISEI KK).
                print('teste')
                retorno_servidor = verificar_status_jogada_servidor()
                if not retorno_servidor: timer = 0

def verificar_status_jogada_servidor():
    dados_rcv = obter_retorno_servidor(json.dumps({"clientId": clientId, "jogador": nro_jogador, "message": "aguardando"}))
    new_board = dados_rcv.get("board")

    if new_board != None:
        if new_board != board:
            atualizar_grid()
            return True

    #soquete.close()
    return False

def atualizar_grid():                                                   #TODO -> AJEITAR ISSO AQUI PRA RENDERIZAR CERTO.
    linhas = len(board)
    colunas = len(board[0])

    for i in range(linhas):
        for j in range(colunas):
            labels_grid = tk.Label(gameframe, text="      ", bg= "white" if board[i][j] == 0 else "gray" if board[i][j] == 1 else "black")
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

    if retorno == None:
        showinfo("Aviso!", "Ocorreu um erro ao tentar conectar ao servidor.")
        fechar_janela()

    nro_jogador = retorno.get("nro_jogador")
    print("Conectado ao servidor com sucesso!")

    if nro_jogador == 1:
        print("Você é o primeiro a jogar.")
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


    #root.iconbitmap(bitmap='themes/icons/Gomoku.ico') ----> TODO -> ESPECIFICAR CAMINHOS NO LINUX.
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
    #root.protocol("WM_DELETE_WINDOW", on_window_closing()) ----> TODO -> CONFIGURAR PARA FUNCIONAR QUANDO A JANELA FECHAR (ENVIAR INFO PARA O SERVER).
    root.geometry("700x700")
    root.mainloop()

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

configurar_janela()
conexao_servidor()
inserir_grid()

configurar_mainloop_calls()

#inicia_monitoramento_tabuleiro()

# FIM - LÓGICA TCP CLIENTE
