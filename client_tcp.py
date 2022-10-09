import json
import socket
import sys
import tkinter as tk
from tkinter.messagebox import showinfo

#### ROTAS GLOBAIS - CLIENTE

root = tk.Tk()
board = [[0] * 15 for _ in range(15)]
counter = 0

#### ROTAS GLOBAIS - CLIENTE

# INÍCIO - MÉTODOS PRIVADOS DO CLIENTE

def close_game():
    root.destroy()

def insere_grid():
    global gameframe
    gameframe = tk.Frame(root)
    gameframe.pack()
    global i, j

    for i, row in enumerate(board):
        for j, column in enumerate(row):
            L = tk.Label(gameframe, text="    ", bg="white" if board[i][j] == 0 else "white")
            L.grid(row=i, column=j, padx='4', pady='4')
            L.bind('<Button-1>', lambda e, i=i, j=j: grid_on_click(i, j, e))

def grid_on_click(i, j, event):
    global counter
    global jogador

    if board[i][j] == 0:
        color = "gray" if counter % 2 else "black"
        event.widget.config(bg=color)

        if color == "gray":
            board[i][j] = 1
            jogador = 1
        else:
            board[i][j] = 2
            jogador = 2

        counter += 1

        try:
            soquete = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soquete.connect((ip, porta))

            dados_send = json.dumps({"i": i, "j": j, "jogador": jogador, "board": board})
            soquete.send(dados_send.encode())

            dados = soquete.recv(1024)
            dados = json.loads(dados.decode())
            
            response = dados.get("response")
            print(response)
        except:
            showinfo("Aviso!", "Não foi possível conectar ao servidor no momento. Por favor, tente novamente mais tarde. O jogo será encerrado.")
            close_game()
        
        if bool(response):
            showinfo("FIM DE JOGO!", "Jogador " + str(jogador) + " venceu!")
            close_game()
        elif board[i][j] != jogador:
            showinfo("Aviso!", "Essa posição já foi selecionada!")

        soquete.close()

def configura_janela():
    btn = tk.Button(root, text='Imprimir matriz no console', command=imprime_grid)
    btn.pack(side="bottom", pady="20")

    root.iconbitmap('Themes/icons/Gomoku.ico')
    root.winfo_toplevel().title("Socket's Gomoku")

def exibe_grid():
    root.geometry("700x700")
    root.mainloop()

def imprime_grid():
    linhas = len(board)
    colunas = len(board[0])

    for i in range(linhas):
        for j in range(colunas):
            if (j == colunas - 1):
                print("%d" % board[i][j])
            else:
                print("%d" % board[i][j], end=" ")

# FIM - MÉTODOS PRIVADOS DO CLIENTE

# INÍCIO - LÓGICA TCP DO CLIENTE

if len(sys.argv) != 3:
    print('%s <ip> <porta>' % (sys.argv[0]))
    sys.exit(0)

ip = sys.argv[1]
porta = int(sys.argv[2])

configura_janela()
insere_grid()
exibe_grid()

# FIM - LÓGICA TCP DO CLIENTE