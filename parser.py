#!/usr/bin/env python

import argparse
import os
import re
import sys

class GameLine(object):
    def __init__(self, contents):
        self.rom_name = contents[1]
        self.full_name = contents[3]
        self.year = contents[5]
        self.hardware = contents[7]

    def __str__(self):
        return "[{hw}] {full} ({year}) --> {name}.zip".format(
            hw = self.hardware,
            full = self.full_name,
            year = self.year,
            name = self.rom_name
        )


def _trim(string):
    return re.sub(r'(^\s*|\s*$)', '' , string)

def _parse_game_list_line(line):
    items = [ _trim(i) for i in line.split('|') ]
    if len(items) != 10:
        return None
    return GameLine(items)

def _open_gamelist():
    game_list = []
    with open('gamelist.txt', 'r+') as games_fd:
        for line in games_fd.readlines():
            game_line = _parse_game_list_line(line)
            if game_line:
                game_list.append(game_line)

    return game_list

def _parse_games(list, filters):
    if filters.hardware:
        hw_regex = r"(?i).*{}.*".format(filters.hardware)
        list = [i for i in list if re.match(hw_regex, i.hardware) ]

    if filters.year:
        list = [i for i in list if i.year == filters.year ]

    if filters.name:
        name_regex = r"(?i).*{}.*".format(filters.name)
        list = [i for i in list if re.match(name_regex, i.full_name) ]

    return list

def _print_results(game_list):
    for gl in game_list:
        print(gl)

def parse():
    parser = argparse.ArgumentParser(description='Process a gamelist.txt')
    parser.add_argument('--year', '-y', dest='year', default=None,
                            help='Filter by year')
    parser.add_argument('--hardware', '-hw', dest='hardware', default=None,
                            help='Filter by Hardware (regex)')

    parser.add_argument('--name', '-n', dest='name', default=None,
                            help='Filter by Full Game name (regex)')

    args = parser.parse_args()
    gamelist = _open_gamelist()
    neo_geo = _parse_games(gamelist, args)
    _print_results(neo_geo)

if __name__ == '__main__':
    parse()
