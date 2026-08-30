# HoloMat

Interfaz holográfica controlada con el dedo índice. Inspirado en el proyecto [HoloMat de Concept Bytes](https://github.com/Concept-Bytes/Holomat).

Usa la cámara web para detectar la mano mediante MediaPipe y renderiza una interfaz estilo HUD sobre fondo negro con Pygame. La interacción es únicamente con el dedo índice: apuntar y mantener sobre un elemento para activarlo.

## Demo

- Menú radial con círculo Home central y apps alrededor
- Apps a pantalla completa con botones circulares
- Cursor visual: círculo azul claro en la punta del índice
- Hover para interactuar (sin gestos complejos)

## Interacción

| Acción | Cómo | Tiempo |
|--------|------|--------|
| **Abrir menú de apps** | Mantener índice sobre HOME | ~1s |
| **Seleccionar app** | Mantener índice sobre el círculo de la app | ~0.8s |
| **Controlar Spotify** | Mantener índice sobre botón (<<, ▶/❚❚, >>) | ~0.8s |
| **Regresar al Home** | Mantener índice sobre botón Home (esquina inferior izq.) | ~0.8s |

Todos los elementos interactivos muestran un arco de progreso visual mientras se mantiene el dedo sobre ellos.

## Arquitectura

```
src/
├── main.py                          # Loop principal (2 estados: HOME / APP)
└── core/
    ├── hand_tracker.py              # Detección de mano (MediaPipe + CLAHE + One Euro Filter)
    ├── home_menu.py                 # Menú radial con hover-to-select
    ├── renderer.py                  # Renderizado con Pygame
    └── widgets/
        ├── weather_widget.py        # Widget de hora/fecha (pantalla completa)
        ├── spotify_widget.py        # Widget de Spotify con botones hover
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
- Mantén el dedo índice sobre **HOME** para desplegar las apps
- Mantén el dedo sobre una app para abrirla
- Dentro de una app, mantén el dedo sobre los botones para interactuar
- Mantén el dedo sobre el botón **Home** (esquina inferior izquierda) para regresar

## Características técnicas

### Detección de mano
- MediaPipe Hands con confianza de detección 0.75 y tracking 0.6
- Preprocesamiento CLAHE para normalizar iluminación variable
- One Euro Filter para suavizado adaptativo del cursor (suave cuando quieto, rápido al moverse)

### Renderizado
- Pygame con ventana sin bordes (NOFRAME)
- Fondo negro (la cámara solo se usa para detección, no se muestra)
- UI estilo HUD: colores azul claro sobre negro
- Arcos de progreso visual en los elementos al hacer hover

### Menú Home
- Círculo central HOME con apps distribuidas alrededor
- Animación ease-out cubic al desplegar/ocultar apps
- Líneas de conexión del centro a cada app
- Soporte para imágenes en los círculos de apps

## Widgets

### WEATHER
- Muestra hora y fecha en tiempo real (pantalla completa, fuentes grandes)
- Estructura preparada para conectar OpenWeatherMap API

### SPOTIFY
- Integración con Spotify Web API (OAuth2)
- Muestra canción actual, artista y barra de progreso
- Botones circulares con hover: previous, play/pause, next
- Cada botón tiene su propio arco de progreso
- Actualizaciones en hilo de background (no bloquea el render)

### JARVIS
- Placeholder (sin funcionalidad asignada)

## Dependencias principales

- `opencv-contrib-python` — Captura de cámara y preprocesamiento
- `mediapipe` — Detección de mano y landmarks
- `pygame` — Renderizado de la interfaz
- `requests` — Comunicación con Spotify API
- `python-dotenv` — Variables de entorno

## Licencia

Proyecto personal / educativo.
