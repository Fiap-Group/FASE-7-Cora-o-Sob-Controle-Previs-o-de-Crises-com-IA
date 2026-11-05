import json
import time

import network  # pyright: ignore[reportMissingImports]
from machine import ADC, Pin  # pyright: ignore[reportMissingImports]
from umqtt.simple import MQTTClient  # pyright: ignore[reportMissingImports]

from secrets import MQTT_PASSWORD, MQTT_PORT, MQTT_SERVER, MQTT_USER  # pyright: ignore[reportAttributeAccessIssue]

WIFI_SSID = "Wokwi-GUEST"
WIFI_PASSWORD = ""
TOPIC_DATA = "esp32/cardio/data"

PIN_FC = 34
PIN_PA = 35
PIN_SPO2 = 32
PIN_LED = 2

FC_ALERT_THRESHOLD = 120.0
PA_ALERT_THRESHOLD = 90.0
SPO2_ALERT_THRESHOLD = 88.0

led = Pin(PIN_LED, Pin.OUT)
adc_fc = ADC(Pin(PIN_FC))
adc_pa = ADC(Pin(PIN_PA))
adc_spo2 = ADC(Pin(PIN_SPO2))


def conectar_wifi():
    """Conecta o ESP32 à rede WiFi, piscando o LED até a conexão ser estabelecida."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            led.value(not led.value())
            time.sleep(0.5)
    led.value(1)
    print("WiFi conectado:", wlan.ifconfig()[0])


def mapear(valor, min_in, max_in, min_out, max_out):
    """Converte um valor de uma faixa de entrada para a faixa de saída correspondente."""
    return min_out + (valor - min_in) * (max_out - min_out) / (max_in - min_in)


def ler_fc_media():
    """Lê o potenciômetro de frequência cardíaca e converte para batimentos por minuto."""
    return round(mapear(adc_fc.read_u16(), 0, 65535, 40, 180), 1)


def ler_pa_sistolica():
    """Lê o potenciômetro de pressão arterial e converte para a pressão sistólica em mmHg."""
    return round(mapear(adc_pa.read_u16(), 0, 65535, 70, 220), 1)


def ler_spo2_media():
    """Lê o potenciômetro de saturação de oxigênio e converte para a porcentagem de SpO2."""
    return round(mapear(adc_spo2.read_u16(), 0, 65535, 70, 100), 1)


def conectar_mqtt():
    """Cria o cliente MQTT, conecta ao broker HiveMQ Cloud via TLS e o retorna."""
    client = MQTTClient(
        "esp32-cardio-monitor",
        MQTT_SERVER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        ssl=True,
        ssl_params={"server_hostname": MQTT_SERVER},
    )
    client.connect()
    print("Conectado ao broker MQTT em", MQTT_SERVER)
    return client


def main():
    """Conecta o ESP32 ao WiFi e ao broker MQTT e publica as leituras vitais em loop."""
    conectar_wifi()
    client = conectar_mqtt()
    print("Monitor cardíaco iniciado — publicando em", TOPIC_DATA)

    while True:
        fc_media = ler_fc_media()
        pa_sistolica = ler_pa_sistolica()
        spo2_media = ler_spo2_media()

        alerta = fc_media > FC_ALERT_THRESHOLD or pa_sistolica < PA_ALERT_THRESHOLD or spo2_media < SPO2_ALERT_THRESHOLD

        payload = json.dumps(
            {
                "fc_media": fc_media,
                "pa_sistolica": pa_sistolica,
                "spo2_media": spo2_media,
                "alert": alerta,
            }
        )

        try:
            client.publish(TOPIC_DATA, payload)
            print("[MQTT]", payload)
        except OSError as erro:
            print("[ERRO] Falha ao publicar, reconectando:", erro)
            client = conectar_mqtt()

        led.value(0 if alerta else 1)
        if alerta:
            print("[ALERTA] Métrica vital fora da faixa segura!")

        time.sleep(2)


main()
