from flask import Flask, request, jsonify
from difflib import get_close_matches
import json
import os
import openai

# Pegue sua chave da variável de ambiente no Render
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
ARQUIVO_CONHECIMENTO = "conhecimento.json"

def carregar_conhecimento():
    try:
        with open(ARQUIVO_CONHECIMENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_conhecimento(dados):
    with open(ARQUIVO_CONHECIMENTO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

def procurar_resposta_local(pergunta, conhecimento):
    pergunta = pergunta.lower()
    chaves = list(conhecimento.keys())
    parecida = get_close_matches(pergunta, chaves, n=1, cutoff=0.6)
    if parecida:
        return conhecimento[parecida[0]]
    return None

def consultar_openai(pergunta):
    resposta = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": pergunta}],
        temperature=0.7
    )
    return resposta.choices[0].message.content.strip()

@app.route("/responder", methods=["POST"])
def responder():
    dados = request.json
    pergunta = dados.get("pergunta", "").lower()

    conhecimento = carregar_conhecimento()
    resposta = procurar_resposta_local(pergunta, conhecimento)

    if not resposta:
        resposta = consultar_openai(pergunta)
        conhecimento[pergunta] = resposta
        salvar_conhecimento(conhecimento)

    return jsonify({"resposta": resposta})

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
    app.run()
