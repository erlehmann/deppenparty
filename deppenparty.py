#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Deppenparty
# ⓒ 2013  Nils Dagsson Moskopp

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Dieses Programm hat das Ziel, die Medienkompetenz der Leser zu
# steigern. Gelegentlich packe ich sogar einen handfesten Buffer
# Overflow oder eine Format String Vulnerability zwischen die anderen
# Codezeilen und schreibe das auch nicht dran.

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

import pygame

FRAMERATE = 60

BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
WHITE = (255, 255, 255)
BACKGROUND = (63, 72, 204)
FOREGROUND = (255, 201, 14)

STATE_BOARD, STATE_ANSWER, STATE_QUESTION = range(3)

class Player(object):
    def __init__(self, name):
        self.name = name
        self.points = 0

class Game(object):
    def __init__(self, filename, name1, name2):
        self.players = (Player(name1), Player(name2))

        with open(filename) as f:
            # parse by column <http://stackoverflow.com/questions/11059390/parsing-a-tab-separated-file-in-python#answer-11059449>
            board = zip(*(line.strip().split('\t') for line in f))
        logging.debug(board)
        self.categories = [
            {
                'name': line[0].decode('utf-8'),
                'content': [
                    {
                        'answer': (
                            token.split('|')[0].split(':')[0],
                            token.split('|')[0].split(':')[1].decode('utf-8')
                            ),
                        'question': (
                            token.split('|')[1].split(':')[0],
                            token.split('|')[1].split(':')[1].decode('utf-8')
                            ),
                        'active': True,
                        'points': int(board[0][i+1])
                        } for i, token in enumerate(line[1:])
                    ]
                } for line in board[1:]
            ]
        logging.debug(self.categories)

        pygame.init()
        pygame.display.set_caption('Deppenparty!')

        self.size = self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode(self.size)
        self.font = pygame.font.SysFont('sans', 32)
        self.clock = pygame.time.Clock()
        self.state = STATE_BOARD
        self.cursor = [0,0]

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if self.state == STATE_BOARD:
                if event.key == pygame.K_LEFT:
                    if self.cursor[0] > 0:
                        self.cursor[0] -= 1
                elif event.key == pygame.K_RIGHT:
                    if self.cursor[0] < len(self.categories) - 1:
                        self.cursor[0] += 1
                elif event.key == pygame.K_UP:
                    if self.cursor[1] > 0:
                        self.cursor[1] -= 1
                elif event.key == pygame.K_DOWN:
                    if self.cursor[1] < \
                            len(self.categories[0]['content']) - 1:
                        self.cursor[1] += 1
            elif self.state == STATE_ANSWER:
                raise NotImplementedError
            elif self.state == STATE_QUESTION:
                raise NotImplementedError

    def render(self):
        if self.state == STATE_BOARD:
            self.render_board()
        elif self.state == STATE_ANSWER:
            self.render_answer()
        elif self.state == STATE_QUESTION:
            self.render_question()

    def render_answer(self):
        raise NotImplementedError

    def render_board(self):
        self.screen.fill(GRAY)

        margin = 20
        offset = 5 * margin
        col_count = len(self.categories)
        col_width = (self.width - ((3 + col_count) * margin)) / col_count
        logging.debug('%s columns, width %s.' % (col_count, col_width))
        row_count = len(self.categories[0]['content']) + 1
        row_height = (self.height - offset - ((5 + row_count) * margin)) / row_count
        logging.debug('%s rows, height %s.' % (row_count, row_height))
        self.font = pygame.font.SysFont('sans', row_height / 2)

        # draw background rectangles
        pygame.draw.rect(
            self.screen, BLACK, (
                margin,
                margin,
                (col_width + margin) * col_count + margin,
                row_height + 2 * margin
                ),
            0)
        pygame.draw.rect(
            self.screen, BLACK, (
                margin,
                row_height + 4 * margin,
                (col_width + margin) * col_count + margin,
                (row_height + margin) * (row_count - 1) + margin
                ),
            0)
        pygame.draw.rect(
            self.screen, BLACK, (
                margin,
                (row_height + margin) * (row_count) + 5 * margin,
                (col_width + margin) * col_count + margin,
                row_height + 2 * margin
                ),
            0)

        for i in range(col_count):
            # draw category tiles
            x, y = (2 * margin) + i * (col_width + margin), 2 * margin
            pygame.draw.rect(self.screen, BACKGROUND, \
                                 (x, y, col_width, row_height), 0)
            self.render_text(self.categories[i]['name'], x, y)
            y += 2 * margin
            # draw answer tiles
            for j in range(row_count - 1):
                y += margin + row_height
                if i == self.cursor[0] and j == self.cursor[1]:
                    pygame.draw.rect(self.screen, WHITE,
                        (x-margin/2, y-margin/2, \
                             col_width+margin, row_height+margin), 0)
                pygame.draw.rect(self.screen, BACKGROUND, \
                    (x, y, col_width, row_height), 0)
                self.render_text(
                    str(self.categories[i]['content'][j]['points']), x, y)

        player_count = len(self.players)
        player_width = (self.width - ((3 + player_count) * margin)) / \
            player_count
        for i, player in enumerate(self.players):
            # draw player tiles
            x = (2 * margin) + i * (player_width + margin)
            y = (row_height + margin) * (row_count) + 6 * margin
            pygame.draw.rect(self.screen, BACKGROUND, \
                                 (x, y, player_width, row_height), 0)
            self.render_text('%s: %s' % (player.name, player.points), x, y)

    def render_question(self):
        raise NotImplementedError

    def render_text(self, text, x, y):
        surface = self.font.render(text, 1, FOREGROUND)
        self.screen.blit(
            surface, (
                x + (surface.get_height() / 2),
                y + (surface.get_height() / 2)
                )
            )

    def run(self):
        logging.debug('Game started.')
        self.dirty = True
        self.running = True
        while self.running:
            self.clock.tick(FRAMERATE)
            if self.dirty:
                self.render()
                pygame.display.flip()
                self.dirty = False
            for event in pygame.event.get():
                self.handle_event(event)
                self.dirty = True
        logging.debug('Game quit')

if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Clone of the game “Jeopardy!” for two players.')
    parser.add_argument('--file', dest='filename', \
        help='A TSV file describing the board.', default='deppenparty.tsv')
    parser.add_argument('--name1', dest='name1', \
        help='Name of first player.', default='Buffy')
    parser.add_argument('--name2', dest='name2', \
        help='Name of second player.', default='Spike')
    args = parser.parse_args()
    logging.debug(args)

    game = Game(args.filename, args.name1, args.name2)
    game.run()
