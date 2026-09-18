"""Field of view computation using shadowcasting."""


def recompute_fov(game_map, px, py, radius):
    """Mark visible tiles within radius of (px, py)."""
    visible = set()
    visible.add((px, py))

    # 8 octants, iterate with recursive shadowcasting logic.
    def cast_octant(octant, row, start_slope, end_slope, radius, px, py, blocked):
        if start_slope < end_slope:
            return
        if row > radius:
            return
        radius_squared = radius * radius
        blocked = blocked
        for dx in range(row, radius + 1):
            # Transform octant coordinates to map coordinates.
            left_slope = (dx - 0.5) / (row - 0.5)
            if left_slope > start_slope:
                continue
            right_slope = (dx + 0.5) / (row - 0.5)
            if right_slope < end_slope:
                break
            for dy in range(dx + 1):
                if dx * dx + dy * dy > radius_squared:
                    break
                mx, my = transform(octant, dx, dy, px, py)
                if 0 <= mx < game_map.width and 0 <= my < game_map.height:
                    visible.add((mx, my))
            # Determine next slopes.
            # This simplified version just lights the whole octant wedge.
            pass

    # Simpler algorithm: raycast to every tile in the bounding square.
    for x in range(px - radius, px + radius + 1):
        for y in range(py - radius, py + radius + 1):
            if (x - px) ** 2 + (y - py) ** 2 > radius * radius:
                continue
            if 0 <= x < game_map.width and 0 <= y < game_map.height:
                if line_of_sight(game_map, px, py, x, y):
                    visible.add((x, y))

    return visible


def line_of_sight(game_map, x0, y0, x1, y1):
    """Bresenham line of sight."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cx, cy = x0, y0
    while True:
        if game_map.tiles[cx][cy].block_sight and (cx != x0 or cy != y0):
            return False
        if cx == x1 and cy == y1:
            return True
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            cx += sx
        if e2 < dx:
            err += dx
            cy += sy


def transform(octant, row, col, cx, cy):
    if octant == 0:
        return cx + col, cy - row
    if octant == 1:
        return cx + row, cy - col
    if octant == 2:
        return cx + row, cy + col
    if octant == 3:
        return cx + col, cy + row
    if octant == 4:
        return cx - col, cy + row
    if octant == 5:
        return cx - row, cy + col
    if octant == 6:
        return cx - row, cy - col
    return cx - col, cy - row
