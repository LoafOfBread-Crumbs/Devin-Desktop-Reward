"""Player state and progression."""


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '@'
        self.max_hp = 30
        self.hp = 30
        self.base_atk = 4
        self.atk_bonus = 0
        self.xp = 0
        self.level = 1
        self.xp_to_next = 20
        self.weapon_name = 'Fist'
        self.dungeon_level = 1
        self.score = 0

    @property
    def atk(self):
        return self.base_atk + self.atk_bonus

    @property
    def xp_needed(self):
        return self.xp_to_next - self.xp

    def level_up(self):
        self.level += 1
        self.max_hp += 5
        self.hp = self.max_hp
        self.base_atk += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5) + 10
        return self.level

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def add_xp(self, amount):
        self.xp += amount
        self.score += amount
        if self.xp >= self.xp_to_next:
            return self.level_up()
        return None
