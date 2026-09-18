"""Procedural dungeon generation."""

import random
from .constants import (
    MAP_WIDTH, MAP_HEIGHT, ROOM_MAX_SIZE, ROOM_MIN_SIZE,
    MAX_ROOMS, MAX_ENEMIES_PER_ROOM, MAX_ITEMS_PER_ROOM,
    ENEMIES, WEAPONS, IMPLANTS
)


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    @property
    def center(self):
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersects(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.block_sight = block_sight if block_sight is not None else blocked
        self.explored = False


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.rooms = []
        self.stairs = None
        self.enemies = []
        self.items = []

    def initialize_tiles(self):
        return [[Tile(True) for _ in range(self.height)] for _ in range(self.width)]

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.tiles[x][y].blocked


def place_entities(room, dungeon, dungeon_level, is_start_room, is_last_room):
    if is_start_room:
        return

    if is_last_room and dungeon_level % 5 == 0:
        # Boss room.
        bx, by = room.center
        dungeon.enemies.append(Enemy(bx, by, 'B', {
            'name': 'Neon Overlord',
            'hp': 60 + dungeon_level * 10,
            'atk': 10 + dungeon_level,
            'xp': 200 + dungeon_level * 20
        }, dungeon_level))
        dungeon.items.append(Item(bx + 1, by, 'health'))
        return

    num_enemies = random.randint(0, MAX_ENEMIES_PER_ROOM)
    num_items = random.randint(0, MAX_ITEMS_PER_ROOM)

    for _ in range(num_enemies):
        x = random.randint(room.x1 + 1, room.x2 - 2)
        y = random.randint(room.y1 + 1, room.y2 - 2)
        if any(e.x == x and e.y == y for e in dungeon.enemies):
            continue
        roll = random.random()
        if dungeon_level < 3:
            kind = 's'
        elif dungeon_level < 6:
            kind = 'g' if roll < 0.7 else 's'
        else:
            kind = 'D' if roll < 0.3 else 'g' if roll < 0.8 else 's'
        template = ENEMIES[kind]
        dungeon.enemies.append(Enemy(x, y, kind, template, dungeon_level))

    for _ in range(num_items):
        x = random.randint(room.x1 + 1, room.x2 - 2)
        y = random.randint(room.y1 + 1, room.y2 - 2)
        if any(i.x == x and i.y == y for i in dungeon.items):
            continue
        roll = random.random()
        if roll < 0.5:
            dungeon.items.append(Item(x, y, 'health'))
        elif roll < 0.8:
            weapon = random.choice(WEAPONS)
            dungeon.items.append(Item(x, y, 'weapon', weapon))
        else:
            implant = random.choice(IMPLANTS)
            dungeon.items.append(Item(x, y, 'implant', implant))


class Entity:
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char


class Enemy(Entity):
    def __init__(self, x, y, kind, template, dungeon_level):
        super().__init__(x, y, kind)
        self.kind = kind
        self.name = template['name']
        self.max_hp = template['hp'] + dungeon_level * 2
        self.hp = self.max_hp
        self.atk = template['atk'] + dungeon_level // 2
        self.xp = template['xp'] + dungeon_level * 2
        self.alive = True


class Item(Entity):
    def __init__(self, x, y, kind, data=None):
        super().__init__(x, y, kind)
        self.kind = kind
        self.data = data


def make_map(dungeon_level=1):
    dungeon = GameMap(MAP_WIDTH, MAP_HEIGHT)
    rooms = []

    for _ in range(MAX_ROOMS):
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = random.randint(0, MAP_WIDTH - w - 1)
        y = random.randint(0, MAP_HEIGHT - h - 1)
        new_room = Rect(x, y, w, h)

        failed = False
        for other in rooms:
            if new_room.intersects(other):
                failed = True
                break
        if failed:
            continue

        dungeon.create_room(new_room)
        (new_x, new_y) = new_room.center

        if len(rooms) == 0:
            start_x, start_y = new_x, new_y
        else:
            (prev_x, prev_y) = rooms[-1].center
            if random.randint(0, 1) == 1:
                dungeon.create_h_tunnel(prev_x, new_x, prev_y)
                dungeon.create_v_tunnel(prev_y, new_y, new_x)
            else:
                dungeon.create_v_tunnel(prev_y, new_y, prev_x)
                dungeon.create_h_tunnel(prev_x, new_x, new_y)

        is_start = len(rooms) == 0
        is_last = len(rooms) == MAX_ROOMS - 1
        place_entities(new_room, dungeon, dungeon_level, is_start, is_last)
        rooms.append(new_room)

    # Place stairs in the last room.
    if rooms:
        sx, sy = rooms[-1].center
        dungeon.stairs = (sx, sy)

    return dungeon, start_x, start_y
