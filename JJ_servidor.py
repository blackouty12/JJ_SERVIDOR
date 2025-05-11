from flask import Flask, request, jsonify
from difflib import get_close_matches
import json

app = Flask(__name__)
ARQUIVO_CONHECIMENTO = "conhecimento.json"

def carregar_conhecimento():
    try:
        with open(ARQUIVO_CONHECIMENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

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
    resposta = conhecimento[parecida[0]] if parecida else "Desculpe, não entendi."
    return jsonify({"resposta": resposta})

if __name__ == "__main__":
    app.run()
