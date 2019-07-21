#!/usr/bin/env python

"""parser

Reads a FBA romset list and alllows basic querying over its data

"""

import argparse
import json
import logging
import logging.handlers
import os
import re
import sys

logger = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def _parse_args():
    """Reads input parameters"""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)

    parser.add_argument('--gamelist', '-g', dest='gamelist_file',
                        default='gamelist.txt',
                        help='The path to the FBA gamelist to parse')

    g = parser.add_argument_group("querying parameters")
    g.add_argument('--year', '-y', dest='year', default=None,
                   help='Filter by year')
    g.add_argument('--hardware', '-hw', dest='hardware', default=None,
                   help='Filter by Hardware (regex)')
    g.add_argument('--name', '-n', dest='name', default=None,
                   help='Filter by Full Game name (regex)')

    g = parser.add_mutually_exclusive_group()
    g.add_argument("--debug", "-d", action="store_true",
               default=False,
               help="enable debugging")
    g.add_argument("--silent", "-s", action="store_true",
               default=False,
               help="don't log to console")

    parser.add_argument('--format',  dest='format', default='string',
                   choices=['string', 'json'], help='Choose output format')

    return parser.parse_args()

def _setup_logging(options):
    """Configure logging."""
    root = logging.getLogger("")
    root.setLevel(logging.WARNING)
    logger.setLevel(options.debug and logging.DEBUG or logging.INFO)
    if options.silent:
        return

    if not sys.stderr.isatty(): #For example, when running from a cron job
        facility = logging.handlers.SysLogHandler.LOG_DAEMON
        sh = logging.handlers.SysLogHandler(address='/dev/log',
                                            facility=facility)
        sh.setFormatter(logging.Formatter(
            "{0}[{1}]: %(message)s".format(
                logger.name,
                os.getpid())))
        root.addHandler(sh)
    else:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            "%(levelname)s[%(name)s] %(message)s"))
        root.addHandler(ch)


class GameLine(object):
    """Represents a queryable item, read off the gamelist"""
    def __init__(self, contents):
        self.rom_name = contents[1]
        self.full_name = contents[3]
        self.year = contents[5]
        self.hardware = contents[7]

    def __str__(self):
        return "[{hardware}] {full_name} ({year}) --> {rom_name}.zip".format(**self.as_dict())

    def as_dict(self):
        return dict(
            hardware = self.hardware,
            full_name = self.full_name,
            year = self.year,
            rom_name = self.rom_name
        )

def _trim(string):
    return re.sub(r'(^\s*|\s*$)', '' , string)

def _parse_game_list_line(line):
    items = [ _trim(i) for i in line.split('|') ]
    if len(items) != 10:
        return None
    return GameLine(items)

def _open_gamelist(gamelist_file):
    if not os.path.isfile(gamelist_file):
        logger.error("Gamelist file '{}' does not exit".format(gamelist_file))
        sys.exit(1)

    game_list = []
    with open(gamelist_file, 'r+') as games_fd:
        for line in games_fd.readlines():
            game_line = _parse_game_list_line(line)
            if game_line:
                game_list.append(game_line)

    return game_list

def __get_regex_for(string):
    return r"(?i).*{}.*".format(string)

def _parse_games(list, filters):
    if filters.hardware:
        list = [i for i in list if re.match(__get_regex_for(filters.hardware), i.hardware) ]

    if filters.year:
        list = [i for i in list if i.year == filters.year ]

    if filters.name:
        list = [i for i in list if re.match(__get_regex_for(filters.name), i.full_name) ]

    return list

def _print_results(game_list, format='string'):
    if format == 'string':
        for gl in game_list:
            print(gl)
    elif format == 'json':
        items = [ gl.as_dict() for gl in game_list]
        print(json.dumps(items))

def parse():
    options = _parse_args()
    _setup_logging(options)

    gamelist = _open_gamelist(options.gamelist_file)
    filtered_results = _parse_games(gamelist, options)
    _print_results(filtered_results, options.format)

if __name__ == '__main__':
    parse()
