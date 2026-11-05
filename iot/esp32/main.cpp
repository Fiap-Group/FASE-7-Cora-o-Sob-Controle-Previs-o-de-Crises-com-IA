// Adaptado do projeto "TEMPLATE-TIAO-2026" (Global Solution, 2 ANO) — trocado
// o sensor DHT22 (clima) por 3 potenciômetros simulando leituras vitais
// (Wokwi não tem um sensor de FC/SPO2/PA simulável; o potenciômetro é o jeito
// padrão de simular qualquer leitura analógica ajustável à mão no simulador).
//
// Credenciais do MQTT NÃO ficam mais hardcoded aqui: vêm de build_flags do
// platformio.ini, que lê ${sysenv.*} do ambiente (ver .env/.env.example
// nesta pasta e o comentário no topo do platformio.ini).
#ifndef MQTT_SERVER
#error "Defina MQTT_SERVER/MQTT_PORT/MQTT_USER/MQTT_PASSWORD via .env + platformio.ini (ver .env.example)"
#endif

#include <PubSubClient.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>

const char *ssid = "Wokwi-GUEST";
const char *password = "";
const char *mqtt_server = MQTT_SERVER;
const int mqtt_port = MQTT_PORT;
const char *mqtt_user = MQTT_USER;
const char *mqtt_password = MQTT_PASSWORD;
const char *TOPIC_DATA = "esp32/cardio/data";

// Pinos ADC1 do ESP32 (seguros de usar com WiFi ligado; ADC2 conflita com o rádio).
const int PIN_FC = 34;    // potenciômetro -> frequência cardíaca
const int PIN_PA = 35;    // potenciômetro -> pressão arterial sistólica
const int PIN_SPO2 = 32;  // potenciômetro -> saturação de oxigênio (SPO2)
const int WIFI_LED = 2;

WiFiClientSecure espClient;
PubSubClient client(espClient);

unsigned long lastPublishTime = 0;
const int publishInterval = 2000; // publica a cada 2 segundos

// Limiares de alerta — mesmas condições reais usadas em
// app/backend/shared/preditivo/protocolos.py, não valores inventados aqui.
const float FC_ALERT_THRESHOLD = 120.0;   // FC > 120
const float PA_ALERT_THRESHOLD = 90.0;    // PA sistólica < 90
const float SPO2_ALERT_THRESHOLD = 88.0;  // SPO2 < 88%

// ---------------------------------------------------------------------------
// WiFi
// ---------------------------------------------------------------------------
void setup_wifi() {
  delay(10);
  Serial.println("\nConectando WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    digitalWrite(WIFI_LED, !digitalRead(WIFI_LED));
    delay(500);
    Serial.print(".");
  }

  digitalWrite(WIFI_LED, HIGH);
  Serial.println("\nWiFi conectado: " + WiFi.localIP().toString());
  espClient.setInsecure(); // mantido conforme original (sem certificado)
}

// ---------------------------------------------------------------------------
// Reconexão MQTT
// ---------------------------------------------------------------------------
void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando ao broker MQTT...");
    String clientId = "ESP32-CardioMonitor-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str(), mqtt_user, mqtt_password)) {
      Serial.println("Conectado!");
    } else {
      Serial.print("Falhou (rc=");
      Serial.print(client.state());
      Serial.println("). Tentando novamente em 5s...");
      delay(5000);
    }
  }
}

// ---------------------------------------------------------------------------
// Leitura dos potenciômetros, mapeada para faixas clinicamente plausíveis
// (mesmas faixas usadas em app/backend/shared/preditivo/dataset.py).
// ---------------------------------------------------------------------------
float ler_fc_media() {
  int leitura = analogRead(PIN_FC); // 0-4095 (ADC de 12 bits)
  return map(leitura, 0, 4095, 40, 180) * 1.0;
}

float ler_pa_sistolica() {
  int leitura = analogRead(PIN_PA);
  return map(leitura, 0, 4095, 70, 220) * 1.0;
}

float ler_spo2_media() {
  int leitura = analogRead(PIN_SPO2);
  return map(leitura, 0, 4095, 70, 100) * 1.0;
}

// ---------------------------------------------------------------------------
// Setup
// ---------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(WIFI_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);

  Serial.println("Sistema de monitoramento cardiaco iniciado.");
  Serial.print("Publicando em: ");
  Serial.println(TOPIC_DATA);
}

// ---------------------------------------------------------------------------
// Loop principal
// ---------------------------------------------------------------------------
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();

  if (now - lastPublishTime > publishInterval) {
    lastPublishTime = now;

    float fc_media = ler_fc_media();
    float pa_sistolica = ler_pa_sistolica();
    float spo2_media = ler_spo2_media();

    bool alert = fc_media > FC_ALERT_THRESHOLD || pa_sistolica < PA_ALERT_THRESHOLD ||
                 spo2_media < SPO2_ALERT_THRESHOLD;

    // Monta JSON com os mesmos nomes de campo do backend
    // (app/backend/shared/preditivo/dataset.py:COLUNAS_FEATURES), pra poder
    // alimentar o modelo preditivo sem renomear nada depois.
    char payload[160];
    snprintf(payload, sizeof(payload),
             "{\"fc_media\": %.1f, \"pa_sistolica\": %.1f, \"spo2_media\": %.1f, \"alert\": %s}",
             fc_media, pa_sistolica, spo2_media, alert ? "true" : "false");

    client.publish(TOPIC_DATA, payload);

    Serial.print("[MQTT] Publicado em ");
    Serial.print(TOPIC_DATA);
    Serial.print(" -> ");
    Serial.println(payload);

    if (alert) {
      Serial.println("[ALERTA] Métrica vital fora da faixa segura!");
    }
  }
}
