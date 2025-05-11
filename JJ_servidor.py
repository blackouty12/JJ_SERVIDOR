from flask import Flask, request, jsonify
from difflib import get_close_matches
import json
import os
import openai

app = Flask(__name__)
ARQUIVO_CONHECIMENTO = "conhecimento.json"
openai.api_key = os.getenv("OPENAI_API_KEY")

# Carrega conhecimento local
def carregar_conhecimento():
    if os.path.exists(ARQUIVO_CONHECIMENTO):
        with open(ARQUIVO_CONHECIMENTO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Salva novas informações
def salvar_conhecimento(dados):
    with open(ARQUIVO_CONHECIMENTO, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# Busca respostas com correspondência aproximada
def procurar_resposta_local(pergunta, conhecimento):
    pergunta = pergunta.lower().strip()
    chaves = list(conhecimento.keys())
    parecida = get_close_matches(pergunta, chaves, n=1, cutoff=0.65)
    if parecida:
        return conhecimento[parecida[0]]
    return None

# Consulta a OpenAI (se necessário)
def consultar_openai(pergunta):
    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": pergunta}],
            temperature=0.5
        )
        return resposta.choices[0].message.content.strip()
    except Exception:
        return "Não foi possível consultar a inteligência externa no momento."

# Rota principal de resposta
@app.route("/responder", methods=["POST"])
def responder():
    dados = request.json
    pergunta = dados.get("pergunta", "").strip()
    conhecimento = carregar_conhecimento()
    resposta = procurar_resposta_local(pergunta, conhecimento)

    if not resposta:
        resposta = consultar_openai(pergunta)
        conhecimento[pergunta] = resposta
        salvar_conhecimento(conhecimento)

    return jsonify({"resposta": resposta})

# Rota para ensino manual
@app.route("/ensinar", methods=["POST"])
def ensinar():
    dados = request.json
    pergunta = dados.get("pergunta", "").lower().strip()
    resposta = dados.get("resposta", "").strip()

    if not pergunta or not resposta:
        return jsonify({"erro": "Pergunta e resposta são obrigatórias"}), 400

    conhecimento = carregar_conhecimento()
    conhecimento[pergunta] = resposta
    salvar_conhecimento(conhecimento)

    return jsonify({"mensagem": "Informação registrada com sucesso."})

if __name__ == "__main__":
    app.run()
