"""Constants and styling for Neon Crawler."""

import sys

MAP_WIDTH = 50
MAP_HEIGHT = 20
ROOM_MAX_SIZE = 8
ROOM_MIN_SIZE = 4
MAX_ROOMS = 12
MAX_ENEMIES_PER_ROOM = 3
MAX_ITEMS_PER_ROOM = 2

FOV_RADIUS = 10

COLORS = {
    'reset': '\033[0m',
    'wall': '\033[38;5;240m',
    'floor': '\033[38;5;235m',
    'player': '\033[38;5;51m',
    'enemy': '\033[38;5;196m',
    'enemy_weak': '\033[38;5;208m',
    'enemy_strong': '\033[38;5;201m',
    'health': '\033[38;5;46m',
    'weapon': '\033[38;5;226m',
    'implant': '\033[38;5;93m',
    'stairs': '\033[38;5;255m',
    'text': '\033[38;5;252m',
    'hp_low': '\033[38;5;196m',
    'hp_mid': '\033[38;5;220m',
    'hp_high': '\033[38;5;46m',
    'muted': '\033[38;5;245m',
    'gold': '\033[38;5;220m',
}

TILES = {
    'wall': '#',
    'floor': '.',
    'player': '@',
    'stairs': '>',
    'enemy_weak': 's',
    'enemy': 'g',
    'enemy_strong': 'D',
    'health': '+',
    'weapon': '/',
    'implant': '*',
    'corpse': '%',
}

WEAPONS = [
    {'name': 'Shiv', 'dmg_bonus': 0, 'crit': 0.05},
    {'name': 'Mono-Blade', 'dmg_bonus': 2, 'crit': 0.10},
    {'name': 'Plasma Cutter', 'dmg_bonus': 4, 'crit': 0.12},
    {'name': 'Rail-Spike', 'dmg_bonus': 6, 'crit': 0.15},
    {'name': 'Void Saber', 'dmg_bonus': 10, 'crit': 0.20},
]

IMPLANTS = [
    {'name': 'Subdermal Plating', 'hp_bonus': 10, 'atk_bonus': 0},
    {'name': 'Neural Overclock', 'hp_bonus': 0, 'atk_bonus': 2},
    {'name': 'Adrenal Pump', 'hp_bonus': 5, 'atk_bonus': 1},
    {'name': 'Synth-Heart', 'hp_bonus': 15, 'atk_bonus': 0},
    {'name': 'Combat Chip', 'hp_bonus': 0, 'atk_bonus': 4},
]

ENEMIES = {
    's': {'name': 'Scrapper', 'hp': 8, 'atk': 2, 'xp': 5},
    'g': {'name': 'Ganger', 'hp': 14, 'atk': 4, 'xp': 10},
    'D': {'name': 'Dreadnought', 'hp': 28, 'atk': 7, 'xp': 25},
}


def supports_color():
    """Return True if the terminal probably supports ANSI colors."""
    if sys.platform == 'win32':
        return True  # Assume modern Windows Terminal; colorama not required.
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


USE_COLOR = supports_color()


def c(name, text):
    """Wrap text in an ANSI color if supported."""
    if not USE_COLOR:
        return text
    return f"{COLORS.get(name, '')}{text}{COLORS['reset']}"


def floor_theme(dungeon_level):
    """Return a theme tuple (wall_color, floor_color) for a given floor."""
    themes = [
        ('wall', 'floor'),
        ('muted', 'text'),
        ('enemy_weak', 'hp_mid'),
        ('enemy', 'hp_high'),
        ('enemy_strong', 'weapon'),
    ]
    return themes[(dungeon_level - 1) % len(themes)]
