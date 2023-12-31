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

# This file is part of the package for testing eggs in `MwlareBuilder`.

from setuptools import setup

setup(
    name='unzipped_egg',
    version='0.1',
    description='A unzipped egg for testing MwlareBuilder',
    packages=['unzipped_egg'],
    package_data={'unzipped_egg': ['data/datafile.txt']},
    zip_safe=False,
)
