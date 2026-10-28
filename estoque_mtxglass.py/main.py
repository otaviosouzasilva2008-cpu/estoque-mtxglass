
import json
import os
import datetime

estoque = []
historico = []

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ESTOQUE = os.path.join(PASTA_PROJETO, "estoque.json")
ARQUIVO_HISTORICO = os.path.join(PASTA_PROJETO, "historico.json")


def carregar_estoque():
    """Carrega o estoque e verifica se o arquivo contém uma lista."""
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            with open(ARQUIVO_ESTOQUE, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, list):
                print("O arquivo de estoque está em formato inválido.")
                print("O arquivo foi preservado; verifique-o antes de continuar.")
                return []

            campos_obrigatorios = {
                "codigo", "tipo", "espessura", "largura", "altura", "quantidade"
            }

            for item in dados:
                if not isinstance(item, dict) or not campos_obrigatorios.issubset(item):
                    print("Há um registro inválido no arquivo de estoque.")
                    print("O arquivo foi preservado; verifique-o antes de continuar.")
                    return []

                if (
                    not isinstance(item["quantidade"], int)
                    or isinstance(item["quantidade"], bool)
                    or item["quantidade"] < 0
                ):
                    print("Há uma quantidade inválida no arquivo de estoque.")
                    print("O arquivo foi preservado; verifique-o antes de continuar.")
                    return []

            return dados

        except (json.JSONDecodeError, OSError) as erro:
            print(f"Não foi possível carregar o estoque: {erro}")
            print("O arquivo original não foi apagado nem substituído.")
            return []

    return []


def salvar_estoque():
    """Salva o estoque e informa se houve falha de gravação."""
    try:
        with open(ARQUIVO_ESTOQUE, "w", encoding="utf-8") as arquivo:
            json.dump(estoque, arquivo, ensure_ascii=False, indent=4)
        return True
    except OSError as erro:
        print(f"ERRO: não foi possível salvar o estoque: {erro}")
        print("Confira as permissões e o espaço disponível no disco.")
        return False


def carregar_historico():
    """Carrega o histórico e verifica se o arquivo contém uma lista."""
    if os.path.exists(ARQUIVO_HISTORICO):
        try:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            if not isinstance(dados, list):
                print("O arquivo de histórico está em formato inválido.")
                print("O arquivo foi preservado; verifique-o antes de continuar.")
                return []

            for registro in dados:
                if not isinstance(registro, dict):
                    print("Há um registro inválido no histórico.")
                    print("O arquivo foi preservado; verifique-o antes de continuar.")
                    return []

            return dados

        except (json.JSONDecodeError, OSError) as erro:
            print(f"Não foi possível carregar o histórico: {erro}")
            print("O arquivo original não foi apagado nem substituído.")
            return []

    return []


def salvar_historico():
    """Salva o histórico e informa se houve falha de gravação."""
    try:
        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
            json.dump(historico, arquivo, ensure_ascii=False, indent=4)
        return True
    except OSError as erro:
        print(f"ERRO: não foi possível salvar o histórico: {erro}")
        print("Confira as permissões e o espaço disponível no disco.")
        return False


def cadastrar_vidro():
    print("\n--- CADASTRO DE VIDRO ---")

    codigo = input("Código do vidro: ").strip()

    if not codigo:
        print("O código não pode ficar vazio.")
        return

    for vidro in estoque:
        if vidro["codigo"] == codigo:
            print("Esse código já está cadastrado!")
            return

    tipo = input("Tipo de vidro: ").strip()
    espessura = input("Espessura em mm: ").strip()
    largura = input("Largura em cm: ").strip()
    altura = input("Altura em cm: ").strip()
    quantidade = input("Quantidade inicial: ").strip()

    if not tipo:
        print("O tipo de vidro não pode ficar vazio.")
        return

    if not all([espessura, largura, altura, quantidade]):
        print("Preencha todos os campos.")
        return

    try:
        espessura = float(espessura.replace(",", "."))
        largura = float(largura.replace(",", "."))
        altura = float(altura.replace(",", "."))
        quantidade = int(quantidade)

        if espessura <= 0 or largura <= 0 or altura <= 0:
            print("As medidas devem ser maiores que zero.")
            return

        if quantidade < 0:
            print("A quantidade não pode ser negativa.")
            return

    except ValueError:
        print("Digite medidas válidas e uma quantidade inteira.")
        return

    vidro = {
        "codigo": codigo,
        "tipo": tipo,
        "espessura": espessura,
        "largura": largura,
        "altura": altura,
        "quantidade": quantidade
    }

    estoque.append(vidro)

    if salvar_estoque():
        print("Vidro cadastrado com sucesso!")
    else:
        estoque.remove(vidro)
        print("O cadastro foi cancelado porque não foi possível salvar.")


def pesquisar_vidro():
    print("\n--- PESQUISAR VIDRO ---")

    codigo = input("Digite o código do vidro: ").strip()

    for vidro in estoque:
        if vidro["codigo"] == codigo:
            print("\n--- VIDRO ENCONTRADO ---")
            print("Código:", vidro["codigo"])
            print("Tipo:", vidro["tipo"])
            print("Espessura:", vidro["espessura"], "mm")
            print(
                "Dimensões:",
                vidro["largura"], "x", vidro["altura"], "cm"
            )
            print("Quantidade:", vidro["quantidade"])
            return

    print("Vidro não encontrado.")


def consultar_historico():
    print("\n--- HISTÓRICO DE MOVIMENTAÇÕES ---")

    if not historico:
        print("Nenhuma movimentação registrada.")
        return

    for registro in historico:
        print("-------------------------")
        print("Tipo:", registro.get("tipo", "Não informado"))
        print("Código do vidro:", registro.get("codigo", "Não informado"))
        print("Tipo de vidro:", registro.get("vidro", "Não informado"))
        print("Quantidade:", registro.get("quantidade", "Não informada"))
        print("Data e hora:", registro.get("data_hora", "Registro antigo"))

        if "motivo" in registro:
            print("Motivo da perda:", registro["motivo"])


def verificar_estoque_baixo():
    print("\n--- ALERTA DE ESTOQUE BAIXO ---")

    encontrou = False

    for vidro in estoque:
        if vidro["quantidade"] <= 5:
            print("-------------------------")
            print("Código:", vidro["codigo"])
            print("Tipo:", vidro["tipo"])
            print("Quantidade disponível:", vidro["quantidade"])
            print("ATENÇÃO: Estoque baixo!")
            encontrou = True

    if not encontrou:
        print("Nenhum vidro com estoque baixo.")


def resumo_estoque():
    print("\n===== RESUMO DO ESTOQUE =====")

    total_tipos = len(estoque)
    total_unidades = sum(vidro["quantidade"] for vidro in estoque)

    print("Tipos de vidro cadastrados:", total_tipos)
    print("Total de unidades em estoque:", total_unidades)


def consultar_estoque():
    print("\n--- ESTOQUE DE VIDROS ---")

    if not estoque:
        print("Nenhum vidro cadastrado.")
        return

    for vidro in estoque:
        print("-------------------------")
        print("Código:", vidro["codigo"])
        print("Tipo:", vidro["tipo"])
        print("Espessura:", vidro["espessura"], "mm")
        print(
            "Dimensões:",
            vidro["largura"], "x", vidro["altura"], "cm"
        )
        print("Quantidade:", vidro["quantidade"])


def registrar_perda():
    print("\n--- REGISTRAR QUEBRA OU PERDA ---")

    codigo = input("Código do vidro: ").strip()
    vidro_encontrado = None

    for vidro in estoque:
        if vidro["codigo"] == codigo:
            vidro_encontrado = vidro
            break

    if vidro_encontrado is None:
        print("Vidro não encontrado.")
        return

    try:
        quantidade = int(input("Quantidade perdida: "))

        if quantidade <= 0:
            print("A quantidade deve ser maior que zero.")
            return

        if quantidade > vidro_encontrado["quantidade"]:
            print("Estoque insuficiente para registrar essa perda.")
            return

    except ValueError:
        print("Digite uma quantidade inteira válida.")
        return

    motivo = input("Motivo da perda (quebra, risco etc.): ").strip()

    if not motivo:
        print("Informe o motivo da perda.")
        return

    vidro_encontrado["quantidade"] -= quantidade

    registro = {
        "tipo": "perda",
        "codigo": vidro_encontrado["codigo"],
        "vidro": vidro_encontrado["tipo"],
        "quantidade": quantidade,
        "motivo": motivo,
        "data_hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    historico.append(registro)

    estoque_salvo = salvar_estoque()
    historico_salvo = salvar_historico()

    if estoque_salvo and historico_salvo:
        print("Perda registrada com sucesso!")
        print("Motivo:", motivo)
        print("Quantidade perdida:", quantidade)
        print("Quantidade atual:", vidro_encontrado["quantidade"])
    else:
        print("ATENÇÃO: ocorreu um erro ao salvar os dados.")
        print("Confira os arquivos antes de continuar.")


def movimentar_estoque(tipo_movimento):
    if tipo_movimento not in ("entrada", "saida"):
        print("Tipo de movimentação inválido.")
        return

    print(f"\n--- REGISTRAR {tipo_movimento.upper()} ---")

    codigo = input("Código do vidro: ").strip()
    vidro_encontrado = None

    for vidro in estoque:
        if vidro["codigo"] == codigo:
            vidro_encontrado = vidro
            break

    if vidro_encontrado is None:
        print("Vidro não encontrado. Cadastre-o primeiro.")
        return

    try:
        quantidade = int(input("Quantidade: "))

        if quantidade <= 0:
            print("A quantidade deve ser maior que zero.")
            return

    except ValueError:
        print("Digite uma quantidade inteira válida.")
        return

    if tipo_movimento == "saida":
        if quantidade > vidro_encontrado["quantidade"]:
            print("Estoque insuficiente! Saída não realizada.")
            return

    quantidade_anterior = vidro_encontrado["quantidade"]

    if tipo_movimento == "entrada":
        vidro_encontrado["quantidade"] += quantidade
    else:
        vidro_encontrado["quantidade"] -= quantidade

    registro = {
        "tipo": tipo_movimento,
        "codigo": vidro_encontrado["codigo"],
        "vidro": vidro_encontrado["tipo"],
        "quantidade": quantidade,
        "data_hora": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    historico.append(registro)

    estoque_salvo = salvar_estoque()
    historico_salvo = salvar_historico()

    if estoque_salvo and historico_salvo:
        if tipo_movimento == "entrada":
            print("Entrada registrada com sucesso!")
        else:
            print("Saída registrada com sucesso!")

        print("Quantidade atual:", vidro_encontrado["quantidade"])
    else:
        print("ATENÇÃO: ocorreu um erro ao salvar os dados.")
        print("Confira os arquivos antes de continuar.")
        print("A quantidade foi alterada na memória; reinicie apenas após verificar os arquivos.")


print("Pasta do projeto:")
print(PASTA_PROJETO)

estoque = carregar_estoque()
historico = carregar_historico()

while True:
    print("\n===================================")
    print("     SISTEMA DE ESTOQUE DE VIDROS")
    print("===================================")
    print("1 - Cadastrar vidro")
    print("2 - Consultar estoque")
    print("3 - Registrar entrada")
    print("4 - Registrar saída")
    print("5 - Registrar quebra ou perda")
    print("6 - Pesquisar vidro pelo código")
    print("7 - Verificar estoque baixo")
    print("8 - Consultar histórico de movimentações")
    print("9 - Resumo do estoque")
    print("0 - Sair")

    opcao = input("Digite a opção desejada: ").strip()

    if opcao == "1":
        cadastrar_vidro()
    elif opcao == "2":
        consultar_estoque()
    elif opcao == "3":
        movimentar_estoque("entrada")
    elif opcao == "4":
        movimentar_estoque("saida")
    elif opcao == "5":
        registrar_perda()
    elif opcao == "6":
        pesquisar_vidro()
    elif opcao == "7":
        verificar_estoque_baixo()
    elif opcao == "8":
        consultar_historico()
    elif opcao == "9":
        resumo_estoque()
    elif opcao == "0":
        print("Sistema encerrado.")
        break
    else:
        print("Opção inválida. Tente novamente.")
