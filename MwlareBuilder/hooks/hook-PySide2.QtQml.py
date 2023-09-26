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

from MwlareBuilder.utils.hooks.qt import add_qt5_dependencies, pyside2_library_info

hiddenimports, binaries, datas = add_qt5_dependencies(__file__)
qml_binaries, qml_datas = pyside2_library_info.collect_qtqml_files()
binaries += qml_binaries
datas += qml_datas

hiddenimports += ["PySide2.QtGui"]