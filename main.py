from db import registrar_compra

cpf = input("Digite o CPF do cliente: ")
valor = float(input("Digite o valor da compra (R$): "))

resposta = registrar_compra(cpf, valor)

print("Resultado da compra:")
print(resposta)

from db import usar_pontos_parcial

cpf = input("CPF do cliente: ")
pontos = int(input("Quantos pontos deseja usar? "))

resposta = usar_pontos_parcial(cpf, pontos)
print("Resultado:", resposta)
