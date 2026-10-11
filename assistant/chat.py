import sys

from assistant.index import IndexUnavailable, require_index
from assistant.pipeline import RagConfig, stream_answer
from assistant.settings import SettingsError, get_strategy


def to_ask():
    try:
        config = RagConfig()
        require_index(get_strategy(config.strategy))
    except SettingsError as error:
        print(f"Configuração inválida: {len(error.problems)} problema(s)")
        for problem in error.problems:
            print(f"  - {problem}")
        return 2
    except IndexUnavailable as error:
        print(f"Não foi possível iniciar: {error}")
        return 1

    while True:
        ask = input("Digite sua pergunta: ")

        if ask.lower() in ["sair", "exit", "quit"]:
            print("Encerrando o assistente. Até mais!")
            break

        if not ask.strip():
            continue

        print("\nresponse: ", end="", flush=True)
        for piece in stream_answer(ask, config):
            print(piece, end="", flush=True)
        print("\n")
    return 0


if __name__ == "__main__":
    sys.exit(to_ask())
