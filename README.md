# HoloMat

Interfaz holográfica controlada por gestos de la mano. Inspirado en el proyecto [HoloMat de Concept Bytes](https://github.com/Concept-Bytes/Holomat).

Usa la cámara web para detectar la mano mediante MediaPipe y renderiza una interfaz estilo HUD sobre fondo negro con Pygame, donde puedes interactuar con paneles flotantes usando gestos naturales.

## Demo

- Paneles flotantes con estilo HUD (esquinas bracket, fondo semi-transparente)
- Cursor visual: círculos en índice, pulgar y dedo medio
- Drag para mover ventanas, click para interactuar

## Gestos

| Gesto | Dedos | Acción |
|-------|-------|--------|
| **Click** | Pulgar + dedo medio | Ejecuta acción en la ventana apuntada |
| **Drag** | Pulgar + índice + mover | Arrastra la ventana |
| **Hold** | Pulgar + índice quieto (0.6s) | Mantener presionado |
| **Puño** | Todos los dedos cerrados | Detectado (sin acción asignada) |
| **Mano abierta** | Todos los dedos extendidos | Detectado (sin acción asignada) |

## Arquitectura

```
src/
├── main.py                          # Loop principal (orquestación)
├── resources/                       # Assets (logos, iconos)
│   └── spotify_logo.png
└── core/
    ├── hand_tracker.py              # Detección de mano (MediaPipe)
    ├── gesture_detector.py          # Máquina de estados de gestos
    ├── draggable_object.py          # Objeto arrastrable con smoothing
    ├── window_manager.py            # Gestión de ventanas y eventos
    ├── renderer.py                  # Renderizado con Pygame
    └── widgets/
        ├── weather_widget.py        # Widget de hora/fecha (listo para API de clima)
        ├── spotify_widget.py        # Widget de Spotify (reproductor)
        └── spotify_controller.py    # Auth OAuth2 + control de Spotify
```

## Requisitos

- Python 3.12+
- Cámara web
- Cuenta de Spotify (Premium para control de reproducción)

## Instalación

```bash
# Clonar el proyecto
git clone <repo_url>
cd holomat

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## Configuración

### Spotify (opcional)

1. Crea una app en [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Agrega `http://127.0.0.1:8888/callback` como Redirect URI
3. Crea un archivo `.env` en la raíz del proyecto:

```env
SPOTIFY_CLIENT_ID=tu_client_id
SPOTIFY_CLIENT_SECRET=tu_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## Uso

```bash
cd src
python main.py
```

- Presiona **ESC** para salir
- Pon la mano frente a la cámara
- Junta **pulgar + índice** sobre una ventana y mueve para arrastrar
- Junta **pulgar + dedo medio** para hacer click

## Características técnicas

### Detección de gestos
- Histéresis en el pinch (umbral diferente para activar vs soltar)
- Suavizado con mediana sobre N frames para reducir ruido
- Buffer de confirmación para evitar falsos positivos
- Protección extra contra soltar durante drag (umbral más generoso + buffer de release)
- Detección de dedos basada en distancias 3D al MCP (independiente de orientación)

### Renderizado
- Pygame con ventana sin bordes (NOFRAME)
- Fondo negro (la cámara solo se usa para detección, no se muestra)
- Transparencia real con SRCALPHA
- UI estilo HUD: esquinas bracket, colores azul claro sobre negro
- Sistema de widgets extensible

### Interacción
- Cursor suavizado para reducir jitter de MediaPipe
- Drag con interpolación suave (smoothing)
- Z-order dinámico (la ventana arrastrada se trae al frente)
- Sistema de click_actions por ventana

## Widgets

### WEATHER
- Muestra hora y fecha en tiempo real
- Estructura preparada para conectar OpenWeatherMap API

### SPOTIFY
- Integración con Spotify Web API (OAuth2)
- Muestra canción actual, artista y barra de progreso
- Control de reproducción: play/pause, next, previous
- Actualizaciones en hilo de background (no bloquea el render)

### JARVIS
- Placeholder (sin funcionalidad asignada)

## Dependencias principales

- `opencv-contrib-python` — Captura de cámara
- `mediapipe` — Detección de mano y landmarks
- `pygame` — Renderizado de la interfaz
- `requests` — Comunicación con Spotify API
- `python-dotenv` — Variables de entorno

## Licencia

Proyecto personal / educativo.
