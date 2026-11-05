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
    """Última leitura de sinais vitais recebida do ESP32 via MQTT."""

    conectado: bool = False
    fc_media: float | None = None
    pa_sistolica: float | None = None
    spo2_media: float | None = None
    recebido_em: datetime | None = None


_leitura = LeituraIot()


def get_leitura_iot() -> LeituraIot:
    """Devolve a instância compartilhada com a última leitura do ESP32."""
    return _leitura


def _ao_conectar(
    client: mqtt.Client, _userdata: object, _connect_flags: object, codigo_motivo: object, _properties: object
) -> None:
    """Assina o tópico MQTT do ESP32 ao conectar com sucesso no broker."""
    topico = os.getenv("MQTT_TOPIC", "esp32/cardio/data")
    if codigo_motivo == 0:
        _leitura.conectado = True
        client.subscribe(topico)
        logger.info("Conectado ao broker MQTT, assinando %s", topico, extra={"evento": "mqtt_conectado"})
    else:
        logger.warning("Falha ao conectar no broker MQTT: %s", codigo_motivo, extra={"evento": "mqtt_erro"})


def _ao_desconectar(_client: mqtt.Client, _userdata: object, *_args: object) -> None:
    """Marca a leitura como desconectada do broker MQTT."""
    _leitura.conectado = False


def _ao_receber_mensagem(_client: mqtt.Client, _userdata: object, msg: mqtt.MQTTMessage) -> None:
    """Atualiza a última leitura de sinais vitais a partir da mensagem MQTT recebida."""
    try:
        dados = json.loads(msg.payload)
        _leitura.fc_media = float(dados["fc_media"])
        _leitura.pa_sistolica = float(dados["pa_sistolica"])
        _leitura.spo2_media = float(dados["spo2_media"])
        _leitura.recebido_em = datetime.now()
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        logger.warning("Mensagem MQTT em formato inesperado: %s", e, extra={"evento": "mqtt_payload_invalido"})


def iniciar_mqtt_listener() -> None:
    """Conecta ao broker MQTT em segundo plano, sem derrubar o backend se a conexão falhar."""
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
