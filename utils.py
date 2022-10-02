import tkinter as tk
from tkinter.messagebox import showinfo


# rotas globais
root = tk.Tk()
board = [[0] * 15 for _ in range(15)]
counter = 0


class StartGame:

    def __init__(self):
        super(StartGame, self).__init__()

    def imprime_grid(self):
        linhas = len(board)
        colunas = len(board[0])

        for i in range(linhas):
            for j in range(colunas):
                if (j == colunas - 1):
                    print("%d" % board[i][j])
                else:
                    print("%d" % board[i][j], end=" ")

    def exibe_grid(self):
        root.geometry("700x700")
        root.mainloop()

    def insere_botao_imprimir(self):
        btn = tk.Button(root, text='Imprimir matriz no console', command=StartGame.imprime_grid)
        btn.pack(side="bottom", pady="20")


    def verifica_linha(i, jogador_atual):
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

    def verifica_coluna(j, jogador_atual):
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

    def verifica_diagonal(jogador):
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


    def return_coord_jogadas(i, j):
        return (i, j)
    def verifica_tabuleiro(i, j, jogador):
        if StartGame.verifica_linha(i, jogador_atual=jogador):
            return True
        if StartGame.verifica_coluna(j, jogador_atual=jogador):
            return True
        if StartGame.verifica_diagonal(jogador):
            return True

    def on_click(self, i, j, event):
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
            if StartGame.verifica_tabuleiro(i, j, jogador):
                showinfo("FIM DE JOGO!", "Jogador " + str(jogador) + " venceu!")
                StartGame.close_game(self)

        else:
            showinfo("Aviso!", "Essa posição já foi selecionada!")


        StartGame.return_coord_jogadas(i, j)
    def close_game(self):
        root.destroy()

    def insere_grid(self):
        global gameframe
        gameframe = tk.Frame(root)
        gameframe.pack()

        for i, row in enumerate(board):
            for j, column in enumerate(row):
                L = tk.Label(gameframe, text="    ", bg="white" if board[i][j] == 0 else "white")
                L.grid(row=i, column=j, padx='4', pady='4')
                L.bind('<Button-1>', lambda e, i=i, j=j: StartGame.on_click(self, i, j, e))

