"""Conversa com o Guardião por texto, para testar o grafo sem a Alexa.

    python -m backend.cli
"""

import uuid

from backend import observabilidade
from backend.graph import Guardiao


def main() -> None:
    guardiao = Guardiao()
    sessao_id = f"cli-{uuid.uuid4()}"

    turno = guardiao.iniciar(sessao_id)
    try:
        while True:
            print(f"Guardião: {turno.fala}")
            if turno.encerrou:
                break
            turno = guardiao.responder(sessao_id, input("Você: "))
    except (EOFError, KeyboardInterrupt):
        print()
        return
    finally:
        observabilidade.enviar_pendentes()

    alerta = "não"
    if turno.alertar:
        alerta = "enviado no Telegram" if turno.alerta_enviado else "sim (Telegram não configurado)"
    print(f"\n[risco {turno.risco}/100 · alerta à família: {alerta}]")
    if turno.motivos:
        print(f"[motivos: {', '.join(turno.motivos)}]")
    if turno.golpe:
        print(f"[golpe parecido: {turno.golpe['nome']} (distância {turno.golpe['distancia']})]")
        print(f"[fonte: {turno.golpe['fonte']} - {turno.golpe['url']}]")


if __name__ == "__main__":
    main()
