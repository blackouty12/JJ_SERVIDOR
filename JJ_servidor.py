import wikipedia
from PyDictionary import PyDictionary
dictionary = PyDictionary()

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
        # Tenta responder com dicionário
        significado = dictionary.meaning(pergunta)
        if significado:
            primeira_def = list(significado.values())[0][0]
            resposta = f"Segundo o dicionário: {primeira_def}"
        else:
            # Tenta responder com Wikipedia
            try:
                resposta = wikipedia.summary(pergunta, sentences=2, lang="pt")
            except:
                resposta = "Desculpe, não encontrei nada sobre isso."

    return jsonify({"resposta": resposta})
