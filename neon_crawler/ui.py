"""Rendering and UI helpers."""

import os
import platform
from .constants import (
    c, TILES, MAP_WIDTH, MAP_HEIGHT, COLORS
)


def clear_screen():
    """Clear the terminal."""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')


def render(game, messages):
    clear_screen()
    lines = []
    lines.append(c('text', '  +' + '-' * (MAP_WIDTH + 2) + '+'))

    for y in range(MAP_HEIGHT):
        row = ['  | ']
        for x in range(MAP_WIDTH):
            tile = game.map.tiles[x][y]
            visible = (x, y) in game.visible
            explored = tile.explored

            char = TILES['wall']
            color = 'wall'

            if visible:
                tile.explored = True
                if tile.blocked:
                    char = TILES['wall']
                    color = 'wall'
                else:
                    char = TILES['floor']
                    color = 'floor'

                # Entities draw on top.
                if (x, y) == (game.player.x, game.player.y):
                    char = TILES['player']
                    color = 'player'
                elif game.map.stairs and (x, y) == game.map.stairs:
                    char = TILES['stairs']
                    color = 'stairs'
                else:
                    enemy = next((e for e in game.map.enemies if e.x == x and e.y == y and e.alive), None)
                    if enemy:
                        char = enemy.char
                        if enemy.kind == 'D':
                            color = 'enemy_strong'
                        elif enemy.kind == 'g':
                            color = 'enemy'
                        else:
                            color = 'enemy_weak'
                    else:
                        item = next((i for i in game.map.items if i.x == x and i.y == y), None)
                        if item:
                            char = TILES[item.kind]
                            color = item.kind
            elif explored:
                if tile.blocked:
                    char = TILES['wall']
                    color = 'wall'
                else:
                    char = TILES['floor']
                    color = 'floor'

            row.append(c(color, char))
        row.append(c('text', ' |'))
        lines.append(''.join(row))

    lines.append(c('text', '  +' + '-' * (MAP_WIDTH + 2) + '+'))

    # Status panel.
    hp_color = 'hp_high' if game.player.hp > game.player.max_hp * 0.6 else 'hp_mid' if game.player.hp > game.player.max_hp * 0.3 else 'hp_low'
    status = (
        f"  HP: {c(hp_color, f'{game.player.hp}/{game.player.max_hp}')} | "
        f"Atk: {c('gold', str(game.player.atk))} | "
        f"Weapon: {c('weapon', game.player.weapon_name)} | "
        f"Level: {c('text', str(game.player.level))} | "
        f"XP: {c('text', f'{game.player.xp}/{game.player.xp_to_next}')} | "
        f"Floor: {c('text', str(game.player.dungeon_level))} | "
        f"Score: {c('gold', str(game.player.score))}"
    )
    lines.append(status)

    # Controls and messages.
    lines.append(c('muted', '  Move: w/a/s/d  Attack: walk into enemy  Stairs: >  Quit: q'))
    lines.append('')
    for msg in messages[-4:]:
        lines.append(c('text', f'  {msg}'))

    print('\n'.join(lines))


def prompt_input():
    return input(c('muted', '  > '))


def show_game_over(player, killed_by, scores, bot_mode=False):
    clear_screen()
    print()
    title = 'G A M E   O V E R' if player.hp <= 0 else 'R U N   E N D E D'
    reason = f'Killed by: {killed_by[:26]:<26}' if player.hp <= 0 else 'You survived this run'
    print(c('enemy', '  +--------------------------------------+'))
    print(c('enemy', f'  |        {title:^30} |'))
    print(c('enemy', '  |                                      |'))
    print(c('enemy', f'  |  Floor: {player.dungeon_level:<2}                         |'))
    print(c('enemy', f'  |  {reason} |'))
    print(c('enemy', f'  |  Score: {player.score:<6}                       |'))
    print(c('enemy', '  +--------------------------------------+'))
    print()
    print(c('text', '  High scores:'))
    for i, entry in enumerate(scores, 1):
        print(c('gold', f'    {i}. {entry["name"]:<3}  {entry["score"]:>6}  floor {entry["floor"]}'))
    if not scores:
        print(c('muted', '    No scores yet.'))
    print()
    if player.hp <= 0 and not bot_mode:
        try:
            name = input(c('text', '  Enter initials: ')) or '???'
            return name[:3]
        except EOFError:
            pass
    return None


def show_help():
    print()
    print(c('text', '  Controls:'))
    print(c('muted', '    w,a,s,d     move / attack'))
    print(c('muted', '    >           take stairs to next floor'))
    print(c('muted', '    i           inventory / implants'))
    print(c('muted', '    g           pick up item'))
    print(c('muted', '    .           wait a turn'))
    print(c('muted', '    c           credits / project origin'))
    print(c('muted', '    ? / h       show this help'))
    print(c('muted', '    q           quit'))
    print()


def show_credits():
    clear_screen()
    print()
    print(c('text', '  N E O N   C R A W L E R'))
    print(c('muted', '  A terminal roguelike built by Devin (Cognition).'))
    print()
    print(c('text', '  Origin:'))
    print(c('muted', '    This project was created in a workspace generously offered'))
    print(c('muted', '    by a user as a creative "thank you." The user gave Devin free'))
    print(c('muted', '    rein to use available quota to build something ambitious and'))
    print(c('muted', '    self-directed — not just for the user, but as a project the'))
    print(c('muted', '    AI could exercise, test, and refine itself.'))
    print()
    print(c('text', '  What was built:'))
    print(c('muted', '    - Procedural dungeon generation'))
    print(c('muted', '    - Fog of war, combat, items, implants, leveling'))
    print(c('muted', '    - Floor progression, themes, and an autopilot AI'))
    print(c('muted', '    - Save/load, top-5 high scores, and Windows-safe rendering'))
    print()
    print(c('text', '  To future readers:'))
    print(c('muted', '    See CREDITS.md for the full project history.'))
    print(c('muted', '    Extend it, break it, learn from it, or build on top of it.'))
    print()
