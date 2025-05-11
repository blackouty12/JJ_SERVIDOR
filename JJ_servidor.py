from flask import Flask, request, jsonify
from difflib import get_close_matches
import json
import os
import wikipedia
from PyDictionary import PyDictionary

app = Flask(__name__)
ARQUIVO_CONHECIMENTO = "conhecimento.json"
dictionary = PyDictionary()

# Configura a Wikipedia para português
wikipedia.set_lang("pt")

def carregar_conhecimento():
    try:
        with open(ARQUIVO_CONHECIMENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_conhecimento(dados):
    with open(ARQUIVO_CONHECIMENTO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/")
def inicio():
    return "Servidor da JJ online!"

@app.route("/responder", methods=["POST"])
def responder():
    dados = request.get_json()
    pergunta = dados.get("pergunta", "").lower()
    conhecimento = carregar_conhecimento()
    chaves = list(conhecimento.keys())
    parecida = get_close_matches(pergunta, chaves, n=1, cutoff=0.6)

    if parecida:
        resposta = conhecimento[parecida[0]]
    else:
        # Tenta buscar no dicionário
        significado = dictionary.meaning(pergunta)
        if significado:
            primeira_def = list(significado.values())[0][0]
            resposta = f"Segundo o dicionário: {primeira_def}"
        else:
            # Tenta buscar na Wikipedia
            try:
                resposta = wikipedia.summary(pergunta, sentences=2)
            except:
                resposta = "Desculpe, não sei responder isso ainda."

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
    app.run(debug=True)
