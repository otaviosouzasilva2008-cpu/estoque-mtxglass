
import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash


app = Flask(__name__)
app.secret_key = "mtxglass-chave-local"

PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ESTOQUE = os.path.join(PASTA_PROJETO, "estoque.json")
ARQUIVO_HISTORICO = os.path.join(PASTA_PROJETO, "historico.json")


# CARREGAR O ESTOQUE
def carregar_estoque():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        return []

    try:
        with open(ARQUIVO_ESTOQUE, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return dados

        raise ValueError("O arquivo de estoque precisa conter uma lista.")

    except json.JSONDecodeError as erro:
        raise ValueError("O arquivo de estoque contém JSON inválido.") from erro


# SALVAR O ESTOQUE
def salvar_estoque(estoque):
    with open(ARQUIVO_ESTOQUE, "w", encoding="utf-8") as arquivo:
        json.dump(estoque, arquivo, ensure_ascii=False, indent=4)


# REGISTRAR MOVIMENTAÇÕES NO HISTÓRICO
def salvar_historico(tipo, vidro, quantidade):
    historico = []

    if os.path.exists(ARQUIVO_HISTORICO):
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
            historico = json.load(arquivo)

        if not isinstance(historico, list):
            raise ValueError("O histórico precisa ser uma lista.")

    registro = {
        "tipo": tipo,
        "codigo": vidro.get("codigo", ""),
        "vidro": vidro.get("tipo", ""),
        "quantidade": quantidade,
        "data_hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    historico.append(registro)

    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=4)


# LOCALIZAR VIDRO PELO CÓDIGO
def localizar_vidro(estoque, codigo):
    for vidro in estoque:
        if str(vidro.get("codigo", "")).lower() == codigo.lower():
            return vidro

    return None


# PÁGINA INICIAL E CONSULTA DE ESTOQUE
@app.route("/")
def inicio():
    estoque = carregar_estoque()
    busca = request.args.get("busca", "").strip()

    if busca:
        estoque = [
            vidro for vidro in estoque
            if busca.lower() in str(vidro.get("codigo", "")).lower()
        ]

    return render_template(
        "index.html",
        estoque=estoque,
        busca=busca
    )


# CADASTRAR VIDRO
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        tipo = request.form.get("tipo", "").strip()
        espessura = request.form.get("espessura", "").strip().replace(",", ".")
        largura = request.form.get("largura", "").strip().replace(",", ".")
        altura = request.form.get("altura", "").strip().replace(",", ".")
        quantidade = request.form.get("quantidade", "").strip()

        if not all([codigo, tipo, espessura, largura, altura, quantidade]):
            flash("Preencha todos os campos.")
            return redirect(url_for("cadastrar"))

        try:
            espessura = float(espessura)
            largura = float(largura)
            altura = float(altura)
            quantidade = int(quantidade)
        except ValueError:
            flash("Confira os números digitados.")
            return redirect(url_for("cadastrar"))

        if (
            espessura <= 0
            or largura <= 0
            or altura <= 0
            or quantidade < 0
        ):
            flash(
                "As medidas devem ser positivas e a quantidade "
                "não pode ser negativa."
            )
            return redirect(url_for("cadastrar"))

        try:
            estoque = carregar_estoque()
        except (OSError, ValueError):
            flash("Não foi possível ler os dados do estoque.")
            return redirect(url_for("cadastrar"))

        if any(
            str(item.get("codigo", "")).lower() == codigo.lower()
            for item in estoque
        ):
            flash("Já existe um vidro cadastrado com esse código.")
            return redirect(url_for("cadastrar"))

        vidro = {
            "codigo": codigo,
            "tipo": tipo,
            "espessura": espessura,
            "largura": largura,
            "altura": altura,
            "quantidade": quantidade
        }

        estoque.append(vidro)

        try:
            salvar_estoque(estoque)
        except OSError:
            flash("Não foi possível salvar o cadastro.")
            return redirect(url_for("cadastrar"))

        flash("Vidro cadastrado com sucesso!")
        return redirect(url_for("inicio"))

    return render_template("cadastro.html")


# REGISTRAR ENTRADA
@app.route("/entrada", methods=["GET", "POST"])
def entrada():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        quantidade_texto = request.form.get("quantidade", "").strip()

        if not codigo:
            flash("Informe o código do vidro.")
            return redirect(url_for("entrada"))

        try:
            quantidade = int(quantidade_texto)
        except ValueError:
            flash("Digite uma quantidade inteira válida.")
            return redirect(url_for("entrada"))

        if quantidade <= 0:
            flash("A quantidade deve ser maior que zero.")
            return redirect(url_for("entrada"))

        try:
            estoque = carregar_estoque()
        except (OSError, ValueError):
            flash("Não foi possível ler os dados do estoque.")
            return redirect(url_for("entrada"))

        vidro_encontrado = localizar_vidro(estoque, codigo)

        if vidro_encontrado is None:
            flash("Vidro não encontrado. Confira o código cadastrado.")
            return redirect(url_for("entrada"))

        try:
            quantidade_anterior = int(vidro_encontrado.get("quantidade", 0))
        except (ValueError, TypeError):
            flash("A quantidade cadastrada para esse vidro é inválida.")
            return redirect(url_for("entrada"))

        vidro_encontrado["quantidade"] = quantidade_anterior + quantidade

        try:
            salvar_estoque(estoque)
            salvar_historico("entrada", vidro_encontrado, quantidade)
        except (OSError, ValueError, TypeError):
            flash("Não foi possível salvar a entrada ou seu histórico.")
            return redirect(url_for("entrada"))

        flash("Entrada registrada com sucesso!")
        return redirect(url_for("inicio"))

    return render_template("entrada.html")


# REGISTRAR SAÍDA
@app.route("/saida", methods=["GET", "POST"])
def saida():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        quantidade_texto = request.form.get("quantidade", "").strip()

        if not codigo:
            flash("Informe o código do vidro.")
            return redirect(url_for("saida"))

        try:
            quantidade = int(quantidade_texto)
        except ValueError:
            flash("Digite uma quantidade inteira válida.")
            return redirect(url_for("saida"))

        if quantidade <= 0:
            flash("A quantidade deve ser maior que zero.")
            return redirect(url_for("saida"))

        try:
            estoque = carregar_estoque()
        except (OSError, ValueError):
            flash("Não foi possível ler os dados do estoque.")
            return redirect(url_for("saida"))

        vidro_encontrado = localizar_vidro(estoque, codigo)

        if vidro_encontrado is None:
            flash("Vidro não encontrado. Confira o código cadastrado.")
            return redirect(url_for("saida"))

        try:
            quantidade_atual = int(vidro_encontrado.get("quantidade", 0))
        except (ValueError, TypeError):
            flash("A quantidade cadastrada para esse vidro é inválida.")
            return redirect(url_for("saida"))

        if quantidade_atual < 0:
            flash("A quantidade cadastrada não pode ser negativa.")
            return redirect(url_for("saida"))

        if quantidade > quantidade_atual:
            flash(
                f"Estoque insuficiente. Disponível: "
                f"{quantidade_atual} unidades."
            )
            return redirect(url_for("saida"))

        vidro_encontrado["quantidade"] = quantidade_atual - quantidade

        try:
            salvar_estoque(estoque)
            salvar_historico("saida", vidro_encontrado, quantidade)
        except (OSError, ValueError, TypeError):
            flash("Não foi possível salvar a saída ou seu histórico.")
            return redirect(url_for("saida"))

        flash("Saída registrada com sucesso!")
        return redirect(url_for("inicio"))

    return render_template("saida.html")


# CONSULTAR HISTÓRICO
@app.route("/historico")
def historico():
    try:
        if not os.path.exists(ARQUIVO_HISTORICO):
            registros = []
        else:
            with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as arquivo:
                registros = json.load(arquivo)

            if not isinstance(registros, list):
                flash("O arquivo de histórico contém um formato inválido.")
                registros = []

    except (OSError, json.JSONDecodeError):
        flash("Não foi possível ler o histórico.")
        registros = []

    return render_template("historico.html", historico=registros)


# REGISTRAR PERDAS
@app.route("/perdas", methods=["GET", "POST"])
def perdas():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        quantidade_texto = request.form.get("quantidade", "").strip()

        if not codigo:
            flash("Informe o código do vidro.", "perdas")
            return redirect(url_for("perdas"))

        try:
            quantidade = int(quantidade_texto)
        except ValueError:
            flash("Digite uma quantidade inteira válida.", "perdas")
            return redirect(url_for("perdas"))

        if quantidade <= 0:
            flash("A quantidade deve ser maior que zero.", "perdas")
            return redirect(url_for("perdas"))

        try:
            estoque = carregar_estoque()
        except (OSError, ValueError):
            flash("Não foi possível ler os dados do estoque.", "perdas")
            return redirect(url_for("perdas"))

        vidro_encontrado = localizar_vidro(estoque, codigo)

        if vidro_encontrado is None:
            flash(
                "Vidro não encontrado. Confira o código cadastrado.",
                "perdas"
            )
            return redirect(url_for("perdas"))

        try:
            quantidade_atual = int(vidro_encontrado.get("quantidade", 0))
        except (ValueError, TypeError):
            flash(
                "A quantidade cadastrada para esse vidro é inválida.",
                "perdas"
            )
            return redirect(url_for("perdas"))

        if quantidade_atual < 0:
            flash(
                "A quantidade cadastrada não pode ser negativa.",
                "perdas"
            )
            return redirect(url_for("perdas"))

        if quantidade > quantidade_atual:
            flash(
                f"Estoque insuficiente. Disponível: "
                f"{quantidade_atual} unidades.",
                "perdas"
            )
            return redirect(url_for("perdas"))

        vidro_encontrado["quantidade"] = quantidade_atual - quantidade

        try:
            salvar_estoque(estoque)
            salvar_historico("perda", vidro_encontrado, quantidade)
        except (OSError, ValueError, TypeError):
            flash(
                "Não foi possível salvar a perda ou seu histórico.",
                "perdas"
            )
            return redirect(url_for("perdas"))

        flash("Perda registrada com sucesso!", "perdas")
        return redirect(url_for("inicio"))

    return render_template("perdas.html")


if __name__ == "__main__":
    app.run(debug=False)