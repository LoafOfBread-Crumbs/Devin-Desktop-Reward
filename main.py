#!/usr/bin/env python3
"""Entry point for Neon Crawler.

Neon Crawler is a turn-based cyberpunk roguelike built by Devin (Cognition)
as a self-directed creative project. It was created after the user offered
their workspace quota as a "thank you" and asked Devin to build something
ambitious and enjoyable.

For the full project origin and a message to future readers, see CREDITS.md
or press 'c' in-game.
"""

import argparse
import random
import time

from neon_crawler.game import Game


def main():
    parser = argparse.ArgumentParser(description='Neon Crawler - terminal roguelike')
    parser.add_argument('--bot', action='store_true', help='Run an AI autopilot (spectator mode)')
    parser.add_argument('--silent', action='store_true', help='Bot mode: suppress animation, show final state')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for deterministic runs')
    parser.add_argument('--delay', type=float, default=0.05, help='Delay between bot turns in seconds')
    parser.add_argument('--snapshot', type=int, default=0, help='Print a snapshot every N turns in bot mode')
    parser.add_argument('--max-turns', type=int, default=0, help='Stop bot after N turns (0 = unlimited)')
    parser.add_argument('--continue', dest='continue_game', action='store_true', help='Continue a saved game')
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print('\n  N E O N   C R A W L E R')
    print('  procedural terminal roguelike')
    print("  press '?' in-game for controls\n")

    if not args.bot:
        input('  Press Enter to descend...')

    game = Game(continue_saved=args.continue_game)

    if args.bot:
        game.run_bot(args.delay, silent=args.silent, snapshot_every=args.snapshot, max_turns=args.max_turns)
    else:
        game.run()


if __name__ == '__main__':
    main()
