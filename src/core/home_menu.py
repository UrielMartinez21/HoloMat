import math
import time
import pygame


class AppCircle:
    """Círculo de app en el menú radial estilo HoloMat."""

    def __init__(
        self,
        name,
        radius,
        final_pos,
        center_pos,
        is_main=False,
        image_path=None
    ):
        self.name = name
        self.radius = radius
        self.final_pos = final_pos
        self.center_pos = center_pos
        self.is_main = is_main

        # Posición actual (empieza en el centro)
        self.cx = float(center_pos[0])
        self.cy = float(center_pos[1])

        self.visible = is_main
        self.is_hovered = False
        self.hover_start_time = 0

        # Animación
        self.animation_start_time = None
        self.is_animating = False
        self.animation_duration = 0.4

        # Escala de hover (crece al pasar el dedo)
        self.hover_scale = 1.0

        # Imagen opcional
        self.image = None
        if image_path:
            try:
                img = pygame.image.load(image_path)
                size = int(radius * 2)
                self.image = pygame.transform.scale(img, (size, size))
            except (pygame.error, FileNotFoundError):
                pass

    @property
    def pos(self):
        return (int(self.cx), int(self.cy))

    def contains(self, px, py):
        """Verifica si un punto está dentro del círculo."""
        dx = px - self.cx
        dy = py - self.cy
        return math.sqrt(dx * dx + dy * dy) <= self.radius * self.hover_scale

    def start_animation(self, showing):
        """Inicia animación de aparecer/desaparecer."""
        self.animation_start_time = time.time()
        self.is_animating = True
        self.visible = showing

    def update_animation(self):
        """Actualiza posición durante la animación."""
        if not self.is_animating or self.animation_start_time is None:
            return

        elapsed = time.time() - self.animation_start_time
        t = min(elapsed / self.animation_duration, 1.0)

        # Easing: ease-out cubic
        t = 1 - (1 - t) ** 3

        if self.visible:
            self.cx = self.center_pos[0] + (self.final_pos[0] - self.center_pos[0]) * t
            self.cy = self.center_pos[1] + (self.final_pos[1] - self.center_pos[1]) * t
        else:
            self.cx = self.final_pos[0] + (self.center_pos[0] - self.final_pos[0]) * t
            self.cy = self.final_pos[1] + (self.center_pos[1] - self.final_pos[1]) * t

        if t >= 1.0:
            self.is_animating = False
            self.animation_start_time = None

            if self.visible:
                self.cx = float(self.final_pos[0])
                self.cy = float(self.final_pos[1])
            else:
                self.cx = float(self.center_pos[0])
                self.cy = float(self.center_pos[1])

    def update_hover(self, px, py):
        """Actualiza estado de hover. Solo si es visible o es el main."""
        was_hovered = self.is_hovered
        self.is_hovered = self.contains(px, py) and (self.visible or self.is_main)

        if self.is_hovered and not was_hovered:
            self.hover_start_time = time.time()

        if not self.is_hovered:
            self.hover_start_time = 0
            self.hover_scale = 1.0
        else:
            elapsed = time.time() - self.hover_start_time
            self.hover_scale = 1.0 + min(elapsed * 0.3, 0.2)

    def get_hover_duration(self):
        """Retorna cuánto tiempo lleva en hover."""
        if not self.is_hovered or self.hover_start_time == 0:
            return 0
        return time.time() - self.hover_start_time


class HomeMenu:
    """Menú radial estilo HoloMat con círculo central y apps alrededor."""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center = (screen_width // 2, screen_height // 2)

        self.main_radius = 70
        self.app_radius = 55
        self.orbit_distance = 180

        self.apps_visible = False
        self.last_toggle_time = 0
        self.toggle_cooldown = 1.0  # Tiempo de hover en HOME para toggle

        self.select_delay = 0.8  # Tiempo de hover en app para seleccionar

        # Colores
        self.color_primary = (173, 216, 230)
        self.color_bg = (20, 20, 40)
        self.color_white = (255, 255, 255)
        self.color_hover = (200, 255, 255)
        self.color_selected = (100, 255, 100)

        # Fuentes
        self.font_main = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_app = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_hint = pygame.font.SysFont("Consolas", 12)

        # Círculos
        self.circles = []
        self.main_circle = None

        # Círculo que está cargando (para dibujar progreso)
        self.loading_circle = None
        self.loading_progress = 0.0

    def setup(self, app_names, app_images=None):
        """Configura el menú con los nombres de apps."""
        if app_images is None:
            app_images = {}

        self.circles = []

        # Círculo principal (Home)
        self.main_circle = AppCircle(
            name="HOME",
            radius=self.main_radius,
            final_pos=self.center,
            center_pos=self.center,
            is_main=True
        )
        self.circles.append(self.main_circle)

        # Círculos de apps
        num_apps = len(app_names)
        angle_step = 360 / max(num_apps, 1)

        for i, name in enumerate(app_names):
            angle = math.radians(angle_step * i - 90)
            x = self.center[0] + int(self.orbit_distance * math.cos(angle))
            y = self.center[1] + int(self.orbit_distance * math.sin(angle))

            image_path = app_images.get(name, None)

            circle = AppCircle(
                name=name,
                radius=self.app_radius,
                final_pos=(x, y),
                center_pos=self.center,
                image_path=image_path
            )
            self.circles.append(circle)

    def update(self, finger_x, finger_y):
        """
        Actualiza el menú con la posición del dedo.
        Retorna el nombre del app seleccionada o None.
        """
        current_time = time.time()
        self.loading_circle = None
        self.loading_progress = 0.0

        # Actualizar animaciones y hover
        for circle in self.circles:
            circle.update_animation()
            circle.update_hover(finger_x, finger_y)

        # Hover en Home → toggle apps
        if self.main_circle.is_hovered:
            duration = self.main_circle.get_hover_duration()

            if duration >= self.toggle_cooldown:
                if current_time - self.last_toggle_time > self.toggle_cooldown:
                    self.apps_visible = not self.apps_visible
                    self.last_toggle_time = current_time
                    self.main_circle.hover_start_time = 0

                    for circle in self.circles[1:]:
                        circle.start_animation(self.apps_visible)

            elif duration > 0:
                self.loading_circle = self.main_circle
                self.loading_progress = min(duration / self.toggle_cooldown, 1.0)

            return None

        # Hover en apps → seleccionar
        if self.apps_visible:
            for circle in self.circles[1:]:
                if circle.visible and circle.is_hovered and not circle.is_animating:
                    duration = circle.get_hover_duration()

                    if duration >= self.select_delay:
                        return circle.name

                    elif duration > 0:
                        self.loading_circle = circle
                        self.loading_progress = min(duration / self.select_delay, 1.0)

        return None

    def update_no_hand(self):
        """Actualiza cuando no hay mano detectada."""
        for circle in self.circles:
            circle.update_animation()
            circle.is_hovered = False
            circle.hover_start_time = 0
            circle.hover_scale = 1.0

        self.loading_circle = None
        self.loading_progress = 0.0

    def draw(self, screen):
        """Dibuja el menú radial completo."""
        # Líneas de conexión
        if self.apps_visible:
            for circle in self.circles[1:]:
                if circle.visible or circle.is_animating:
                    pygame.draw.line(
                        screen, (40, 40, 60),
                        self.center, circle.pos, 1
                    )

        # Círculos de apps
        for circle in self.circles[1:]:
            if circle.visible or circle.is_animating:
                self._draw_circle(screen, circle)

        # Círculo Home (al frente)
        self._draw_circle(screen, self.main_circle)

        # Progreso de carga en el círculo correspondiente
        if self.loading_circle and self.loading_progress > 0.05:
            self._draw_loading_arc(screen, self.loading_circle)

    def _draw_circle(self, screen, circle):
        """Dibuja un círculo individual del menú."""
        pos = circle.pos
        radius = int(circle.radius * circle.hover_scale)

        if circle.is_hovered:
            color = self.color_hover
            thickness = 4
        else:
            color = self.color_primary
            thickness = 3

        # Fondo del círculo
        bg_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(
            bg_surface, (20, 20, 40, 180),
            (radius, radius), radius
        )
        screen.blit(bg_surface, (pos[0] - radius, pos[1] - radius))

        # Imagen si tiene
        if circle.image and not circle.is_main:
            img_size = int(circle.radius * 2 * circle.hover_scale)
            scaled_img = pygame.transform.scale(circle.image, (img_size, img_size))

            mask_surface = pygame.Surface((img_size, img_size), pygame.SRCALPHA)
            pygame.draw.circle(
                mask_surface, (255, 255, 255, 255),
                (img_size // 2, img_size // 2), img_size // 2
            )

            img_masked = pygame.Surface((img_size, img_size), pygame.SRCALPHA)
            img_masked.blit(scaled_img, (0, 0))
            img_masked.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

            screen.blit(img_masked, (pos[0] - img_size // 2, pos[1] - img_size // 2))

        # Borde
        pygame.draw.circle(screen, color, pos, radius, thickness)

        # Texto
        if circle.is_main:
            font = self.font_main
        else:
            font = self.font_app

        if circle.image is None or circle.is_main:
            text_surface = font.render(circle.name, True, color)
            text_rect = text_surface.get_rect(center=pos)
            screen.blit(text_surface, text_rect)

        if circle.image and not circle.is_main:
            label = self.font_hint.render(circle.name, True, color)
            label_rect = label.get_rect(centerx=pos[0], top=pos[1] + radius + 5)
            screen.blit(label, label_rect)

    def _draw_loading_arc(self, screen, circle):
        """Dibuja un arco de progreso alrededor del círculo que se está cargando."""
        pos = circle.pos
        radius = int(circle.radius * circle.hover_scale) + 8

        rect = pygame.Rect(
            pos[0] - radius, pos[1] - radius,
            radius * 2, radius * 2
        )

        start_angle = math.pi / 2
        end_angle = start_angle + (2 * math.pi * self.loading_progress)

        if self.loading_progress >= 0.9:
            color = self.color_selected
        else:
            color = self.color_hover

        pygame.draw.arc(screen, color, rect, start_angle, end_angle, 3)
