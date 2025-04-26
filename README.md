# Signalio Framework

> **Framework modular de trading algorítmico para el procesamiento y distribución de señales en tiempo real.**

Signalio Framework es un sistema extensible diseñado para conectar con exchanges de criptomonedas (actualmente Binance), procesar datos de mercado, generar señales de trading y enviarlas automáticamente mediante un bot de Telegram.

---

## Tabla de contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Roadmap](#roadmap)
- [Contribuciones](#contribuciones)
- [Licencia](#licencia)

---

## Características

- 🔌 **Conexión a Binance** vía API pública/privada.
- 🧠 **Procesamiento modular** de datos de mercado.
- 🏗️ **Platform Connector**: capa de abstracción para facilitar soporte multi-exchange.
- 📈 **Generador de señales** configurable.
- 📲 **Integración con Telegram** para notificación de señales.
- 🚀 **Contenerización** lista mediante Docker.

---

## Arquitectura

```mermaid
flowchart TD
    A[PlatformConnector] --> B[DataProvider]
    B --> C[SignalGenerator]
    C --> D[Notifier]
    C --> E[Usuario de Telegram]
    D --> F[(próximamente)<br/>Ejecución de órdenes en Exchange]
```

### Componentes principales

| Componente          | Descripción |
|----------------------|-------------|
| **Platform Connector** | Capa de conexión estandarizada para comunicación con exchanges como Binance. |
| **Data Provider**    | Obtiene datos de mercado (precio, volumen, indicadores). |
| **Signal Generator** | Procesa los datos y genera señales basadas en estrategias. |
| **Notifier**         | Envía las señales generadas a un canal de Telegram. |

---

## Instalación

### Requisitos

- Python 3.7+
- Cuenta Binance con API habilitada
- Bot de Telegram activo

### Clonar el proyecto

```bash
git clone https://github.com/fdlang/signalio-framework.git
cd signalio-framework
```

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## Configuración

SignalIO utiliza variables de entorno para las credenciales y configuraciones básicas:

| Variable               | Descripción                         |
|-------------------------|-------------------------------------|
| `BINANCE_API_KEY`        | Clave pública de Binance           |
| `BINANCE_API_SECRET`     | Clave secreta de Binance           |
| `TELEGRAM_BOT_TOKEN`     | Token de tu bot en Telegram        |
| `TELEGRAM_CHAT_ID`       | ID del chat o grupo objetivo       |

**Ejemplo**:

```bash
export BINANCE_API_KEY='your_api_key'
export BINANCE_API_SECRET='your_api_secret'
export TELEGRAM_BOT_TOKEN='your_bot_token'
export TELEGRAM_CHAT_ID='your_chat_id'
```

O puedes crear un archivo `.env`:

```bash
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

---

## Uso

### Ejecución local

```bash
python trading_app.py
```

Esto lanzará:
- Conexión a Binance
- Generación de señales
- Envío de señales a Telegram

### Uso con Docker

```bash
docker build -t signalio-framework .
docker run --env-file .env signalio-framework
```

---

## Roadmap

- [x] Conexión a Binance
- [x] Envío de señales a Telegram
- [x] Creación de Platform Connector para facilitar nuevos exchanges
- [ ] Ejecución automática de órdenes de compra/venta
- [ ] Soporte para múltiples exchanges (Coinbase, KuCoin, etc.)
- [ ] Dashboard Web para visualización de señales en tiempo real
- [ ] Soporte a diferentes estrategias de trading dinámicas

---

## Contribuciones

Las contribuciones son bienvenidas 🚀:

1. Haz un fork del repositorio.
2. Crea una nueva rama:  
   `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios.
4. Envía un Pull Request.

Por favor asegúrate de mantener el estilo de codificación existente y agregar pruebas donde sea aplicable.

---
