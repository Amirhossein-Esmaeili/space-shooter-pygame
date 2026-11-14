import pygame
import random
import math
import json
import os
import sys

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
FPS = 60
LEADERBOARD_FILE = "leaderboard.json"

COLOR_BG = (6, 8, 18)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (0, 240, 255)
COLOR_BLUE = (0, 130, 255)
COLOR_MAGENTA = (255, 0, 128)
COLOR_ORANGE = (255, 140, 0)
COLOR_YELLOW = (255, 225, 40)
COLOR_GREEN = (0, 255, 140)
COLOR_RED = (255, 45, 70)
COLOR_PURPLE = (180, 50, 255)
COLOR_GRAY = (130, 145, 170)
COLOR_GOLD = (255, 215, 0)
COLOR_SILVER = (210, 220, 235)
COLOR_BRONZE = (215, 135, 75)

def get_chamfer_points(x, y, w, h, cut=14):
    return [
        (x + cut, y),
        (x + w - cut, y),
        (x + w, y + cut),
        (x + w, y + h - cut),
        (x + w - cut, y + h),
        (x + cut, y + h),
        (x, y + h - cut),
        (x, y + cut)
    ]

def draw_glow_polygon(surface, color, points, width=0, glow_size=6):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_x, max_x = min(xs) - glow_size * 2, max(xs) + glow_size * 2
    min_y, max_y = min(ys) - glow_size * 2, max(ys) + glow_size * 2
    w = max(1, int(max_x - min_x))
    h = max(1, int(max_y - min_y))
    glow_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    local_pts = [(p[0] - min_x, p[1] - min_y) for p in points]
    for i in range(glow_size, 0, -2):
        alpha = int(65 * (1 - i / glow_size))
        pygame.draw.polygon(glow_surf, (*color[:3], alpha), local_pts, i * 2)
    pygame.draw.polygon(glow_surf, (*color[:3], 255), local_pts, width)
    surface.blit(glow_surf, (int(min_x), int(min_y)), special_flags=pygame.BLEND_ALPHA_SDL2)

class SpriteFactory:
    @staticmethod
    def create_player_ship():
        w, h = 96, 96
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        outer_wings = [
            (cx, cy - 30),
            (cx - 42, cy + 20),
            (cx - 38, cy + 32),
            (cx - 14, cy + 22),
            (cx + 14, cy + 22),
            (cx + 38, cy + 32),
            (cx + 42, cy + 20)
        ]
        pygame.draw.polygon(surf, (18, 36, 68), outer_wings)
        pygame.draw.polygon(surf, (40, 90, 150), outer_wings, 2)

        for side in (-1, 1):
            bx = cx + side * 26
            pygame.draw.rect(surf, (80, 100, 130), (bx - 3, cy - 16, 6, 26), border_radius=2)
            pygame.draw.rect(surf, COLOR_CYAN, (bx - 2, cy - 22, 4, 8))
            pygame.draw.line(surf, COLOR_CYAN, (cx + side * 12, cy - 4), (cx + side * 36, cy + 22), 2)

        mid_armor = [
            (cx, cy - 38),
            (cx - 24, cy + 14),
            (cx - 12, cy + 28),
            (cx + 12, cy + 28),
            (cx + 24, cy + 14)
        ]
        pygame.draw.polygon(surf, (32, 65, 115), mid_armor)
        pygame.draw.polygon(surf, COLOR_CYAN, mid_armor, 2)

        fuselage = [
            (cx, cy - 44),
            (cx - 12, cy + 8),
            (cx - 7, cy + 34),
            (cx + 7, cy + 34),
            (cx + 12, cy + 8)
        ]
        pygame.draw.polygon(surf, (210, 230, 250), fuselage)
        pygame.draw.polygon(surf, (90, 150, 210), fuselage, 2)

        visor = [
            (cx, cy - 24),
            (cx - 6, cy - 4),
            (cx, cy + 10),
            (cx + 6, cy - 4)
        ]
        pygame.draw.polygon(surf, (0, 180, 220), visor)
        pygame.draw.polygon(surf, COLOR_WHITE, [
            (cx, cy - 20),
            (cx - 3, cy - 5),
            (cx, cy + 4),
            (cx + 3, cy - 5)
        ])

        for side in (-1, 1):
            nx = cx + side * 8
            pygame.draw.rect(surf, (35, 45, 65), (nx - 5, cy + 30, 10, 8), border_radius=2)
            pygame.draw.rect(surf, COLOR_CYAN, (nx - 3, cy + 34, 6, 4))

        return surf

    @staticmethod
    def create_interceptor():
        w, h = 84, 84
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        for side in (-1, 1):
            cx_gun = cx + side * 22
            pygame.draw.rect(surf, (70, 25, 45), (cx_gun - 3, cy + 6, 6, 22))
            pygame.draw.circle(surf, COLOR_MAGENTA, (cx_gun, cy + 28), 4)
            pygame.draw.rect(surf, (45, 20, 40), (cx + side * 9 - 4, cy - 32, 8, 8))

        wings = [
            (cx, cy + 20),
            (cx - 36, cy - 22),
            (cx - 28, cy + 18),
            (cx - 12, cy + 8),
            (cx + 12, cy + 8),
            (cx + 28, cy + 18),
            (cx + 36, cy - 22)
        ]
        pygame.draw.polygon(surf, (55, 14, 38), wings)
        pygame.draw.polygon(surf, (190, 30, 100), wings, 2)

        armor_plates = [
            (cx, cy + 34),
            (cx - 15, cy - 8),
            (cx - 8, cy - 28),
            (cx + 8, cy - 28),
            (cx + 15, cy - 8)
        ]
        pygame.draw.polygon(surf, (110, 22, 65), armor_plates)
        pygame.draw.polygon(surf, COLOR_MAGENTA, armor_plates, 2)

        visor = [
            (cx, cy + 20),
            (cx - 6, cy + 2),
            (cx, cy - 10),
            (cx + 6, cy + 2)
        ]
        pygame.draw.polygon(surf, COLOR_RED, visor)
        pygame.draw.polygon(surf, (255, 200, 220), [
            (cx, cy + 15),
            (cx - 3, cy + 3),
            (cx, cy - 4),
            (cx + 3, cy + 3)
        ])

        return surf

    @staticmethod
    def create_gunship():
        w, h = 104, 104
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        for side in (-1, 1):
            for offset in (18, 28):
                gx = cx + side * offset
                pygame.draw.rect(surf, (70, 35, 25), (gx - 3, cy + 10, 6, 24))
                pygame.draw.rect(surf, COLOR_ORANGE, (gx - 2, cy + 30, 4, 5))
            pygame.draw.rect(surf, (50, 30, 25), (cx + side * 14 - 6, cy - 38, 12, 10), border_radius=2)

        wings = [
            (cx - 18, cy - 28),
            (cx - 46, cy - 10),
            (cx - 42, cy + 20),
            (cx - 16, cy + 26),
            (cx + 16, cy + 26),
            (cx + 42, cy + 20),
            (cx + 46, cy - 10),
            (cx + 18, cy - 28)
        ]
        pygame.draw.polygon(surf, (65, 24, 18), wings)
        pygame.draw.polygon(surf, (200, 75, 30), wings, 2)

        shoulder_pads = [
            (cx - 14, cy - 32),
            (cx - 28, cy - 4),
            (cx - 20, cy + 28),
            (cx + 20, cy + 28),
            (cx + 28, cy - 4),
            (cx + 14, cy - 32)
        ]
        pygame.draw.polygon(surf, (105, 38, 25), shoulder_pads)
        pygame.draw.polygon(surf, COLOR_ORANGE, shoulder_pads, 2)

        hull = [
            (cx, cy + 38),
            (cx - 14, cy + 18),
            (cx - 12, cy - 30),
            (cx + 12, cy - 30),
            (cx + 14, cy + 18)
        ]
        pygame.draw.polygon(surf, (145, 55, 30), hull)
        pygame.draw.polygon(surf, COLOR_YELLOW, hull, 2)

        visor = [
            (cx - 9, cy + 8),
            (cx + 9, cy + 8),
            (cx + 6, cy + 22),
            (cx - 6, cy + 22)
        ]
        pygame.draw.polygon(surf, COLOR_YELLOW, visor)
        pygame.draw.polygon(surf, COLOR_WHITE, [
            (cx - 5, cy + 11),
            (cx + 5, cy + 11),
            (cx + 3, cy + 18),
            (cx - 3, cy + 18)
        ])

        return surf

    @staticmethod
    def create_dreadnought():
        w, h = 136, 136
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = w // 2, h // 2

        for side in (-1, 1):
            tx = cx + side * 38
            pygame.draw.rect(surf, (60, 25, 85), (tx - 7, cy + 8, 14, 30), border_radius=3)
            pygame.draw.circle(surf, COLOR_PURPLE, (tx, cy + 38), 6)
            pygame.draw.circle(surf, COLOR_WHITE, (tx, cy + 38), 3)
            pygame.draw.rect(surf, (45, 20, 65), (cx + side * 20 - 7, cy - 50, 14, 12), border_radius=2)

        outer_hull = [
            (cx - 26, cy - 44),
            (cx - 62, cy - 16),
            (cx - 54, cy + 28),
            (cx - 24, cy + 44),
            (cx + 24, cy + 44),
            (cx + 54, cy + 28),
            (cx + 62, cy - 16),
            (cx + 26, cy - 44)
        ]
        pygame.draw.polygon(surf, (38, 14, 58), outer_hull)
        pygame.draw.polygon(surf, (130, 45, 200), outer_hull, 3)

        inner_plating = [
            (cx - 18, cy - 38),
            (cx - 40, cy - 8),
            (cx - 32, cy + 30),
            (cx, cy + 48),
            (cx + 32, cy + 30),
            (cx + 40, cy - 8),
            (cx + 18, cy - 38)
        ]
        pygame.draw.polygon(surf, (72, 26, 108), inner_plating)
        pygame.draw.polygon(surf, COLOR_PURPLE, inner_plating, 2)

        for y_bar in (-20, -6, 8):
            pygame.draw.line(surf, (150, 80, 220), (cx - 24, cy + y_bar), (cx + 24, cy + y_bar), 2)

        pygame.draw.circle(surf, (120, 20, 180), (cx, cy + 16), 15)
        pygame.draw.circle(surf, COLOR_MAGENTA, (cx, cy + 16), 11)
        pygame.draw.circle(surf, COLOR_WHITE, (cx, cy + 16), 6)

        return surf

class Button:
    def __init__(self, center_x, center_y, width, height, text, icon_type, base_color=COLOR_CYAN, hover_color=COLOR_MAGENTA):
        self.cx = center_x
        self.cy = center_y
        self.width = width
        self.height = height
        self.text = text
        self.icon_type = icon_type
        self.base_color = base_color
        self.hover_color = hover_color
        self.hover_progress = 0.0
        self.sweep_pos = -0.4
        self.press_scale = 1.0
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.rect = pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)

    def update(self, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        target = 1.0 if hovered else 0.0
        self.hover_progress += (target - self.hover_progress) * 0.18
        if self.hover_progress > 0.02:
            self.sweep_pos += 0.035
            if self.sweep_pos > 1.4:
                self.sweep_pos = -0.4
        else:
            self.sweep_pos = -0.4
        self.press_scale += (1.0 - self.press_scale) * 0.25

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.press_scale = 0.93
                return True
        return False

    def draw_icon(self, surface, cx, cy, color):
        if self.icon_type == "play":
            pts = [(cx - 7, cy - 10), (cx - 7, cy + 10), (cx + 11, cy)]
            pygame.draw.polygon(surface, color, pts)
        elif self.icon_type == "trophy":
            pygame.draw.polygon(surface, color, [(cx - 9, cy - 9), (cx + 9, cy - 9), (cx + 6, cy + 1), (cx - 6, cy + 1)], 2)
            pygame.draw.line(surface, color, (cx, cy + 1), (cx, cy + 8), 2)
            pygame.draw.line(surface, color, (cx - 7, cy + 8), (cx + 7, cy + 8), 3)
            pygame.draw.arc(surface, color, (cx - 13, cy - 8, 6, 8), math.pi / 2, math.pi * 1.5, 2)
            pygame.draw.arc(surface, color, (cx + 7, cy - 8, 6, 8), -math.pi / 2, math.pi / 2, 2)
        elif self.icon_type == "retry":
            pygame.draw.arc(surface, color, (cx - 10, cy - 10, 20, 20), 0.6, math.pi * 1.85, 3)
            pygame.draw.polygon(surface, color, [(cx + 4, cy - 12), (cx + 12, cy - 9), (cx + 7, cy - 2)])
        elif self.icon_type == "back":
            pygame.draw.line(surface, color, (cx + 10, cy), (cx - 8, cy), 3)
            pygame.draw.lines(surface, color, False, [(cx - 1, cy - 8), (cx - 9, cy), (cx - 1, cy + 8)], 3)
        elif self.icon_type == "quit":
            pygame.draw.line(surface, color, (cx - 8, cy - 8), (cx + 8, cy + 8), 3)
            pygame.draw.line(surface, color, (cx + 8, cy - 8), (cx - 8, cy + 8), 3)
        elif self.icon_type == "pilot":
            pygame.draw.circle(surface, color, (cx, cy - 4), 5, 2)
            pygame.draw.arc(surface, color, (cx - 10, cy + 1, 20, 16), 0, math.pi, 2)
        elif self.icon_type == "check":
            pygame.draw.lines(surface, color, False, [(cx - 9, cy), (cx - 2, cy + 7), (cx + 10, cy - 7)], 3)

    def draw(self, surface):
        pad = 24
        base_w = self.width + pad * 2
        base_h = self.height + pad * 2
        btn_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)

        t = self.hover_progress
        border_col = (
            int(self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * t),
            int(self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * t),
            int(self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * t)
        )

        outer_pts = get_chamfer_points(pad, pad, self.width, self.height, cut=13)
        inner_pts = get_chamfer_points(pad + 4, pad + 4, self.width - 8, self.height - 8, cut=10)

        if t > 0.01:
            for g in range(12, 0, -3):
                alpha = int(55 * t * (1 - g / 12))
                pygame.draw.polygon(btn_surf, (*border_col, alpha), outer_pts, g * 2)

        bg_col = (
            int(14 + 28 * t),
            int(22 + 18 * t),
            int(44 + 40 * t),
            235
        )
        pygame.draw.polygon(btn_surf, bg_col, outer_pts)
        pygame.draw.polygon(btn_surf, (int(24 + 40 * t), int(38 + 30 * t), int(72 + 55 * t), 210), inner_pts)

        if t > 0.05:
            sweep_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
            sx = int(pad + self.sweep_pos * self.width)
            sweep_poly = [
                (sx - 35, pad),
                (sx + 10, pad),
                (sx - 20, pad + self.height),
                (sx - 65, pad + self.height)
            ]
            pygame.draw.polygon(sweep_surf, (255, 255, 255, int(65 * t)), sweep_poly)
            mask_surf = pygame.Surface((base_w, base_h), pygame.SRCALPHA)
            pygame.draw.polygon(mask_surf, (255, 255, 255, 255), outer_pts)
            sweep_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            btn_surf.blit(sweep_surf, (0, 0))

        pygame.draw.polygon(btn_surf, border_col, outer_pts, 2)
        pygame.draw.polygon(btn_surf, (*border_col, int(90 + 110 * t)), inner_pts, 1)

        corner_c = COLOR_WHITE if t > 0.5 else border_col
        pygame.draw.line(btn_surf, corner_c, (pad + 15, pad + 3), (pad + 42, pad + 3), 3)
        pygame.draw.line(btn_surf, corner_c, (pad + self.width - 42, pad + self.height - 3), (pad + self.width - 15, pad + self.height - 3), 3)

        icon_x = pad + 34
        icon_y = pad + self.height // 2
        icon_col = COLOR_WHITE if t > 0.4 else border_col
        self.draw_icon(btn_surf, icon_x, icon_y, icon_col)
        pygame.draw.line(btn_surf, (*border_col, 120), (pad + 58, pad + 10), (pad + 58, pad + self.height - 10), 1)

        txt_col = COLOR_WHITE if t > 0.2 else (215, 235, 255)
        txt_surf = self.font.render(self.text, True, txt_col)
        txt_x = pad + 64 + (self.width - 74 - txt_surf.get_width()) // 2
        txt_y = pad + self.height // 2 - txt_surf.get_height() // 2
        btn_surf.blit(txt_surf, (txt_x, txt_y))

        scale = (1.0 + 0.065 * t) * self.press_scale
        if abs(scale - 1.0) > 0.003:
            scaled_w = int(base_w * scale)
            scaled_h = int(base_h * scale)
            btn_surf = pygame.transform.smoothscale(btn_surf, (scaled_w, scaled_h))

        surface.blit(btn_surf, (self.cx - btn_surf.get_width() // 2, self.cy - btn_surf.get_height() // 2))

class TextInputBox:
    def __init__(self, center_x, center_y, width, height, max_len=12):
        self.cx = center_x
        self.cy = center_y
        self.width = width
        self.height = height
        self.max_len = max_len
        self.text = ""
        self.type_pulse = 0.0
        self.scan_pos = 0.0
        self.font_input = pygame.font.SysFont("consolas", 32, bold=True)
        self.font_meta = pygame.font.SysFont("consolas", 15, bold=True)
        self.rect = pygame.Rect(center_x - width // 2, center_y - height // 2, width, height)

    def handle_key(self, event, particles=None):
        if event.key == pygame.K_BACKSPACE:
            if len(self.text) > 0:
                self.text = self.text[:-1]
                self.type_pulse = 1.0
                if particles:
                    particles.create_hit_sparks(self.cx, self.cy, COLOR_MAGENTA, count=8)
            return True
        elif event.key not in (pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_TAB):
            ch = event.unicode
            if ch and (ch.isalnum() or ch in ("_", "-", " ")) and len(self.text) < self.max_len:
                if ch == " " and len(self.text) == 0:
                    return False
                self.text += ch.upper()
                self.type_pulse = 1.0
                if particles:
                    particles.create_hit_sparks(self.cx + len(self.text) * 10 - 60, self.cy, COLOR_CYAN, count=10)
                return True
        return False

    def update(self):
        self.type_pulse = max(0.0, self.type_pulse - 0.06)
        self.scan_pos = (self.scan_pos + 0.015) % 1.0

    def draw(self, surface):
        pad = 28
        surf_w = self.width + pad * 2
        surf_h = self.height + pad * 2
        box_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)

        p = self.type_pulse
        border_col = (
            int(COLOR_CYAN[0] + (COLOR_MAGENTA[0] - COLOR_CYAN[0]) * p),
            int(COLOR_CYAN[1] + (COLOR_MAGENTA[1] - COLOR_CYAN[1]) * p),
            int(COLOR_CYAN[2] + (COLOR_MAGENTA[2] - COLOR_CYAN[2]) * p)
        )

        outer_pts = get_chamfer_points(pad, pad, self.width, self.height, cut=16)
        inner_pts = get_chamfer_points(pad + 5, pad + 5, self.width - 10, self.height - 10, cut=12)

        glow_layers = int(8 + 8 * p)
        for g in range(glow_layers, 0, -2):
            alpha = int((35 + 45 * p) * (1 - g / max(1, glow_layers)))
            pygame.draw.polygon(box_surf, (*border_col, alpha), outer_pts, g * 2)

        pygame.draw.polygon(box_surf, (12, 20, 44, 230), outer_pts)
        pygame.draw.polygon(box_surf, (20, 34, 70, 195), inner_pts)

        scan_x = int(pad + 16 + self.scan_pos * (self.width - 32))
        pygame.draw.line(box_surf, (*border_col, 90), (scan_x, pad + 6), (scan_x, pad + self.height - 6), 2)

        pygame.draw.polygon(box_surf, border_col, outer_pts, 2 + int(p * 2))
        pygame.draw.polygon(box_surf, (*COLOR_WHITE, int(80 + 140 * p)), inner_pts, 1)

        bracket_col = COLOR_WHITE if p > 0.3 else COLOR_CYAN
        pygame.draw.lines(box_surf, bracket_col, False, [
            (pad - 6, pad + 26), (pad - 6, pad + 10), (pad + 12, pad - 6), (pad + 36, pad - 6)
        ], 3)
        pygame.draw.lines(box_surf, bracket_col, False, [
            (pad + self.width + 6, pad + self.height - 26),
            (pad + self.width + 6, pad + self.height - 10),
            (pad + self.width - 12, pad + self.height + 6),
            (pad + self.width - 36, pad + self.height + 6)
        ], 3)

        display_str = self.text
        txt_surf = self.font_input.render(display_str, True, COLOR_WHITE)
        tx = pad + self.width // 2 - txt_surf.get_width() // 2
        ty = pad + self.height // 2 - txt_surf.get_height() // 2 - 4
        box_surf.blit(txt_surf, (tx, ty))

        if (pygame.time.get_ticks() // 320) % 2 == 0 or p > 0.2:
            cur_x = tx + txt_surf.get_width() + 4
            cur_y = ty + 4
            pygame.draw.rect(box_surf, COLOR_CYAN if p < 0.3 else COLOR_MAGENTA, (cur_x, cur_y, 14, txt_surf.get_height() - 8), border_radius=2)

        bar_w = self.width - 56
        bar_x = pad + 28
        bar_y = pad + self.height - 14
        pygame.draw.rect(box_surf, (25, 40, 75), (bar_x, bar_y, bar_w, 5), border_radius=2)
        fill_ratio = len(self.text) / self.max_len
        if fill_ratio > 0:
            fill_c = COLOR_GREEN if len(self.text) >= 3 else COLOR_YELLOW
            pygame.draw.rect(box_surf, fill_c, (bar_x, bar_y, int(bar_w * fill_ratio), 5), border_radius=2)

        surface.blit(box_surf, (self.cx - surf_w // 2, self.cy - surf_h // 2))

        counter_col = COLOR_CYAN if len(self.text) < self.max_len else COLOR_YELLOW
        counter_txt = self.font_meta.render(f"{len(self.text)} / {self.max_len}", True, counter_col)
        surface.blit(counter_txt, (self.cx - counter_txt.get_width() // 2, self.cy + self.height // 2 + 10))

class LeaderboardManager:
    def __init__(self, filename=LEADERBOARD_FILE):
        self.filename = filename
        self.scores = self.load_scores()

    def load_scores(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                best_by_pilot = {}
                for entry in data:
                    if isinstance(entry, dict) and "name" in entry and "score" in entry:
                        pname = str(entry["name"]).strip().upper()[:12]
                        if not pname:
                            pname = "PLAYER"
                        sc = int(entry["score"])
                        if pname not in best_by_pilot or sc > best_by_pilot[pname]:
                            best_by_pilot[pname] = sc
                deduped = [{"name": k, "score": v} for k, v in best_by_pilot.items()]
                deduped.sort(key=lambda x: x["score"], reverse=True)
                return deduped[:5]
        except Exception:
            return []

    def add_score(self, name, score):
        clean_name = name.strip().upper()[:12] if name.strip() else "PLAYER"
        score_val = int(score)

        existing = None
        for entry in self.scores:
            if entry["name"].upper() == clean_name:
                existing = entry
                break

        if existing is not None:
            if score_val > existing["score"]:
                existing["score"] = score_val
        else:
            self.scores.append({"name": clean_name, "score": score_val})

        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:5]
        self.save_scores()

    def save_scores(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.scores, f, indent=4)
        except Exception:
            pass

    def get_high_score(self):
        if not self.scores:
            return 0
        return self.scores[0]["score"]

    def get_pilot_best(self, name):
        clean = name.strip().upper()[:12]
        for entry in self.scores:
            if entry["name"].upper() == clean:
                return entry["score"]
        return 0

    def get_rank(self, current_score):
        rank = 1
        for entry in self.scores:
            if current_score < entry["score"]:
                rank += 1
        return rank

class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, decay=0.95):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_lifetime = lifetime
        self.lifetime = lifetime
        self.decay = decay

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.decay
        self.vy *= self.decay
        self.lifetime -= 1

    def draw(self, surface, offset=(0, 0)):
        if self.lifetime <= 0:
            return
        ratio = self.lifetime / self.max_lifetime
        alpha = max(0, min(255, int(255 * ratio)))
        cur_size = max(1, int(self.size * ratio))
        surf = pygame.Surface((cur_size * 4, cur_size * 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color[:3], alpha // 3), (cur_size * 2, cur_size * 2), cur_size * 2)
        pygame.draw.circle(surf, (*self.color[:3], alpha), (cur_size * 2, cur_size * 2), cur_size)
        surface.blit(surf, (int(self.x - cur_size * 2 + offset[0]), int(self.y - cur_size * 2 + offset[1])))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, vx, vy, color, size, lifetime, decay=0.95):
        self.particles.append(Particle(x, y, vx, vy, color, size, lifetime, decay))

    def create_explosion(self, x, y, color, count=40, speed_range=(2, 9.5)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            size = random.uniform(2.2, 6.2)
            lifetime = random.randint(22, 48)
            c = color if random.random() > 0.28 else COLOR_WHITE
            self.emit(x, y, vx, vy, c, size, lifetime, decay=0.94)

    def create_hit_sparks(self, x, y, color, count=14):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.8, 6.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.emit(x, y, vx, vy, color, random.uniform(1.5, 3.8), random.randint(10, 22), decay=0.92)

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.lifetime > 0]

    def draw(self, surface, offset=(0, 0)):
        for p in self.particles:
            p.draw(surface, offset)

class Starfield:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = []
        self.nebulae = []
        for layer in range(1, 5):
            count = 45 if layer == 1 else (30 if layer == 2 else (18 if layer == 3 else 10))
            for _ in range(count):
                x = random.uniform(0, width)
                y = random.uniform(0, height)
                speed = (layer ** 1.35) * 0.65 + random.uniform(0, 0.3)
                size = 1 if layer < 3 else (2 if layer == 3 else 3)
                color = random.choice([
                    (180, 210, 255),
                    (255, 225, 200),
                    (140, 240, 255),
                    (220, 175, 255)
                ])
                self.stars.append([x, y, speed, size, color, layer])

        nebula_colors = [
            (70, 12, 110, 24),
            (10, 60, 120, 24),
            (110, 15, 70, 20),
            (12, 95, 95, 22)
        ]
        for _ in range(7):
            nx = random.uniform(0, width)
            ny = random.uniform(0, height)
            radius = random.randint(160, 290)
            speed = random.uniform(0.25, 0.55)
            color = random.choice(nebula_colors)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            for r in range(radius, 0, -14):
                alpha = int(color[3] * (1 - (r / radius) ** 1.5))
                pygame.draw.circle(surf, (color[0], color[1], color[2], alpha), (radius, radius), r)
            self.nebulae.append([nx, ny, speed, radius, surf])

    def update(self, speed_mult=1.0):
        for n in self.nebulae:
            n[1] += n[2] * speed_mult
            if n[1] - n[3] > self.height:
                n[1] = -n[3]
                n[0] = random.uniform(0, self.width)

        for s in self.stars:
            s[1] += s[2] * speed_mult
            if s[1] > self.height:
                s[1] = 0
                s[0] = random.uniform(0, self.width)

    def draw(self, surface, offset=(0, 0)):
        for n in self.nebulae:
            surface.blit(n[4], (int(n[0] - n[3] + offset[0] * 0.3), int(n[1] - n[3] + offset[1] * 0.3)))
        for s in self.stars:
            x = int(s[0] + offset[0] * 0.5)
            y = int(s[1] + offset[1] * 0.5)
            if s[5] == 4:
                pygame.draw.line(surface, (*s[4], 150), (x, y - 5), (x, y + 5), 1)
                pygame.draw.line(surface, (*s[4], 150), (x - 5, y), (x + 5, y), 1)
            pygame.draw.circle(surface, s[4], (x, y), s[3])

class Projectile:
    def __init__(self, x, y, vx, vy, color=COLOR_CYAN, damage=1, radius=5, proj_type="laser"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.damage = damage
        self.radius = radius
        self.proj_type = proj_type
        self.alive = True
        self.tick = 0

    def update(self, particles=None):
        self.x += self.vx
        self.y += self.vy
        self.tick += 1
        if particles and self.tick % 2 == 0:
            if self.proj_type == "orb":
                particles.emit(
                    self.x + random.uniform(-3, 3),
                    self.y + random.uniform(-3, 3),
                    -self.vx * 0.15,
                    -self.vy * 0.15,
                    self.color,
                    random.uniform(2.5, 4.5),
                    random.randint(8, 15)
                )
            elif self.proj_type == "enemy_bolt":
                particles.emit(
                    self.x,
                    self.y - 6,
                    random.uniform(-0.3, 0.3),
                    -self.vy * 0.1,
                    self.color,
                    random.uniform(1.5, 2.8),
                    random.randint(6, 11)
                )
        if self.y < -40 or self.y > SCREEN_HEIGHT + 40 or self.x < -40 or self.x > SCREEN_WIDTH + 40:
            self.alive = False

    def draw(self, surface, offset=(0, 0)):
        ox, oy = int(self.x + offset[0]), int(self.y + offset[1])
        if self.proj_type == "player_laser":
            glow_surf = pygame.Surface((26, 48), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, (*self.color[:3], 65), (13, 4), (13, 44), 11)
            pygame.draw.line(glow_surf, (*self.color[:3], 170), (13, 6), (13, 42), 6)
            pygame.draw.line(glow_surf, COLOR_WHITE, (13, 8), (13, 40), 2)
            surface.blit(glow_surf, (ox - 13, oy - 24), special_flags=pygame.BLEND_ALPHA_SDL2)
        elif self.proj_type == "enemy_bolt":
            glow_surf = pygame.Surface((24, 38), pygame.SRCALPHA)
            pygame.draw.line(glow_surf, (*self.color[:3], 75), (12, 4), (12, 34), 10)
            pygame.draw.line(glow_surf, (*self.color[:3], 200), (12, 6), (12, 32), 5)
            pygame.draw.line(glow_surf, COLOR_WHITE, (12, 8), (12, 30), 2)
            surface.blit(glow_surf, (ox - 12, oy - 19), special_flags=pygame.BLEND_ALPHA_SDL2)
        else:
            r = self.radius + 10
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            for rad in range(r, self.radius, -2):
                alpha = int(95 * (1 - (rad - self.radius) / max(1, (r - self.radius))))
                pygame.draw.circle(glow_surf, (*self.color[:3], alpha), (r, r), rad)
            pygame.draw.circle(glow_surf, self.color, (r, r), self.radius + 1)
            pygame.draw.circle(glow_surf, COLOR_WHITE, (r, r), max(2, self.radius - 2))
            surface.blit(glow_surf, (ox - r, oy - r), special_flags=pygame.BLEND_ALPHA_SDL2)

class Player:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.accel = 0.9
        self.friction = 0.88
        self.max_speed = 8.5
        self.radius = 24
        self.max_health = 100
        self.health = 100
        self.shoot_cooldown = 0
        self.shoot_delay = 9
        self.invulnerable_timer = 0
        self.shield_pulse = 0.0
        self.base_sprite = sprite
        self.muzzle_flash = 0

    def update(self, keys, particles):
        ax, ay = 0.0, 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= self.accel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += self.accel
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= self.accel
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += self.accel

        if ax != 0 and ay != 0:
            ax *= 0.7071
            ay *= 0.7071

        self.vx = (self.vx + ax) * self.friction
        self.vy = (self.vy + ay) * self.friction

        speed = math.hypot(self.vx, self.vy)
        if speed > self.max_speed:
            self.vx = (self.vx / speed) * self.max_speed
            self.vy = (self.vy / speed) * self.max_speed

        self.x += self.vx
        self.y += self.vy

        margin = 36
        if self.x < margin:
            self.x = margin
            self.vx = 0
        elif self.x > SCREEN_WIDTH - margin:
            self.x = SCREEN_WIDTH - margin
            self.vx = 0

        if self.y < 75:
            self.y = 75
            self.vy = 0
        elif self.y > SCREEN_HEIGHT - margin:
            self.y = SCREEN_HEIGHT - margin
            self.vy = 0

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        if self.muzzle_flash > 0:
            self.muzzle_flash -= 1

        self.shield_pulse += 0.12

        for side in (-8, 8):
            px = self.x + side + random.uniform(-1.5, 1.5)
            py = self.y + 34
            pvx = self.vx * 0.2 + random.uniform(-0.5, 0.5)
            pvy = random.uniform(3.0, 5.5)
            color = random.choice([COLOR_CYAN, COLOR_BLUE, COLOR_WHITE])
            particles.emit(px, py, pvx, pvy, color, random.uniform(2.2, 4.2), random.randint(9, 16), decay=0.9)

    def try_shoot(self, projectiles):
        if self.shoot_cooldown <= 0:
            projectiles.append(Projectile(self.x - 26, self.y - 20, 0, -15.5, COLOR_CYAN, damage=1, radius=4, proj_type="player_laser"))
            projectiles.append(Projectile(self.x + 26, self.y - 20, 0, -15.5, COLOR_CYAN, damage=1, radius=4, proj_type="player_laser"))
            self.shoot_cooldown = self.shoot_delay
            self.muzzle_flash = 3
            return True
        return False

    def draw(self, surface, offset=(0, 0)):
        ox = self.x + offset[0]
        oy = self.y + offset[1]

        flame_len = random.randint(14, 26)
        for side in (-8, 8):
            nx = ox + side
            ny = oy + 34
            flame_pts = [(nx - 4, ny), (nx + 4, ny), (nx, ny + flame_len)]
            pygame.draw.polygon(surface, COLOR_CYAN, flame_pts)
            pygame.draw.polygon(surface, COLOR_WHITE, [(nx - 2, ny), (nx + 2, ny), (nx, ny + flame_len - 6)])

        angle = -self.vx * 1.6
        rotated = pygame.transform.rotozoom(self.base_sprite, angle, 1.0)
        surface.blit(rotated, (int(ox - rotated.get_width() // 2), int(oy - rotated.get_height() // 2)))

        if self.muzzle_flash > 0:
            for side in (-26, 26):
                pygame.draw.circle(surface, COLOR_CYAN, (int(ox + side), int(oy - 22)), 8)
                pygame.draw.circle(surface, COLOR_WHITE, (int(ox + side), int(oy - 22)), 4)

        shield_alpha = int(40 + 22 * math.sin(self.shield_pulse))
        if self.invulnerable_timer > 0:
            shield_alpha = 160 if (self.invulnerable_timer // 3) % 2 == 0 else 35
        shield_surf = pygame.Surface((92, 92), pygame.SRCALPHA)
        pygame.draw.circle(shield_surf, (*COLOR_CYAN, shield_alpha), (46, 46), 42, 2)
        pygame.draw.circle(shield_surf, (*COLOR_CYAN, shield_alpha // 4), (46, 46), 40)
        surface.blit(shield_surf, (int(ox - 46), int(oy - 46)))

class Asteroid:
    def __init__(self, x, y, size_tier=2, difficulty=1.0):
        self.x = x
        self.y = y
        self.size_tier = size_tier
        self.radius = 16 if size_tier == 1 else (28 if size_tier == 2 else 42)
        self.max_health = size_tier * 2 + int(difficulty * 0.8)
        self.health = self.max_health
        self.score_value = size_tier * 20
        self.vy = random.uniform(1.6, 3.2) * (1.0 + difficulty * 0.08) * (1.3 if size_tier == 1 else 1.0)
        self.vx = random.uniform(-1.3, 1.3)
        self.angle = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-0.035, 0.035)
        self.num_vertices = random.randint(9, 13)
        self.offsets = [random.uniform(self.radius * 0.78, self.radius * 1.15) for _ in range(self.num_vertices)]
        self.color = COLOR_ORANGE if size_tier == 3 else (COLOR_YELLOW if size_tier == 2 else COLOR_GRAY)
        self.alive = True
        self.hit_flash = 0

    def update(self, player, enemy_projectiles, particles):
        self.x += self.vx
        self.y += self.vy
        self.angle += self.rot_speed
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.y - self.radius > SCREEN_HEIGHT + 50 or self.x < -70 or self.x > SCREEN_WIDTH + 70:
            self.alive = False

    def get_points(self, offset=(0, 0), scale=1.0):
        pts = []
        for i in range(self.num_vertices):
            a = self.angle + (i / self.num_vertices) * math.pi * 2
            r = self.offsets[i] * scale
            pts.append((self.x + math.cos(a) * r + offset[0], self.y + math.sin(a) * r + offset[1]))
        return pts

    def draw(self, surface, offset=(0, 0)):
        pts = self.get_points(offset, 1.0)
        inner_pts = self.get_points(offset, 0.55)
        color = COLOR_WHITE if self.hit_flash > 0 else self.color
        pygame.draw.polygon(surface, (28, 24, 38), pts)
        pygame.draw.polygon(surface, (42, 36, 55), inner_pts)
        draw_glow_polygon(surface, color, pts, width=2, glow_size=4)

class EnemyShip:
    def __init__(self, x, y, enemy_type, difficulty, sprites):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.alive = True
        self.hit_flash = 0
        self.time = random.uniform(0, 100)
        self.sprite = sprites[enemy_type]
        self.flash_sprite = self.sprite.copy()
        self.flash_sprite.fill((220, 220, 220, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if enemy_type == "interceptor":
            self.radius = 24
            self.max_health = 3 + int(difficulty * 0.6)
            self.vy = 3.1 * (1 + difficulty * 0.05)
            self.vx = 0.0
            self.color = COLOR_MAGENTA
            self.score_value = 35
            self.shoot_cooldown = random.randint(55, 110)
            self.thrusters = [(-9, -32), (9, -32)]
            self.cannons = [(-22, 28), (22, 28)]
        elif enemy_type == "gunship":
            self.radius = 30
            self.max_health = 6 + int(difficulty * 1.1)
            self.vy = 2.0 * (1 + difficulty * 0.04)
            self.vx = 0.0
            self.color = COLOR_ORANGE
            self.score_value = 65
            self.shoot_cooldown = random.randint(50, 95)
            self.thrusters = [(-14, -38), (14, -38)]
            self.cannons = [(-28, 32), (-18, 32), (18, 32), (28, 32)]
        else:
            self.radius = 40
            self.max_health = 14 + int(difficulty * 2.0)
            self.vy = 1.15 * (1 + difficulty * 0.03)
            self.vx = 0.0
            self.color = COLOR_PURPLE
            self.score_value = 130
            self.shoot_cooldown = random.randint(55, 90)
            self.thrusters = [(-20, -50), (20, -50)]
            self.cannons = [(-38, 38), (0, 32), (38, 38)]

        self.health = self.max_health

    def update(self, player, enemy_projectiles, particles):
        self.time += 0.06
        if self.enemy_type == "interceptor":
            self.vx = math.sin(self.time) * 3.2
        elif self.enemy_type == "gunship":
            diff_x = player.x - self.x
            self.vx = max(-2.2, min(2.2, diff_x * 0.03))
        else:
            self.vx = math.cos(self.time * 0.45) * 1.3

        self.x += self.vx
        self.y += self.vy
        self.x = max(45, min(SCREEN_WIDTH - 45, self.x))

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if random.random() < 0.7:
            for tx, ty in self.thrusters:
                particles.emit(
                    self.x + tx + random.uniform(-2, 2),
                    self.y + ty,
                    random.uniform(-0.3, 0.3),
                    random.uniform(-3.0, -1.2),
                    self.color,
                    random.uniform(2.2, 3.8),
                    random.randint(7, 13)
                )

        self.shoot_cooldown -= 1
        if self.shoot_cooldown <= 0 and 20 < self.y < SCREEN_HEIGHT - 140:
            if self.enemy_type == "interceptor":
                for cx_off, cy_off in self.cannons:
                    enemy_projectiles.append(
                        Projectile(self.x + cx_off, self.y + cy_off, 0, 8.2, COLOR_MAGENTA, damage=10, radius=4, proj_type="enemy_bolt")
                    )
                self.shoot_cooldown = random.randint(75, 120)
            elif self.enemy_type == "gunship":
                for cx_off in (-23, 23):
                    enemy_projectiles.append(
                        Projectile(self.x + cx_off, self.y + 32, 0, 8.8, COLOR_ORANGE, damage=12, radius=5, proj_type="enemy_bolt")
                    )
                self.shoot_cooldown = random.randint(65, 100)
            else:
                enemy_projectiles.append(
                    Projectile(self.x - 38, self.y + 38, -1.2, 6.8, COLOR_PURPLE, damage=16, radius=6, proj_type="orb")
                )
                enemy_projectiles.append(
                    Projectile(self.x + 38, self.y + 38, 1.2, 6.8, COLOR_PURPLE, damage=16, radius=6, proj_type="orb")
                )
                dx = player.x - self.x
                dy = max(60, player.y - self.y)
                dist = math.hypot(dx, dy)
                enemy_projectiles.append(
                    Projectile(self.x, self.y + 32, (dx / dist) * 7.2, (dy / dist) * 7.2, COLOR_MAGENTA, damage=18, radius=7, proj_type="orb")
                )
                self.shoot_cooldown = random.randint(80, 115)

        if self.y - self.radius > SCREEN_HEIGHT + 60:
            self.alive = False

    def draw(self, surface, offset=(0, 0)):
        ox = self.x + offset[0]
        oy = self.y + offset[1]

        flame_h = random.randint(10, 20)
        for tx, ty in self.thrusters:
            nx, ny = ox + tx, oy + ty
            pygame.draw.polygon(surface, self.color, [(nx - 4, ny), (nx + 4, ny), (nx, ny - flame_h)])
            pygame.draw.polygon(surface, COLOR_WHITE, [(nx - 2, ny), (nx + 2, ny), (nx, ny - flame_h + 4)])

        spr = self.flash_sprite if self.hit_flash > 0 else self.sprite
        surface.blit(spr, (int(ox - spr.get_width() // 2), int(oy - spr.get_height() // 2)))

        if self.health < self.max_health:
            bw = self.radius * 1.7
            bx = ox - bw / 2
            by = oy - self.radius - 14
            pygame.draw.rect(surface, (45, 18, 30), (bx, by, bw, 5), border_radius=2)
            pygame.draw.rect(surface, self.color, (bx, by, bw * (self.health / self.max_health), 5), border_radius=2)
            pygame.draw.rect(surface, COLOR_WHITE, (bx, by, bw, 5), 1, border_radius=2)

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("SPACE SHOOTER")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("consolas", 52, bold=True)
        self.font_subtitle = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_hud = pygame.font.SysFont("consolas", 19, bold=True)
        self.font_small = pygame.font.SysFont("consolas", 15, bold=True)

        self.player_sprite = SpriteFactory.create_player_ship()
        self.enemy_sprites = {
            "interceptor": SpriteFactory.create_interceptor(),
            "gunship": SpriteFactory.create_gunship(),
            "dreadnought": SpriteFactory.create_dreadnought()
        }

        self.leaderboard = LeaderboardManager()
        self.starfield = Starfield(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.particles = ParticleSystem()

        self.state = "ENTER_NAME"
        self.player_name = ""
        self.shake_timer = 0
        self.shake_magnitude = 0

        cx = SCREEN_WIDTH // 2
        self.name_input_box = TextInputBox(cx, 430, 480, 74, max_len=12)
        self.confirm_name_btn = Button(cx, 565, 340, 56, "CONFIRM", "check", COLOR_CYAN, COLOR_GREEN)

        self.menu_buttons = {
            "start": Button(cx, 430, 410, 52, "START MISSION", "play", COLOR_CYAN, COLOR_GREEN),
            "leaderboard": Button(cx, 498, 410, 52, "HALL OF FAME (LEADERBOARD)", "trophy", COLOR_CYAN, COLOR_YELLOW),
            "change_pilot": Button(cx, 566, 410, 52, "CHANGE PILOT", "pilot", COLOR_BLUE, COLOR_CYAN),
            "quit": Button(cx, 634, 410, 52, "QUIT", "quit", COLOR_RED, COLOR_MAGENTA)
        }
        self.leaderboard_back_btn = Button(cx, 668, 360, 54, "BACK TO MENU", "back", COLOR_CYAN, COLOR_MAGENTA)
        self.gameover_buttons = {
            "play_again": Button(cx - 195, 665, 340, 54, "PLAY AGAIN", "retry", COLOR_GREEN, COLOR_CYAN),
            "menu": Button(cx + 195, 665, 340, 54, "BACK TO MENU", "back", COLOR_CYAN, COLOR_MAGENTA)
        }

        self.reset_gameplay()

    def confirm_pilot_registration(self):
        cleaned = self.name_input_box.text.strip().upper()
        self.player_name = cleaned if cleaned else "PLAYER 1"
        self.name_input_box.text = self.player_name
        self.state = "MENU"

    def reset_gameplay(self):
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 95, self.player_sprite)
        self.player_projectiles = []
        self.enemy_projectiles = []
        self.enemies = []
        self.score = 0
        self.ticks = 0
        self.difficulty = 1.0
        self.spawn_timer = 40
        self.shake_timer = 0
        self.shake_magnitude = 0

    def trigger_shake(self, duration, magnitude):
        self.shake_timer = max(self.shake_timer, duration)
        self.shake_magnitude = max(self.shake_magnitude, magnitude)

    def get_shake_offset(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1
            return (
                random.randint(-self.shake_magnitude, self.shake_magnitude),
                random.randint(-self.shake_magnitude, self.shake_magnitude)
            )
        self.shake_magnitude = 0
        return (0, 0)

    def spawn_wave(self):
        x = random.randint(60, SCREEN_WIDTH - 60)
        roll = random.random()
        if roll < 0.35:
            tier = random.choices([1, 2, 3], weights=[35, 45, 20])[0]
            self.enemies.append(Asteroid(x, -55, size_tier=tier, difficulty=self.difficulty))
        elif roll < 0.68:
            self.enemies.append(EnemyShip(x, -55, "interceptor", self.difficulty, self.enemy_sprites))
        elif roll < 0.90:
            self.enemies.append(EnemyShip(x, -65, "gunship", self.difficulty, self.enemy_sprites))
        else:
            self.enemies.append(EnemyShip(x, -75, "dreadnought", self.difficulty, self.enemy_sprites))

    def update_playing(self):
        self.ticks += 1
        self.difficulty = 1.0 + (self.ticks / (FPS * 22.0))
        self.starfield.update(speed_mult=1.0 + (self.difficulty - 1.0) * 0.35)

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.particles)
        if keys[pygame.K_SPACE]:
            self.player.try_shoot(self.player_projectiles)

        self.spawn_timer -= 1
        if self.spawn_timer <= 0:
            self.spawn_wave()
            base_delay = max(14, int(54 - self.difficulty * 6))
            self.spawn_timer = random.randint(base_delay, base_delay + 20)

        for proj in self.player_projectiles:
            proj.update(self.particles)
        self.player_projectiles = [p for p in self.player_projectiles if p.alive]

        for proj in self.enemy_projectiles:
            proj.update(self.particles)
        self.enemy_projectiles = [p for p in self.enemy_projectiles if p.alive]

        for enemy in self.enemies:
            enemy.update(self.player, self.enemy_projectiles, self.particles)

        for proj in self.player_projectiles:
            for enemy in self.enemies:
                if not enemy.alive or not proj.alive:
                    continue
                dist = math.hypot(proj.x - enemy.x, proj.y - enemy.y)
                if dist < enemy.radius + proj.radius:
                    proj.alive = False
                    enemy.health -= proj.damage
                    enemy.hit_flash = 4
                    self.particles.create_hit_sparks(proj.x, proj.y, enemy.color, count=12)
                    if enemy.health <= 0:
                        enemy.alive = False
                        self.score += enemy.score_value
                        self.particles.create_explosion(enemy.x, enemy.y, enemy.color, count=42)
                        self.trigger_shake(10, 5)
                        if isinstance(enemy, Asteroid) and enemy.size_tier > 1:
                            for _ in range(2):
                                child = Asteroid(enemy.x, enemy.y, size_tier=enemy.size_tier - 1, difficulty=self.difficulty)
                                child.vx = random.uniform(-2.8, 2.8)
                                self.enemies.append(child)

        for proj in self.enemy_projectiles:
            if not proj.alive:
                continue
            dist = math.hypot(proj.x - self.player.x, proj.y - self.player.y)
            if dist < self.player.radius + proj.radius:
                proj.alive = False
                if self.player.invulnerable_timer <= 0:
                    self.player.health -= proj.damage
                    self.player.invulnerable_timer = 22
                    self.particles.create_hit_sparks(proj.x, proj.y, COLOR_CYAN, count=18)
                    self.trigger_shake(12, 7)

        for enemy in self.enemies:
            if not enemy.alive:
                continue
            dist = math.hypot(enemy.x - self.player.x, enemy.y - self.player.y)
            if dist < enemy.radius + self.player.radius - 4:
                enemy.alive = False
                self.particles.create_explosion(enemy.x, enemy.y, enemy.color, count=45)
                if self.player.invulnerable_timer <= 0:
                    self.player.health -= 34
                    self.player.invulnerable_timer = 35
                    self.trigger_shake(18, 11)

        self.enemies = [e for e in self.enemies if e.alive]
        self.particles.update()

        if self.player.health <= 0:
            self.player.health = 0
            self.particles.create_explosion(self.player.x, self.player.y, COLOR_CYAN, count=75, speed_range=(2, 12))
            self.trigger_shake(26, 14)
            self.leaderboard.add_score(self.player_name, self.score)
            self.state = "GAME_OVER"

    def draw_hud(self):
        hud_surf = pygame.Surface((SCREEN_WIDTH, 66), pygame.SRCALPHA)
        pts = [(0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, 52), (SCREEN_WIDTH - 30, 64), (30, 64), (0, 52)]
        pygame.draw.polygon(hud_surf, (10, 16, 36, 215), pts)
        pygame.draw.lines(hud_surf, COLOR_CYAN, False, [(0, 52), (30, 64), (SCREEN_WIDTH - 30, 64), (SCREEN_WIDTH, 52)], 2)
        self.screen.blit(hud_surf, (0, 0))

        bar_x, bar_y, bar_w, bar_h = 30, 28, 220, 18
        pygame.draw.rect(self.screen, (35, 18, 32), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        ratio = max(0.0, self.player.health / self.player.max_health)
        fill_color = COLOR_GREEN if ratio > 0.5 else (COLOR_YELLOW if ratio > 0.25 else COLOR_RED)
        if ratio > 0:
            pygame.draw.rect(self.screen, fill_color, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)

        hp_txt = self.font_small.render(f"SHIELD: {self.player.health}%", True, COLOR_WHITE)
        self.screen.blit(hp_txt, (bar_x, bar_y - 18))

        pilot_badge = self.font_hud.render(f"PILOT: {self.player_name}", True, COLOR_GREEN)
        self.screen.blit(pilot_badge, (280, 21))

        score_txt = self.font_subtitle.render(f"SCORE: {self.score:06d}", True, COLOR_CYAN)
        self.screen.blit(score_txt, (SCREEN_WIDTH // 2 + 25 - score_txt.get_width() // 2, 18))

        rank = self.leaderboard.get_rank(self.score)
        rank_txt = self.font_hud.render(f"RANK #{rank}  |  {self.difficulty:.1f}x", True, COLOR_YELLOW)
        self.screen.blit(rank_txt, (SCREEN_WIDTH - rank_txt.get_width() - 30, 21))

    def draw_cyber_header(self, title_str, subtitle_str, top_y):
        cx = SCREEN_WIDTH // 2
        t = pygame.time.get_ticks() * 0.004
        glow_val = int(160 + 85 * math.sin(t))

        plate_w, plate_h = 720, 108
        plate = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
        pts = get_chamfer_points(4, 4, plate_w - 8, plate_h - 8, cut=20)
        pygame.draw.polygon(plate, (12, 20, 44, 200), pts)
        pygame.draw.polygon(plate, (0, glow_val, 255), pts, 2)
        self.screen.blit(plate, (cx - plate_w // 2, top_y))

        shadow_surf = self.font_title.render(title_str, True, (0, 90, 160))
        title_surf = self.font_title.render(title_str, True, (200, 250, 255))
        self.screen.blit(shadow_surf, (cx - title_surf.get_width() // 2 + 3, top_y + 14))
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, top_y + 11))

        sub_surf = self.font_hud.render(subtitle_str, True, COLOR_MAGENTA)
        self.screen.blit(sub_surf, (cx - sub_surf.get_width() // 2, top_y + 72))

    def draw_rank_medal(self, surface, cx, cy, rank):
        if rank == 1:
            primary, rim = COLOR_GOLD, (255, 245, 160)
        elif rank == 2:
            primary, rim = COLOR_SILVER, COLOR_WHITE
        elif rank == 3:
            primary, rim = COLOR_BRONZE, (255, 195, 145)
        else:
            primary, rim = (45, 65, 100), COLOR_CYAN

        if rank <= 3:
            pygame.draw.polygon(surface, COLOR_RED, [(cx - 10, cy + 8), (cx - 16, cy + 24), (cx - 4, cy + 20)])
            pygame.draw.polygon(surface, COLOR_RED, [(cx + 10, cy + 8), (cx + 16, cy + 24), (cx + 4, cy + 20)])

        pts = []
        for i in range(6):
            a = math.pi / 6 + i * math.pi / 3
            pts.append((cx + math.cos(a) * 20, cy + math.sin(a) * 20))
        pygame.draw.polygon(surface, primary, pts)
        pygame.draw.polygon(surface, rim, pts, 2)

        num_surf = self.font_hud.render(str(rank), True, (15, 20, 30) if rank <= 3 else COLOR_WHITE)
        surface.blit(num_surf, (cx - num_surf.get_width() // 2, cy - num_surf.get_height() // 2))

    def draw_leaderboard_cards(self, start_y, row_h=64, gap=12):
        cx = SCREEN_WIDTH // 2
        card_w = 700
        scores = self.leaderboard.scores

        for i in range(5):
            rank = i + 1
            y = start_y + i * (row_h + gap)
            card = pygame.Surface((card_w, row_h), pygame.SRCALPHA)
            pts = get_chamfer_points(2, 2, card_w - 4, row_h - 4, cut=12)

            is_active_pilot = i < len(scores) and scores[i]["name"].upper() == self.player_name.upper()

            if rank == 1:
                border_c = COLOR_GOLD
                bg_c = (42, 36, 20, 220)
            elif rank == 2:
                border_c = COLOR_SILVER
                bg_c = (28, 34, 48, 220)
            elif rank == 3:
                border_c = COLOR_BRONZE
                bg_c = (40, 26, 24, 220)
            else:
                border_c = COLOR_GREEN if is_active_pilot else (0, 140, 210)
                bg_c = (18, 38, 48, 215) if is_active_pilot else (16, 24, 48, 200)

            pygame.draw.polygon(card, bg_c, pts)
            pygame.draw.polygon(card, border_c, pts, 3 if is_active_pilot else 2)

            self.draw_rank_medal(card, 48, row_h // 2 - 2, rank)

            if i < len(scores):
                name_str = scores[i]["name"]
                if is_active_pilot:
                    name_str += " (YOU)"
                score_str = f"{scores[i]['score']:07d} PTS"
                name_col = COLOR_GREEN if is_active_pilot else (COLOR_WHITE if rank <= 3 else (200, 220, 245))
                score_col = border_c if rank <= 3 else COLOR_CYAN
            else:
                name_str = "--- EMPTY ---"
                score_str = "0000000 PTS"
                name_col = (90, 105, 130)
                score_col = (80, 95, 120)

            name_surf = self.font_subtitle.render(name_str, True, name_col)
            score_surf = self.font_subtitle.render(score_str, True, score_col)
            card.blit(name_surf, (95, row_h // 2 - name_surf.get_height() // 2))
            card.blit(score_surf, (card_w - score_surf.get_width() - 30, row_h // 2 - score_surf.get_height() // 2))

            self.screen.blit(card, (cx - card_w // 2, y))

    def draw_enter_name_screen(self):
        self.draw_cyber_header("SPACE SHOOTER", "PLAYER REGISTRATION", 34)

        cx = SCREEN_WIDTH // 2
        panel_w, panel_h = 680, 480
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_pts = get_chamfer_points(4, 4, panel_w - 8, panel_h - 8, cut=24)
        pygame.draw.polygon(panel_surf, (10, 16, 36, 175), panel_pts)
        pygame.draw.polygon(panel_surf, (0, 150, 220, 160), panel_pts, 2)
        self.screen.blit(panel_surf, (cx - panel_w // 2, 165))

        t = pygame.time.get_ticks() * 0.004
        holo_y = 265
        holo_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(holo_surf, (*COLOR_CYAN, 30), (80, 80), 64)
        pygame.draw.circle(holo_surf, (*COLOR_CYAN, 150), (80, 80), 64, 2)
        for i in range(3):
            a = t + i * (math.pi * 2 / 3)
            pygame.draw.arc(holo_surf, COLOR_MAGENTA, (8, 8, 144, 144), a, a + 0.8, 3)
        self.screen.blit(holo_surf, (cx - 80, holo_y - 80))

        ship_preview = pygame.transform.smoothscale(self.player_sprite, (82, 82))
        self.screen.blit(ship_preview, (cx - 41, int(holo_y - 41 + math.sin(t * 1.5) * 5)))

        prompt_surf = self.font_subtitle.render("Enter your name:", True, COLOR_WHITE)
        self.screen.blit(prompt_surf, (cx - prompt_surf.get_width() // 2, 350))

        self.name_input_box.draw(self.screen)
        self.confirm_name_btn.draw(self.screen)

    def draw_menu(self):
        best_score = self.leaderboard.get_pilot_best(self.player_name)
        self.draw_cyber_header(
            "SPACE SHOOTER",
            f"PILOT: {self.player_name}   |   BEST SCORE: {best_score:06d}",
            30
        )

        cx = SCREEN_WIDTH // 2
        cy = 265
        t = pygame.time.get_ticks() * 0.003

        holo_surf = pygame.Surface((220, 220), pygame.SRCALPHA)
        pygame.draw.circle(holo_surf, (*COLOR_CYAN, 25), (110, 110), 88)
        pygame.draw.circle(holo_surf, (*COLOR_CYAN, 120), (110, 110), 88, 2)
        pygame.draw.circle(holo_surf, (*COLOR_MAGENTA, 90), (110, 110), 68, 1)

        for i in range(4):
            ang = t + i * (math.pi / 2)
            pygame.draw.arc(holo_surf, COLOR_CYAN, (12, 12, 196, 196), ang, ang + 0.7, 4)

        self.screen.blit(holo_surf, (cx - 110, cy - 110))

        hover_y = cy + math.sin(t * 1.4) * 7
        flame_len = random.randint(15, 26)
        for side in (-8, 8):
            nx, ny = cx + side, hover_y + 32
            pygame.draw.polygon(self.screen, COLOR_CYAN, [(nx - 4, ny), (nx + 4, ny), (nx, ny + flame_len)])
            pygame.draw.polygon(self.screen, COLOR_WHITE, [(nx - 2, ny), (nx + 2, ny), (nx, ny + flame_len - 6)])

        scaled_ship = pygame.transform.smoothscale(self.player_sprite, (102, 102))
        self.screen.blit(scaled_ship, (cx - 51, int(hover_y - 51)))

        for btn in self.menu_buttons.values():
            btn.draw(self.screen)

    def draw_leaderboard_screen(self):
        self.draw_cyber_header("LEADERBOARD", f"PILOT: {self.player_name}   |   TOP 5 PLAYERS", 30)
        self.draw_leaderboard_cards(start_y=170, row_h=72, gap=14)
        self.leaderboard_back_btn.draw(self.screen)

    def draw_game_over(self):
        high_score = max(self.score, self.leaderboard.get_high_score())
        self.draw_cyber_header(
            "GAME OVER",
            f"PILOT: {self.player_name}   |   SCORE: {self.score:06d}   |   HIGH SCORE: {high_score:06d}",
            22
        )

        cx = SCREEN_WIDTH // 2
        box_w, box_h = 700, 68
        bx = cx - box_w // 2
        by = 144
        box_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pts = get_chamfer_points(2, 2, box_w - 4, box_h - 4, cut=12)
        pygame.draw.polygon(box_surf, (16, 32, 48, 225), pts)
        pygame.draw.polygon(box_surf, COLOR_GREEN, pts, 2)
        self.screen.blit(box_surf, (bx, by))

        saved_txt = self.font_hud.render(
            f"Score saved for {self.player_name} in {LEADERBOARD_FILE}",
            True,
            COLOR_GREEN
        )
        self.screen.blit(saved_txt, (cx - saved_txt.get_width() // 2, by + 13))

        rank = self.leaderboard.get_rank(self.score)
        sub_txt = self.font_small.render(
            f"RANK: #{rank}   |   PERSONAL BEST: {self.leaderboard.get_pilot_best(self.player_name):06d} PTS",
            True,
            COLOR_YELLOW
        )
        self.screen.blit(sub_txt, (cx - sub_txt.get_width() // 2, by + 40))

        self.draw_leaderboard_cards(start_y=230, row_h=62, gap=11)

        for btn in self.gameover_buttons.values():
            btn.draw(self.screen)

    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()

            if self.state == "ENTER_NAME":
                self.name_input_box.update()
                self.confirm_name_btn.update(mouse_pos)
            elif self.state == "MENU":
                for btn in self.menu_buttons.values():
                    btn.update(mouse_pos)
            elif self.state == "LEADERBOARD":
                self.leaderboard_back_btn.update(mouse_pos)
            elif self.state == "GAME_OVER":
                for btn in self.gameover_buttons.values():
                    btn.update(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "ENTER_NAME":
                    if self.confirm_name_btn.check_click(event):
                        self.confirm_pilot_registration()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.confirm_pilot_registration()
                        else:
                            self.name_input_box.handle_key(event, self.particles)

                elif self.state == "MENU":
                    if self.menu_buttons["start"].check_click(event):
                        self.reset_gameplay()
                        self.state = "PLAYING"
                    elif self.menu_buttons["leaderboard"].check_click(event):
                        self.state = "LEADERBOARD"
                    elif self.menu_buttons["change_pilot"].check_click(event):
                        self.name_input_box.text = self.player_name
                        self.state = "ENTER_NAME"
                    elif self.menu_buttons["quit"].check_click(event):
                        running = False

                elif self.state == "LEADERBOARD":
                    if self.leaderboard_back_btn.check_click(event):
                        self.state = "MENU"
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "PLAYING":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state = "MENU"

                elif self.state == "GAME_OVER":
                    if self.gameover_buttons["play_again"].check_click(event):
                        self.reset_gameplay()
                        self.state = "PLAYING"
                    elif self.gameover_buttons["menu"].check_click(event):
                        self.state = "MENU"

            if self.state in ("ENTER_NAME", "MENU", "LEADERBOARD"):
                self.starfield.update(1.0)
                self.particles.update()
            elif self.state == "PLAYING":
                self.update_playing()
            elif self.state == "GAME_OVER":
                self.starfield.update(0.55)
                self.particles.update()

            offset = self.get_shake_offset()
            self.screen.fill(COLOR_BG)
            self.starfield.draw(self.screen, offset)

            if self.state == "ENTER_NAME":
                self.particles.draw(self.screen, offset)
                self.draw_enter_name_screen()

            elif self.state == "PLAYING":
                for proj in self.player_projectiles:
                    proj.draw(self.screen, offset)
                for proj in self.enemy_projectiles:
                    proj.draw(self.screen, offset)
                for enemy in self.enemies:
                    enemy.draw(self.screen, offset)
                self.player.draw(self.screen, offset)
                self.particles.draw(self.screen, offset)
                self.draw_hud()

            elif self.state == "MENU":
                self.particles.draw(self.screen, offset)
                self.draw_menu()

            elif self.state == "LEADERBOARD":
                self.particles.draw(self.screen, offset)
                self.draw_leaderboard_screen()

            elif self.state == "GAME_OVER":
                for enemy in self.enemies:
                    enemy.draw(self.screen, offset)
                self.particles.draw(self.screen, offset)
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()