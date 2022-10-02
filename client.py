from self import self

from utils import StartGame


def main(self):
    StartGame.insere_botao_imprimir(self)
    StartGame.insere_grid(self)
    StartGame.exibe_grid(self)


#chamadas
main(self)

