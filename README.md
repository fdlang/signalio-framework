
# 🚀 Signalio

Framework modular de trading algorítmico desarrollado en Python, diseñado siguiendo principios SOLID y patrones de diseño como Factory, Observer y Dependency Injection.

Signalio Framework conecta al exchange Binance, procesa datos de mercado en tiempo real y genera señales automáticas enviadas a Telegram.
Su arquitectura escalable y desacoplada permite la fácil integración de nuevos exchanges, así como la futura ejecución automática de operaciones.

---

## 📚 Tabla de Contenidos

- [🚀 Signalio Framework](#-signalio-framework)
- [🏗 Tecnologías utilizadas](#-tecnologías-utilizadas)
- [🧠 Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [🎨 Patrones de Diseño Aplicados](#-patrones-de-diseño-aplicados)
  - [📡 Observer](#-observer-pattern)
  - [🛠️ Dependency Injection](#-dependency-injection)
  - [🔌 Adapter](#-adapter-pattern)
  - [🏭 Factory (En evolución)](#-factory-pattern-en-evolución)
- [🚀 Beneficios del Diseño](#-beneficios-del-diseño)
- [📦 Instalación y ejecución](#-instalación-y-ejecución)
- [⚙️ Configuración](#-configuración)
- [🛠️ Futuras mejoras](#-futuras-mejoras)
- [📄 Licencia](#-licencia)

---

## 🏗 Tecnologías utilizadas

- Python 
- Docker
- Anaconda
- Binance API
- Telegram Bot API
- Arquitectura Modular basada en principios SOLID

---

## 🧠 Arquitectura del Proyecto

Signalio Framework se estructura en módulos independientes que interactúan entre sí:

- `platform_connector`: gestión de conexión a exchanges como Binance.
- `data_provider`: gestion y tratamiento de datos en tiempo real.
- `signal_generator`: generación de señales de trading.
- `notifications`: envío de datos via mensajes a Telegram.
- `trading_director`: maneja la logica principal del proyecto.

Cada componente es desacoplado, permitiendo fácil extensión y mantenimiento.

---

## 🎨 Patrones de Diseño Aplicados

Signalio Framework ha sido construido aplicando principios de ingeniería de software sólidos y utilizando varios patrones de diseño clásicos para garantizar escalabilidad, modularidad y mantenibilidad:

---

### 📡 Observer
El módulo `notifications` implementa el patrón Observer para reaccionar a las señales generadas.  
Cuando el `SignalGenerator` detecta una oportunidad de mercado, notifica automáticamente a los observadores (como el bot de Telegram), que se encargan de enviar el mensaje al usuario.

> **Ventaja:** Permite añadir múltiples sistemas de notificación (Telegram, correo electrónico, dashboards) sin modificar la lógica de generación de señales.

---

### 🛠️ Dependency Injection
Los componentes principales (`PlatformConnector`, `SignalGenerator`, `notifications`) reciben sus dependencias externamente en lugar de crearlas internamente, fomentando un bajo acoplamiento y facilitando el testing.

> **Ventaja:** Mejora la testabilidad y permite sustituir o ampliar componentes de forma sencilla.

---

### 🔌 Adapter 
El `PlatformConnector` actúa como adaptador entre la API externa de Binance y la lógica interna del framework, transformando los datos recibidos a un formato estandarizado.

> **Ventaja:** Facilita la integración de nuevos exchanges o fuentes de datos sin modificar la lógica de negocio.

---

### 🏭 Factory (En evolución)
La estructura actual de `PlatformConnector` está diseñada para evolucionar hacia un patrón Factory completo, donde se podrá seleccionar dinámicamente la plataforma a conectar (Binance, Coinbase, KuCoin, etc.).

> **Ventaja:** Permite escalar fácilmente a múltiples plataformas mediante un único punto de creación controlado.

---

## 🚀 Beneficios del Diseño

Gracias a esta arquitectura basada en patrones:
- Signalio es **extensible** y preparado para múltiples exchanges.
- Es **mantenible** con bajo acoplamiento entre componentes.
- Está **optimizado para testeo** y futuras mejoras como la ejecución automática de operaciones.

---

## 📦 Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/fdlang/Signalio-framework.git
   ```
2. Crea un entorno virtual e instala dependencias:
   ```bash
   python -m venv env
   source env/bin/activate
   pip install -r requirements.txt
   ```
3. Configura tus claves API en el archivo `.env`.
4. Ejecuta el programa:
   ```bash
   python trading_app.py
   ```

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# BINANCE
api_key=your_binance_api_key
secret_key=your_binance_api_secret

# BINANCE TESNET
testnet_api_key=your_binance_testnet_api_key
testnet_secret_key=your_binance_tesnet_api_secret

# TELEGRAM
token=your_telegram_bot_token
chat_id=your_telegram_chat_id
```

---

## 🛠️ Futuras mejoras

- Ejecución automática de órdenes de compra/venta en Binance.
- Soporte multi-exchange (Coinbase, KuCoin, etc.).
- Sistema de backtesting de estrategias.
- Dashboard Web para visualización en tiempo real.
- Optimización de la gestión de eventos y señales.

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

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT 
Copyright (c) 2024 Angel Arcos

---
