import os
import time
import json
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, urlencode
import requests
from dotenv import load_dotenv

load_dotenv()


class SpotifyAuth:
    """Maneja la autenticación OAuth2 con Spotify."""

    TOKEN_FILE = ".spotify_token.json"
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    SCOPES = [
        "user-read-playback-state",
        "user-modify-playback-state",
        "user-read-currently-playing",
    ]

    def __init__(self):
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

        self.access_token = None
        self.refresh_token = None
        self.expires_at = 0

        self._load_token()

    def _load_token(self):
        """Carga token guardado si existe."""
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, "r") as f:
                data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.expires_at = data.get("expires_at", 0)

    def _save_token(self):
        """Guarda token en disco."""
        with open(self.TOKEN_FILE, "w") as f:
            json.dump({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expires_at": self.expires_at,
            }, f)

    def is_authenticated(self):
        return self.access_token is not None

    def get_token(self):
        """Retorna un token válido, refrescando si es necesario."""
        if time.time() >= self.expires_at - 60:
            if self.refresh_token:
                self._refresh()
            else:
                return None
        return self.access_token

    def authenticate(self):
        """Inicia el flujo OAuth2 abriendo el navegador."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
        }

        auth_url = f"{self.AUTH_URL}?{urlencode(params)}"
        print(f"Abriendo navegador para autenticación...")
        webbrowser.open(auth_url)

        # Servidor temporal para capturar el callback
        code = self._wait_for_callback()

        if code:
            self._exchange_code(code)
            print("Autenticación exitosa.")
        else:
            print("Error en la autenticación.")

    def _wait_for_callback(self):
        """Levanta un servidor HTTP temporal para capturar el code."""
        code_holder = {"code": None}

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                query = parse_qs(urlparse(self.path).query)
                code_holder["code"] = query.get("code", [None])[0]

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Autenticacion exitosa. Puedes cerrar esta ventana.</h2></body></html>"
                )

            def log_message(self, format, *args):
                pass

        server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
        server.timeout = 60
        server.handle_request()
        server.server_close()

        return code_holder["code"]

    def _exchange_code(self, code):
        """Intercambia el code por tokens."""
        response = requests.post(self.TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.expires_at = time.time() + data["expires_in"]
            self._save_token()

    def _refresh(self):
        """Refresca el access token."""
        response = requests.post(self.TOKEN_URL, data={
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.expires_at = time.time() + data["expires_in"]
            self._save_token()


class SpotifyController:
    """Controla la reproducción de Spotify (no bloquea el hilo principal)."""

    API_BASE = "https://api.spotify.com/v1/me/player"

    def __init__(self):
        self.auth = SpotifyAuth()

        # Estado actual (leído desde el hilo de background)
        self.is_playing = False
        self.track_name = ""
        self.artist_name = ""
        self.progress_ms = 0
        self.duration_ms = 0

        self.update_interval = 2.0
        self._lock = threading.Lock()
        self._running = True
        self._thread = None

    def ensure_authenticated(self):
        """Autentica si no hay token."""
        if not self.auth.is_authenticated():
            self.auth.authenticate()

    def start_background_updates(self):
        """Inicia un hilo que actualiza el estado periódicamente."""
        self._thread = threading.Thread(target=self._update_loop, daemon=True)
        self._thread.start()

    def _update_loop(self):
        """Loop de background que consulta Spotify cada N segundos."""
        while self._running:
            self._fetch_state()
            time.sleep(self.update_interval)

    def _headers(self):
        token = self.auth.get_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return None

    def _fetch_state(self):
        """Consulta el estado actual de Spotify (corre en background)."""
        headers = self._headers()
        if not headers:
            return

        try:
            response = requests.get(
                f"{self.API_BASE}/currently-playing",
                headers=headers,
                timeout=3
            )

            if response.status_code == 200:
                data = response.json()

                with self._lock:
                    self.is_playing = data.get("is_playing", False)

                    item = data.get("item")
                    if item:
                        self.track_name = item.get("name", "")
                        artists = item.get("artists", [])
                        self.artist_name = artists[0]["name"] if artists else ""
                        self.duration_ms = item.get("duration_ms", 0)

                    self.progress_ms = data.get("progress_ms", 0)

            elif response.status_code == 204:
                with self._lock:
                    self.is_playing = False
                    self.track_name = "Sin reproducción"
                    self.artist_name = ""

        except requests.RequestException:
            pass

    def update(self):
        """No-op: las actualizaciones corren en background."""
        pass

    def play_pause(self):
        """Alterna entre play y pause (en un hilo para no bloquear)."""
        threading.Thread(target=self._do_play_pause, daemon=True).start()

    def _do_play_pause(self):
        headers = self._headers()
        if not headers:
            return

        try:
            if self.is_playing:
                requests.put(f"{self.API_BASE}/pause", headers=headers, timeout=3)
                with self._lock:
                    self.is_playing = False
            else:
                requests.put(f"{self.API_BASE}/play", headers=headers, timeout=3)
                with self._lock:
                    self.is_playing = True
        except requests.RequestException:
            pass

    def next_track(self):
        """Salta a la siguiente canción."""
        threading.Thread(target=self._do_next, daemon=True).start()

    def _do_next(self):
        headers = self._headers()
        if not headers:
            return
        try:
            requests.post(f"{self.API_BASE}/next", headers=headers, timeout=3)
        except requests.RequestException:
            pass

    def previous_track(self):
        """Regresa a la canción anterior."""
        threading.Thread(target=self._do_previous, daemon=True).start()

    def _do_previous(self):
        headers = self._headers()
        if not headers:
            return
        try:
            requests.post(f"{self.API_BASE}/previous", headers=headers, timeout=3)
        except requests.RequestException:
            pass

    def stop(self):
        """Detiene el hilo de background."""
        self._running = False
