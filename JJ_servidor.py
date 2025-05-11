from flask import Flask, request, jsonify
from difflib import get_close_matches
import json
import os

app = Flask(__name__)
ARQUIVO_CONHECIMENTO = "conhecimento.json"

# Carrega o conhecimento existente
def carregar_conhecimento():
    try:
        with open(ARQUIVO_CONHECIMENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Salva o conhecimento atualizado
def salvar_conhecimento(dados):
    with open(ARQUIVO_CONHECIMENTO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Rota para responder perguntas
@app.route("/responder", methods=["POST"])
def responder():
    dados = request.json
    pergunta = dados.get("pergunta", "").lower()
    conhecimento = carregar_conhecimento()
    chaves = list(conhecimento.keys())
    parecida = get_close_matches(pergunta, chaves, n=1, cutoff=0.6)

    if parecida:
        resposta = conhecimento[parecida[0]]
    else:
        resposta = "Desculpe, não sei responder isso ainda."

    return jsonify({"resposta": resposta})

# Rota para ensinar uma nova pergunta e resposta
@app.route("/ensinar", methods=["POST"])
def ensinar():
    dados = request.json
    pergunta = dados.get("pergunta", "").lower()
    resposta = dados.get("resposta", "")

    if not pergunta or not resposta:
        return jsonify({"erro": "Pergunta e resposta são obrigatórias"}), 400

    conhecimento = carregar_conhecimento()
    conhecimento[pergunta] = resposta
    salvar_conhecimento(conhecimento)

    return jsonify({"mensagem": "Aprendido com sucesso!"})

if __name__ == "__main__":
    app.run(debug=True)
