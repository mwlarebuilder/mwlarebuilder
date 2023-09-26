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
Show dll dependencies of executable files or other dynamic libraries.
"""

import argparse
import glob

import MwlareBuilder.depend.bindepend
import MwlareBuilder.log


def run():
    parser = argparse.ArgumentParser()
    MwlareBuilder.log.__add_options(parser)
    parser.add_argument(
        'filenames',
        nargs='+',
        metavar='executable-or-dynamic-library',
        help="executables or dynamic libraries for which the dependencies should be shown",
    )

    args = parser.parse_args()
    MwlareBuilder.log.__process_options(parser, args)

    # Suppress all informative messages from the dependency code.
    MwlareBuilder.log.getLogger('MwlareBuilder.build.bindepend').setLevel(MwlareBuilder.log.WARN)

    try:
        for input_filename_or_pattern in args.filenames:
            for filename in glob.glob(input_filename_or_pattern):
                print(f"{filename}:")
                for lib_name, lib_path in sorted(MwlareBuilder.depend.bindepend.get_imports(filename)):
                    print(f"  {lib_name} => {lib_path}")
                print("")
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()
