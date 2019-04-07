#!/usr/bin/env python

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

def _parse_games(list, hardware):
    if not hardware:
        return list

    hw_regex = r"(?i).*{}.*".format(hardware)
    return [i for i in list if re.match(hw_regex, i.hardware) ]

def _print_results(game_list):
    for gl in game_list:
        print(gl)

def parse(arguments):
    hardware = None
    if (len(arguments) > 0): hardware = arguments[0]

    gamelist = _open_gamelist()
    neo_geo = _parse_games(gamelist, hardware)
    _print_results(neo_geo)

if __name__ == '__main__':
    parse(sys.argv[1:])
