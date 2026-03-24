from models.grupo import Grupo
from models.pessoas import Pessoa

irlan = Pessoa ("irlan","irlansales01@gmail.com",1412,"M")
kezia = Pessoa ("kezia","kezinha@gmail.com",1998, "F")

pizza = Grupo ("Pizza", irlan)

pizza.adicionar_pessoas(kezia)
print(pizza)

pizza.remover_pessoas(kezia)
pizza.remover_pessoas(irlan)
pizza.remover_pessoas(kezia)
print(pizza)

