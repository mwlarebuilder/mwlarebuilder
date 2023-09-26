#-----------------------------------------------------------------------------
# Copyright (c) 2021-2023, MwlareBuilder Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from MwlareBuilder.utils.hooks.qt import add_qt5_dependencies

hiddenimports, binaries, datas = add_qt5_dependencies(__file__)
hiddenimports += ['PySide2.QtXml']  # Not inferred from dynamic lib analysis