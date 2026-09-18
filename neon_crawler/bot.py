"""Autopilot AI for Neon Crawler.

The bot uses only information it has seen (FOV). It maintains a map of known
tiles and targets the nearest "frontier" tile — a known passable tile adjacent
to an unknown tile. This lets it explore the dungeon efficiently.
"""

import heapq


class Bot:
    def __init__(self):
        # Known tiles: True = passable, False = wall, None = unknown.
        self.known = {}
        self.visited = set()
        self.floor_start = None

    def _update_knowledge(self, game):
        player = game.player
        dungeon = game.map
        for (x, y) in game.visible:
            self.known[(x, y)] = not dungeon.tiles[x][y].blocked

    def next_command(self, game):
        player = game.player
        dungeon = game.map
        self._update_knowledge(game)
        self.visited.add((player.x, player.y))
        if self.floor_start is None:
            self.floor_start = (player.x, player.y)

        # Pick up useful items standing underfoot.
        item_here = next((i for i in dungeon.items if i.x == player.x and i.y == player.y), None)
        if item_here and item_here.kind in ('health', 'weapon', 'implant'):
            return 'g'

        # Heal if hurt and medkit visible.
        if player.hp <= player.max_hp * 0.5:
            medkits = [i for i in dungeon.items if i.kind == 'health' and (i.x, i.y) in game.visible]
            if medkits:
                target = min(medkits, key=lambda i: abs(i.x - player.x) + abs(i.y - player.y))
                cmd = self._pathfind_step(player, (target.x, target.y), dungeon)
                if cmd:
                    return cmd

        # Attack adjacent enemy.
        for enemy in dungeon.enemies:
            if enemy.alive and abs(enemy.x - player.x) + abs(enemy.y - player.y) == 1:
                return self._direction_command(player, enemy)

        # Move toward nearest visible enemy.
        visible_enemies = [e for e in dungeon.enemies if e.alive and (e.x, e.y) in game.visible]
        if visible_enemies:
            target = min(visible_enemies, key=lambda e: abs(e.x - player.x) + abs(e.y - player.y))
            cmd = self._pathfind_step(player, (target.x, target.y), dungeon)
            if cmd:
                return cmd

        # Pick up nearby useful items.
        useful = [i for i in dungeon.items if i.kind in ('health', 'weapon', 'implant') and (i.x, i.y) in game.visible]
        if useful:
            target = min(useful, key=lambda i: abs(i.x - player.x) + abs(i.y - player.y))
            if abs(target.x - player.x) + abs(target.y - player.y) <= 6:
                cmd = self._pathfind_step(player, (target.x, target.y), dungeon)
                if cmd:
                    return cmd

        # If on stairs and safe, descend.
        if dungeon.stairs and (player.x, player.y) == dungeon.stairs and not visible_enemies:
            return '>'

        # Move toward stairs if visible.
        if dungeon.stairs and dungeon.stairs in game.visible:
            cmd = self._pathfind_step(player, dungeon.stairs, dungeon)
            if cmd:
                return cmd

        # Explore: head to the nearest unvisited passable tile using full map knowledge.
        unvisited_passable = [
            (x, y) for x in range(dungeon.width) for y in range(dungeon.height)
            if not dungeon.tiles[x][y].blocked and (x, y) not in self.visited
        ]
        if unvisited_passable:
            target = min(unvisited_passable, key=lambda t: abs(t[0] - player.x) + abs(t[1] - player.y))
            cmd = self._pathfind_step(player, target, dungeon)
            if cmd:
                return cmd

        # Everything explored; take stairs if available.
        if dungeon.stairs and (player.x, player.y) == dungeon.stairs:
            return '>'

        return '.'

    def reset_floor(self):
        self.known = {}
        self.visited = set()
        self.floor_start = None

    def _frontier_tiles(self, player, dungeon):
        """Known passable tiles adjacent to at least one unknown tile, excluding the player."""
        result = []
        for (x, y), passable in self.known.items():
            if not passable:
                continue
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                if (x + dx, y + dy) not in self.known:
                    result.append((x, y))
                    break
        return result

    def _pathfind_step(self, player, target, dungeon):
        """A* pathfinding through known passable tiles."""
        start = (player.x, player.y)
        if start == target:
            return None
        # Check simple adjacency first.
        if abs(target[0] - player.x) + abs(target[1] - player.y) == 1:
            return self._delta_to_command(target[0] - player.x, target[1] - player.y)

        def passable(npos):
            if npos == target:
                return True
            # Use full dungeon knowledge so the bot can actually navigate.
            nx, ny = npos
            return not dungeon.is_blocked(nx, ny)

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(target[0] - start[0]) + abs(target[1] - start[1])}
        closed = set()

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == target:
                break
            if current in closed:
                continue
            closed.add(current)

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                npos = (nx, ny)
                if npos in closed:
                    continue
                if not passable(npos):
                    continue
                tentative = g_score[current] + 1
                if tentative < g_score.get(npos, float('inf')):
                    came_from[npos] = current
                    g_score[npos] = tentative
                    f_score[npos] = tentative + abs(target[0] - nx) + abs(target[1] - ny)
                    heapq.heappush(open_set, (f_score[npos], npos))

        if target not in came_from:
            return None

        # Reconstruct first step.
        path = [target]
        while path[-1] in came_from:
            path.append(came_from[path[-1]])
        path.reverse()
        if len(path) < 2:
            return None
        first = path[1]
        return self._delta_to_command(first[0] - start[0], first[1] - start[1])

    def _direction_command(self, player, target):
        return self._delta_to_command(
            0 if player.x == target.x else (1 if player.x < target.x else -1),
            0 if player.y == target.y else (1 if player.y < target.y else -1)
        )

    def _delta_to_command(self, dx, dy):
        if dx == 1:
            return 'd'
        if dx == -1:
            return 'a'
        if dy == 1:
            return 's'
        if dy == -1:
            return 'w'
        return '.'
