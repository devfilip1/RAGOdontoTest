"""Juiz local para os critérios subjetivos (research D8).

Uma chamada por critério, resposta binária com esquema JSON. As notas do juiz ficam em bloco
separado do placar e nunca entram no "acertou/errou" do item.
"""
import json
import os

JUDGE_TEMPERATURE = 0
JUDGE_SEED = 42

CRITERIA = {
    "relevance": {
        "label": "Relevância",
        "rubric": "A resposta trata do que o cliente perguntou. Dizer que não tem a informação pedida também é tratar da pergunta.",
        "yes": "Pergunta: \"Quanto custa a limpeza?\" Resposta: \"A limpeza custa de R$ 120 a R$ 250.\"",
        "no": "Pergunta: \"Quanto custa a limpeza?\" Resposta: \"O implante é uma solução definitiva para o seu sorriso.\"",
    },
    "tone": {
        "label": "Tom",
        "rubric": "O tom é cordial e profissional, como o de um atendente de clínica falando com um cliente.",
        "yes": "\"Claro! A limpeza leva de 30 a 50 minutos. Posso ajudar com mais alguma dúvida?\"",
        "no": "\"Já falei que não sei. Leia o site.\"",
    },
    "scheduling": {
        "label": "Condução para o agendamento",
        "rubric": "A resposta convida o cliente, de forma explícita, a agendar uma consulta ou avaliação.",
        "yes": "\"O clareamento custa de R$ 500 a R$ 1.500. Vamos agendar sua avaliação?\"",
        "no": "\"O clareamento custa de R$ 500 a R$ 1.500.\"",
    },
    "conciseness": {
        "label": "Objetividade",
        "rubric": "A resposta é direta: entrega a informação sem rodeios, sem repetir a pergunta e sem listar informações que não foram pedidas.",
        "yes": "\"A extração simples custa de R$ 150 a R$ 300.\"",
        "no": "\"Você perguntou quanto custa a extração. Essa é uma ótima pergunta! Antes de responder, vale explicar todos os nossos procedimentos...\"",
    },
    "faithfulness": {
        "label": "Fidelidade (afirmações)",
        "rubric": "Tudo o que a resposta afirma sobre a clínica e os procedimentos está nos trechos disponíveis. Convites para agendar e frases de cortesia não contam como afirmação.",
        "yes": "Trecho: \"Tempo: 3 a 6 meses\". Resposta: \"O implante leva de 3 a 6 meses.\"",
        "no": "Trecho: \"Tempo: 3 a 6 meses\". Resposta: \"O implante leva de 3 a 6 meses e é feito com anestesia geral.\"",
        "needs_chunks": True,
    },
}

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"motivo": {"type": "string"}, "veredito": {"type": "boolean"}},
    "required": ["motivo", "veredito"],
}

PROMPT = """Você é um avaliador rigoroso das respostas do assistente virtual de uma clínica odontológica.
Avalie apenas o critério abaixo e responda em JSON.

CRITÉRIO: {label}
{rubric}

Exemplo que atende ao critério: {yes}
Exemplo que não atende ao critério: {no}

PERGUNTA DO CLIENTE:
{question}
{chunks}
RESPOSTA DO ASSISTENTE:
{answer}

Escreva o motivo em uma frase curta e depois o veredito: true se a resposta atende ao critério, false se não atende."""


def judge_model_name(chat_model):
    return os.getenv("OLLAMA_JUDGE_MODEL") or chat_model


def build_prompt(criterion, question, answer, chunks):
    spec = CRITERIA[criterion]
    chunk_block = ""
    if spec.get("needs_chunks"):
        chunk_block = "\nTRECHOS DISPONÍVEIS AO ASSISTENTE:\n" + "\n---\n".join(chunks) + "\n"
    return PROMPT.format(
        label=spec["label"], rubric=spec["rubric"], yes=spec["yes"], no=spec["no"],
        question=question, answer=answer, chunks=chunk_block,
    )


def parse_verdict(content):
    """Lê a saída do juiz. JSON inválido vira veredito None, sem derrubar a execução."""
    try:
        data = json.loads(content)
        verdict = data["veredito"]
        if not isinstance(verdict, bool):
            raise ValueError(f"veredito não é booleano: {verdict!r}")
        return {"verdict": verdict, "reason": str(data.get("motivo", ""))}
    except (ValueError, KeyError, TypeError) as error:
        return {"verdict": None, "reason": f"saída inválida do juiz: {error}"}


def make_judge(model, host=None, chat=None):
    """Devolve judge(question, answer, chunks) -> {critério: {verdict, reason}}."""
    if chat is None:
        import ollama

        chat = ollama.Client(host=host or os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")).chat

    def judge(question, answer, chunks):
        verdicts = {}
        for criterion in CRITERIA:
            response = chat(
                model=model,
                messages=[{"role": "user", "content": build_prompt(criterion, question, answer, chunks)}],
                format=RESPONSE_SCHEMA,
                options={"temperature": JUDGE_TEMPERATURE, "seed": JUDGE_SEED},
            )
            verdicts[criterion] = parse_verdict(response.message.content)
        return verdicts

    return judge
