"""Smoke test: run a few game ticks with scripted input."""

import builtins
from neon_crawler.game import Game, save_game, load_game, delete_save


def test_scripted():
    inputs = iter(['', 'd', 'd', 's', 's', 'a', 'w', 'g', '>', 'q'])

    original_input = builtins.input
    builtins.input = lambda *args: next(inputs)

    try:
        game = Game()
        for cmd in ['d', 'd', 's', 's', 'a', 'w', '.', 'g', '?', 'q']:
            if game.player.hp <= 0:
                break
            game.handle_input(cmd)
            game.recompute_fov()
        print('Smoke test passed. Final score:', game.player.score)
    finally:
        builtins.input = original_input


def test_save_load():
    game = Game()
    game.player.score = 42
    game.player.hp = 25
    save_game(game)
    loaded = load_game()
    delete_save()
    assert loaded.player.score == 42
    assert loaded.player.hp == 25
    print('Save/load test passed.')


if __name__ == '__main__':
    test_scripted()
    test_save_load()
