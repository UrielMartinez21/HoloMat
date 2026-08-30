import math
import time
import random

import pygame

from core.widgets.base_widget import BaseWidget
from core.widgets.hover_button import HoverButton


class JarvisWidget(BaseWidget):
    """Widget JARVIS — interfaz holográfica con animaciones.

    Estado visual animado con botón hover para controlar
    listening/idle. El LLM se conectará después.
    """

    # Estados
    STATE_IDLE = "IDLE"
    STATE_LISTENING = "LISTENING"
    STATE_THINKING = "THINKING"

    def __init__(self):
        self.font_status = pygame.font.SysFont("Consolas", 28, bold=True)
        self.font_label = pygame.font.SysFont("Consolas", 16)
        self.font_hint = pygame.font.SysFont("Consolas", 14)

        self.state = self.STATE_IDLE
        self.start_time = time.time()
        self._thinking_start = 0

        # Colores
        self.color_primary = (173, 216, 230)
        self.color_listening = (100, 255, 180)
        self.color_thinking = (255, 200, 100)
        self.color_dim = (60, 60, 80)

        # Partículas orbitales
        self._particles = []
        for _ in range(12):
            self._particles.append({
                "angle": random.uniform(0, 2 * math.pi),
                "speed": random.uniform(0.3, 0.8),
                "radius_offset": random.uniform(-15, 15),
                "size": random.randint(2, 4),
            })

        # Botón de acción (posición se calcula en draw)
        self.btn_action = HoverButton(
            0, 0, 50, "MIC",
            on_trigger=self._toggle_state,
        )

        # Texto de respuesta (placeholder para cuando se conecte LLM)
        self.response_text = None

    def update(self):
        pass

    def update_hover(self, finger_x, finger_y):
        """Actualiza hover sobre el botón."""
        self.btn_action.update(finger_x, finger_y)

    def clear_hover(self):
        self.btn_action.clear()

    def _toggle_state(self):
        """Cambia entre IDLE y LISTENING."""
        if self.state == self.STATE_IDLE:
            self.state = self.STATE_LISTENING
            self.response_text = None
        elif self.state == self.STATE_LISTENING:
            self.state = self.STATE_THINKING
            self._thinking_start = time.time()
        elif self.state == self.STATE_THINKING:
            self.state = self.STATE_IDLE

    def _get_state_color(self):
        """Color según el estado actual."""
        if self.state == self.STATE_LISTENING:
            return self.color_listening
        elif self.state == self.STATE_THINKING:
            return self.color_thinking
        return self.color_primary

    def draw(self, screen, width, height, color):
        """Dibuja la interfaz JARVIS."""
        cx = width // 2
        cy = height // 2 - 30
        t = time.time() - self.start_time

        state_color = self._get_state_color()

        # Auto-return from THINKING after 2 seconds
        if self.state == self.STATE_THINKING:
            if time.time() - self._thinking_start > 2.0:
                self.state = self.STATE_IDLE
                self.response_text = "LLM not connected yet."

        # --- Core circle (pulsing) ---
        pulse = 1.0 + 0.06 * math.sin(t * 2.5)
        core_radius = int(60 * pulse)

        # Glow
        glow_surface = pygame.Surface(
            (core_radius * 4, core_radius * 4), pygame.SRCALPHA
        )
        for i in range(3):
            r = core_radius + i * 12
            alpha = max(30 - i * 10, 5)
            glow_color = (*state_color[:3], alpha)
            pygame.draw.circle(
                glow_surface, glow_color,
                (core_radius * 2, core_radius * 2), r, 2
            )
        screen.blit(
            glow_surface,
            (cx - core_radius * 2, cy - core_radius * 2),
        )

        # Core ring
        pygame.draw.circle(screen, state_color, (cx, cy), core_radius, 3)

        # Inner ring (counter-rotating)
        inner_radius = int(40 * pulse)
        self._draw_dashed_ring(screen, cx, cy, inner_radius, t * -1.5, state_color, 8)

        # --- Orbiting particles ---
        orbit_radius = int(90 * pulse)
        for p in self._particles:
            angle = p["angle"] + t * p["speed"]

            # In LISTENING state, particles orbit faster
            if self.state == self.STATE_LISTENING:
                angle = p["angle"] + t * p["speed"] * 2.5

            px = cx + int((orbit_radius + p["radius_offset"]) * math.cos(angle))
            py = cy + int((orbit_radius + p["radius_offset"]) * math.sin(angle))

            alpha = int(150 + 80 * math.sin(t * 2 + p["angle"]))
            alpha = max(50, min(255, alpha))

            particle_surface = pygame.Surface(
                (p["size"] * 2, p["size"] * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                particle_surface,
                (*state_color[:3], alpha),
                (p["size"], p["size"]),
                p["size"],
            )
            screen.blit(particle_surface, (px - p["size"], py - p["size"]))

        # --- Outer scanning ring ---
        outer_radius = int(110 * pulse)
        scan_angle = t * 1.2
        arc_length = math.pi * 0.6
        arc_rect = pygame.Rect(
            cx - outer_radius, cy - outer_radius,
            outer_radius * 2, outer_radius * 2,
        )
        pygame.draw.arc(
            screen, (*state_color[:3],),
            arc_rect, scan_angle, scan_angle + arc_length, 2
        )
        pygame.draw.arc(
            screen, (*state_color[:3],),
            arc_rect,
            scan_angle + math.pi,
            scan_angle + math.pi + arc_length,
            2,
        )

        # --- Status text ---
        status_labels = {
            self.STATE_IDLE: "STANDBY",
            self.STATE_LISTENING: "LISTENING...",
            self.STATE_THINKING: "PROCESSING...",
        }
        status = status_labels.get(self.state, "")

        surface = self.font_status.render(status, True, state_color)
        rect = surface.get_rect(centerx=cx, centery=cy + outer_radius + 40)
        screen.blit(surface, rect)

        # --- "J.A.R.V.I.S." label inside core ---
        label = self.font_label.render("J.A.R.V.I.S.", True, state_color)
        label_rect = label.get_rect(centerx=cx, centery=cy)
        screen.blit(label, label_rect)

        # --- Response text (when available) ---
        if self.response_text:
            resp = self.font_hint.render(self.response_text, True, self.color_dim)
            resp_rect = resp.get_rect(centerx=cx, centery=cy + outer_radius + 70)
            screen.blit(resp, resp_rect)

        # --- Action button ---
        btn_y = cy + outer_radius + 120
        self.btn_action.set_position(cx, btn_y)

        # Update label based on state
        if self.state == self.STATE_IDLE:
            self.btn_action.label = "MIC"
        elif self.state == self.STATE_LISTENING:
            self.btn_action.label = "STOP"
        else:
            self.btn_action.label = "..."

        self.btn_action.draw(screen)

    def _draw_dashed_ring(self, screen, cx, cy, radius, rotation, color, segments):
        """Dibuja un anillo segmentado que rota."""
        gap = math.pi * 2 / segments
        segment_len = gap * 0.6

        for i in range(segments):
            angle_start = rotation + i * gap
            angle_end = angle_start + segment_len

            rect = pygame.Rect(
                cx - radius, cy - radius,
                radius * 2, radius * 2,
            )
            pygame.draw.arc(screen, color, rect, angle_start, angle_end, 2)
