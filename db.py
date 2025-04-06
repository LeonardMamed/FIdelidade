from supabase import create_client, Client

# 🔑 Substitua pelas suas credenciais reais do Supabase:
SUPABASE_URL = "https://aezalwonapgogcbgtukb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFlemFsd29uYXBnb2djYmd0dWtiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4MTg2NzMsImV4cCI6MjA1OTM5NDY3M30.VosNEGlFYA78cdnYd-gKa_yDb4gfZWUBg-7Uxjl2WD8"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------
# Função: Cadastrar Cliente
# ---------------------
def cadastrar_cliente(nome, cpf):
    try:
        response = supabase.table("clientes").insert({
            "nome": nome,
            "cpf": cpf,
            "pontos": 0,
            "desconto": 0
        }).execute()
        return response
    except Exception as e:
        if "duplicate key" in str(e):
            return f"Erro: CPF {cpf} já está cadastrado."
        return f"Erro inesperado: {str(e)}"

# ---------------------
# Função: Registrar Compra e Atualizar Pontos
# ---------------------
def registrar_compra(cpf, valor):
    try:
        # Buscar cliente pelo CPF
        cliente = supabase.table("clientes").select("*").eq("cpf", cpf).single().execute()
    except Exception:
        return f"Erro: Cliente com CPF {cpf} não encontrado."

    if not cliente.data:
        return f"Erro: Cliente com CPF {cpf} não encontrado."

    # Dados do cliente
    cliente_id = int(cliente.data["id"])
    pontos_atuais = cliente.data["pontos"]
    total_pontos = pontos_atuais + int(valor)

    # Cálculo do desconto
    if total_pontos >= 400:
        desconto = 15
    elif total_pontos >= 200:
        desconto = 10
    elif total_pontos >= 100:
        desconto = 5
    else:
        desconto = 0

    # DEBUG antes de tentar inserir
    print("\n=== DEBUG - TENTANDO INSERIR COMPRA ===")
    print("cliente_id:", cliente_id, type(cliente_id))
    print("valor:", valor, type(valor))
    print("total_pontos:", total_pontos)
    print("========================================\n")

    # Inserir compra
    try:
        resposta = supabase.table("compras").insert({
            "cliente_id": cliente_id,
            "valor": float(valor)
        }).execute()
        print("✔️ Compra registrada:", resposta)
    except Exception as e:
        print("❌ ERRO AO INSERIR NA TABELA COMPRAS:")
        print(e)
        return "Erro ao registrar a compra."

    # Atualizar cliente com novos pontos e desconto
    try:
        supabase.table("clientes").update({
            "pontos": total_pontos,
            "desconto": desconto
        }).eq("id", cliente_id).execute()
    except Exception as e:
        print("❌ ERRO AO ATUALIZAR CLIENTE:")
        print(e)
        return "Erro ao atualizar pontos/desconto."

    return {
        "nome": cliente.data["nome"],
        "cpf": cpf,
        "pontos": total_pontos,
        "desconto": desconto
    }

# ... funções anteriores ...

def usar_pontos_parcial(cpf, pontos_para_usar):
    cliente = supabase.table("clientes").select("*").eq("cpf", cpf).single().execute()

    if not cliente.data:
        return f"Cliente com CPF {cpf} não encontrado."

    pontos_disponiveis = cliente.data["pontos"]

    if pontos_para_usar > pontos_disponiveis:
        return f"Cliente tem apenas {pontos_disponiveis} pontos."

    # Exemplo: 1 ponto = R$ 0,10 de desconto
    valor_desconto = pontos_para_usar * 0.10

    # Subtrair pontos
    pontos_restantes = pontos_disponiveis - pontos_para_usar

    # Atualizar cliente no banco
    supabase.table("clientes").update({
        "pontos": pontos_restantes
    }).eq("id", cliente.data["id"]).execute()

    return {
        "nome": cliente.data["nome"],
        "cpf": cpf,
        "pontos_usados": pontos_para_usar,
        "desconto_em_reais": round(valor_desconto, 2),
        "pontos_restantes": pontos_restantes
    }


