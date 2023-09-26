#-----------------------------------------------------------------------------
# Copyright (c) 2005-2023, MwlareBuilder Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

from MwlareBuilder.utils.hooks.gi import GiModuleInfo

module_info = GiModuleInfo('GModule', '2.0')
if module_info.available:
    binaries, datas, hiddenimports = module_info.collect_typelib_data()
