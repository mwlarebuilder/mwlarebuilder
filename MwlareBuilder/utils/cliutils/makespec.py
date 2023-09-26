#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, MwlareBuilder Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------
"""
Automatically build a spec file containing the description of the project.
"""

import argparse
import os

import MwlareBuilder.building.makespec
import MwlareBuilder.log


def generate_parser():
    p = argparse.ArgumentParser()
    MwlareBuilder.building.makespec.__add_options(p)
    MwlareBuilder.log.__add_options(p)
    p.add_argument(
        'scriptname',
        nargs='+',
    )
    return p


def run():
    p = generate_parser()
    args = p.parse_args()
    MwlareBuilder.log.__process_options(p, args)

    # Split pathex by using the path separator.
    temppaths = args.pathex[:]
    args.pathex = []
    for p in temppaths:
        args.pathex.extend(p.split(os.pathsep))

    try:
        name = MwlareBuilder.building.makespec.main(args.scriptname, **vars(args))
        print('Wrote %s.' % name)
        print('Now run mwlarebuilder.py to build the executable.')
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
