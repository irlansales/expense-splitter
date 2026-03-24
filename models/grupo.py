class Grupo:
    def __init__(self, nome, criador):
        self.nome = nome
        self.criador = criador
        self.participantes = [criador]
    def __str__(self):
        pessoas = []
        for participante in self.participantes:
            pessoas.append(participante.nome)
        pessoas_str = " e ".join(pessoas)    

        return f' sou o grupo {self.nome}, criado por {self.criador.nome} e meus participantes são {pessoas_str}'
    def adicionar_pessoas(self,usuario):
        self.participantes.append(usuario)


    def remover_pessoas(self,usuario):
        if len(self.participantes) >= 2:
            self.participantes.remove(usuario)
        else:
            print ( f" {usuario.nome} nao pode ser removid{'a' if usuario.sexo=='F' else 'o'} pois o grupo não pode ficar vazio")

    