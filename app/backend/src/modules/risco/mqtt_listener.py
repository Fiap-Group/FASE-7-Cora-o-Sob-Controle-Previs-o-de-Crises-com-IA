"""
=============================================================================
Listener MQTT do módulo de risco cardíaco
=============================================================================
Assina o tópico publicado pelo ESP32 (iot/esp32/main.py, MicroPython) e guarda só a
leitura mais recente em memória — não dispara a avaliação de risco (que
chama o Gemini várias vezes via shared/agentes/) a cada mensagem. O ESP32
publica a cada 2s; se cada mensagem disparasse a cadeia de agentes, a cota
diária gratuita do Gemini (ver docs/ARQUITETURA_IA.md) estouraria em menos
de um minuto. A avaliação continua manual, disparada pelo usuário no front
com os valores desta leitura como ponto de partida.

`get_leitura_iot` é a dependency (igual a `get_estado` do módulo RAG) —
testes substituem por uma `LeituraIot` fake via `app.dependency_overrides`,
sem conectar no broker de verdade.
=============================================================================
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

logger = logging.getLogger("genera_api")


@dataclass
class LeituraIot:
    conectado: bool = False
    fc_media: float | None = None
    pa_sistolica: float | None = None
    spo2_media: float | None = None
    recebido_em: datetime | None = None


_leitura = LeituraIot()


def get_leitura_iot() -> LeituraIot:
    return _leitura


def _ao_conectar(
    client: mqtt.Client, _userdata: object, _connect_flags: object, codigo_motivo: object, _properties: object
) -> None:
    topico = os.getenv("MQTT_TOPIC", "esp32/cardio/data")
    if codigo_motivo == 0:
        _leitura.conectado = True
        client.subscribe(topico)
        logger.info("Conectado ao broker MQTT, assinando %s", topico, extra={"evento": "mqtt_conectado"})
    else:
        logger.warning("Falha ao conectar no broker MQTT: %s", codigo_motivo, extra={"evento": "mqtt_erro"})


def _ao_desconectar(_client: mqtt.Client, _userdata: object, *_args: object) -> None:
    _leitura.conectado = False


def _ao_receber_mensagem(_client: mqtt.Client, _userdata: object, msg: mqtt.MQTTMessage) -> None:
    try:
        dados = json.loads(msg.payload)
        _leitura.fc_media = float(dados["fc_media"])
        _leitura.pa_sistolica = float(dados["pa_sistolica"])
        _leitura.spo2_media = float(dados["spo2_media"])
        _leitura.recebido_em = datetime.now()
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.warning("Mensagem MQTT em formato inesperado: %s", e, extra={"evento": "mqtt_payload_invalido"})


def iniciar_mqtt_listener() -> None:
    """Conecta em segundo plano (client.loop_start(), thread própria do
    paho-mqtt). Erro de conexão não derruba o backend: fica `conectado=False`
    até o broker/ESP32 ficarem disponíveis — mesmo espírito de /api/chat sem
    GEMINI_API_KEY configurada."""
    servidor = os.getenv("MQTT_SERVER")
    if not servidor:
        logger.info("MQTT_SERVER não configurado — listener de IoT desligado.", extra={"evento": "mqtt_desligado"})
        return

    porta = int(os.getenv("MQTT_PORT", "8883"))
    usuario = os.getenv("MQTT_USER")
    senha = os.getenv("MQTT_PASSWORD")

    client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
    client.username_pw_set(usuario, senha)
    client.tls_set()
    client.on_connect = _ao_conectar
    client.on_disconnect = _ao_desconectar
    client.on_message = _ao_receber_mensagem

    try:
        client.connect(servidor, porta, keepalive=60)
        client.loop_start()
    except Exception as e:
        logger.warning("Não foi possível conectar ao broker MQTT agora: %s", e, extra={"evento": "mqtt_erro"})
