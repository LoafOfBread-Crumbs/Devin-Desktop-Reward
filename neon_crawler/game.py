"""Main game logic and loop."""

import os
import pickle
from .constants import c, TILES, ENEMIES, WEAPONS, IMPLANTS, FOV_RADIUS
from .dungeon import make_map
from .fov import recompute_fov
from .player import Player
from .ui import render, prompt_input, show_game_over, show_help, show_credits


SCORES_PATH = os.path.join(os.path.dirname(__file__), '..', 'scores.dat')
GAME_SAVE_PATH = os.path.join(os.path.dirname(__file__), '..', 'save.dat')


def load_scores():
    try:
        with open(SCORES_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return []


def save_scores(scores):
    try:
        with open(SCORES_PATH, 'wb') as f:
            pickle.dump(scores, f)
    except Exception:
        pass


def add_score(name, score, floor):
    scores = load_scores()
    scores.append({'name': name[:3] or '???', 'score': score, 'floor': floor})
    scores.sort(key=lambda e: e['score'], reverse=True)
    save_scores(scores[:5])
    return scores[:5]


def load_game():
    try:
        with open(GAME_SAVE_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception:
        return None


def save_game(game):
    try:
        with open(GAME_SAVE_PATH, 'wb') as f:
            pickle.dump(game, f)
        return True
    except Exception:
        return False


def delete_save():
    try:
        os.remove(GAME_SAVE_PATH)
    except Exception:
        pass


def get_item_name(item):
    if item.kind == 'health':
        return 'Nano-Medkit'
    if item.kind == 'weapon':
        return item.data['name']
    if item.kind == 'implant':
        return item.data['name']
    return 'Unknown'


class Game:
    def __init__(self, continue_saved=False):
        self.messages = []
        self.dungeon_level = 1
        self.player = None
        self.map = None
        self.visible = set()
        self.killed_by = None
        self.scores = load_scores()
        if continue_saved:
            saved = load_game()
            if saved:
                self.__dict__.update(saved.__dict__)
                self.log('Continued saved game.')
            else:
                self.generate_floor()
        else:
            self.generate_floor()

    def generate_floor(self):
        self.map, sx, sy = make_map(self.dungeon_level)
        if self.player is None:
            self.player = Player(sx, sy)
        else:
            self.player.x, self.player.y = sx, sy
        self.visible = set()
        self.recompute_fov()
        self.log(f'Entered floor {self.dungeon_level}.')

    def recompute_fov(self):
        self.visible = recompute_fov(self.map, self.player.x, self.player.y, FOV_RADIUS)

    def log(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 50:
            self.messages.pop(0)

    def handle_input(self, key):
        key = key.lower().strip()
        if not key:
            return True  # wait turn

        if key == 'q':
            save_game(self)
            self.log('Game saved.')
            return False
        if key == 'h' or key == '?':
            show_help()
            input(c('muted', '  Press Enter to continue...'))
            return True
        if key == 'c':
            show_credits()
            input(c('muted', '  Press Enter to continue...'))
            return True

        dx, dy = 0, 0
        if key == 'w' or key == 'k':
            dy = -1
        elif key == 's' or key == 'j':
            dy = 1
        elif key == 'a' or key == 'h':
            dx = -1
        elif key == 'd' or key == 'l':
            dx = 1
        elif key == '.':
            pass  # wait
        elif key == 'g':
            self.pick_up()
            return True
        elif key == 'i':
            self.show_inventory()
            return True
        elif key == '>':
            self.take_stairs()
            return True
        else:
            self.log("Unknown command. Press '?' for help.")
            return True

        if dx != 0 or dy != 0:
            self.move_player(dx, dy)

        self.enemy_turn()
        self.recompute_fov()
        return self.player.hp > 0

    def move_player(self, dx, dy):
        tx, ty = self.player.x + dx, self.player.y + dy
        if self.map.is_blocked(tx, ty):
            return

        enemy = next((e for e in self.map.enemies if e.alive and e.x == tx and e.y == ty), None)
        if enemy:
            self.attack(self.player, enemy)
        else:
            self.player.move(dx, dy)

    def pick_up(self):
        item = next((i for i in self.map.items if i.x == self.player.x and i.y == self.player.y), None)
        if not item:
            self.log('Nothing here to pick up.')
            return
        self.map.items.remove(item)
        if item.kind == 'health':
            self.player.heal(15)
            self.log('You inject a Nano-Medkit. HP restored.')
        elif item.kind == 'weapon':
            self.player.atk_bonus = item.data['dmg_bonus']
            self.player.weapon_name = item.data['name']
            self.log(f'Equipped {item.data["name"]}.')
        elif item.kind == 'implant':
            self.player.max_hp += item.data['hp_bonus']
            self.player.hp += item.data['hp_bonus']
            self.player.atk_bonus += item.data['atk_bonus']
            self.log(f'Installed {item.data["name"]}.')

    def show_inventory(self):
        self.log(f"Weapon: {self.player.weapon_name} | Max HP: {self.player.max_hp} | ATK: {self.player.atk}")

    def take_stairs(self):
        if self.map.stairs and (self.player.x, self.player.y) == self.map.stairs:
            self.dungeon_level += 1
            self.player.dungeon_level = self.dungeon_level
            self.player.score += 50
            self.generate_floor()
        else:
            self.log('No stairs here.')

    def attack(self, attacker, defender):
        import random
        damage = max(1, attacker.atk + random.randint(-1, 1))
        defender.hp -= damage
        if defender.hp <= 0:
            defender.alive = False
            if isinstance(attacker, Player):
                leveled = self.player.add_xp(defender.xp)
                self.log(f'You kill the {defender.name} for {defender.xp} XP.')
                if leveled:
                    self.log(f'Level up! You are now level {leveled}.')
            else:
                self.killed_by = attacker.name
                self.log(f'The {attacker.name} kills you.')
        else:
            if isinstance(attacker, Player):
                self.log(f'You hit {defender.name} for {damage} dmg.')
            else:
                self.log(f'{attacker.name} hits you for {damage} dmg.')

    def enemy_turn(self):
        import random
        for enemy in self.map.enemies:
            if not enemy.alive:
                continue
            dist = abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y)
            if dist == 1:
                self.attack(enemy, self.player)
                if self.player.hp <= 0:
                    return
            elif dist <= 6:
                # Move toward player.
                dx = 0 if enemy.x == self.player.x else (1 if enemy.x < self.player.x else -1)
                dy = 0 if enemy.y == self.player.y else (1 if enemy.y < self.player.y else -1)
                # Try horizontal then vertical.
                if dx != 0 and not self.map.is_blocked(enemy.x + dx, enemy.y):
                    enemy_at = next((e for e in self.map.enemies if e.alive and e.x == enemy.x + dx and e.y == enemy.y), None)
                    if not enemy_at:
                        enemy.x += dx
                elif dy != 0 and not self.map.is_blocked(enemy.x, enemy.y + dy):
                    enemy_at = next((e for e in self.map.enemies if e.alive and e.x == enemy.x and e.y == enemy.y + dy), None)
                    if not enemy_at:
                        enemy.y += dy
            elif random.random() < 0.3:
                # Wander.
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                nx, ny = enemy.x + dx, enemy.y + dy
                if not self.map.is_blocked(nx, ny):
                    enemy_at = next((e for e in self.map.enemies if e.alive and e.x == nx and e.y == ny), None)
                    if not enemy_at:
                        enemy.x, enemy.y = nx, ny

    def run(self):
        while True:
            render(self, self.messages)
            try:
                key = prompt_input()
            except EOFError:
                break
            alive = self.handle_input(key)
            if not alive:
                break
        self.game_over(bot_mode=False)

    def run_bot(self, delay=0.05, silent=False, snapshot_every=0, max_turns=0):
        from .bot import Bot
        import time
        bot = Bot()
        turns = 0
        while self.player.hp > 0:
            if not silent:
                render(self, self.messages)
            cmd = bot.next_command(self)
            old_floor = self.player.dungeon_level
            alive = self.handle_input(cmd)
            if self.player.dungeon_level != old_floor:
                bot.reset_floor()
            turns += 1
            if max_turns and turns >= max_turns:
                self.log(f'Bot stopped after {turns} turns.')
                break
            if not alive:
                break
            if snapshot_every and turns % snapshot_every == 0:
                render(self, self.messages)
                print(f'  [Turn {turns}] Bot snapshot')
            if delay > 0:
                time.sleep(delay)
        if silent:
            render(self, self.messages)
        self.game_over(bot_mode=True)
        return turns

    def game_over(self, bot_mode=False):
        delete_save()
        name = show_game_over(self.player, self.killed_by or 'an enemy', self.scores, bot_mode=bot_mode)
        if self.player.hp <= 0 and name:
            self.scores = add_score(name, self.player.score, self.player.dungeon_level)
