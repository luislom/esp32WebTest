# ESP32 Web LED Controller

Este proyecto permite controlar tres LEDs conectados a un ESP32 desde una interfaz web desarrollada en Python usando Reflex. El ESP32 debe estar conectado a la misma red WiFi que el dispositivo desde el que accedes a la web.

## Descripción

La aplicación web permite encender y apagar tres LEDs (amarillo, azul y verde) conectados al ESP32. La comunicación se realiza mediante peticiones HTTP a un servidor web simple que corre en el ESP32.

## Requisitos

- ESP32 Dev Board
- 3 LEDs y resistencias adecuadas
- Conexión WiFi
- Python 3.10+ y Reflex para la interfaz web

## Instalación y uso

### 1. Subir el siguiente código al ESP32

Copia y sube este código a tu ESP32 usando Arduino IDE o PlatformIO. Cambia el nombre y contraseña de la red WiFi según tu configuración.

```cpp
#include <WiFi.h>

// Cambia por tu red WiFi
const char* ssid = "iPhone de ASUS";
const char* password = "lozano1213";

// Pines para los 3 LEDs
const int led1 = 13;
const int led2 = 12;
const int led3 = 27;

WiFiServer server(80);

void setup() {
  Serial.begin(115200);

  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);

  digitalWrite(led1, LOW);
  digitalWrite(led2, LOW);
  digitalWrite(led3, LOW);

  // Conectar al WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando al WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConectado!");
  Serial.print("IP local: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Cliente conectado.");
    String request = client.readStringUntil('\r');
    Serial.println("Solicitud: " + request);
    client.flush();

    // Comandos LED 1
    if (request.indexOf("/led/yellow/on") != -1) {
      digitalWrite(led1, HIGH);
    } else if (request.indexOf("/led/yellow/off") != -1) {
      digitalWrite(led1, LOW);
    }

    // Comandos LED 2
    if (request.indexOf("/led/green/on") != -1) {
      digitalWrite(led2, HIGH);
    } else if (request.indexOf("/led/green/off") != -1) {
      digitalWrite(led2, LOW);
    }

    // Comandos LED 3
    if (request.indexOf("/led/blue/on") != -1) {
      digitalWrite(led3, HIGH);
    } else if (request.indexOf("/led/blue/off") != -1) {
      digitalWrite(led3, LOW);
    }

    // Respuesta básica
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/html");
    client.println();
    client.println("OK");
    client.stop();
    Serial.println("Cliente desconectado.");
  }
}
```

### 2. Conectar los LEDs

- LED amarillo: Pin GPIO 13
- LED verde: Pin GPIO 12
- LED azul: Pin GPIO 27

### 3. Ejecutar la aplicación web

1. Instala las dependencias de Python (incluyendo Reflex).
2. Ejecuta el servidor web con `reflex run` o el comando correspondiente.
3. Ingresa la IP local del ESP32 en la interfaz web.

## Endpoints HTTP

- `/led/yellow/on` y `/led/yellow/off`
- `/led/green/on` y `/led/green/off`
- `/led/blue/on` y `/led/blue/off`

## Créditos

Desarrollado por [Tu Nombre].

---