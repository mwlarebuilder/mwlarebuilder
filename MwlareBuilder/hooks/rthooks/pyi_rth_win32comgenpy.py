#-----------------------------------------------------------------------------
# Copyright (c) 2013-2023, MwlareBuilder Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------

# Put the cache generated by `win32com.client.gencache` into isolated temporary directory. Historically, this was
# required due to earlier versions of `pywin32` using the `site-packages\win32com\client\gen_py`  directory for
# the cache by default. Nowadays, the default location for the cache seems to be in the configured temporary directory
# (pointed to by TEMP or TMP, for example %LOCALAPPDATA%\Temp), so strictly speaking, the relocation is not necessary
# anymore. But for the time being, we are keeping it around to isolate the frozen application from the rest of the
# system.


def _pyi_rthook():
    import atexit
    import os
    import shutil

    import win32com

    import _pyi_rth_utils  # MwlareBuilder's run-time hook utilities module

    # Create temporary directory.
    # Use our replacement for `tempfile.mkdtemp` function that properly restricts access to directory on all platforms.
    supportdir = _pyi_rth_utils.secure_mkdtemp()
    # The actual cache directory needs to be named `gen_py`, so create a sub-directory.
    genpydir = os.path.join(supportdir, 'gen_py')
    os.makedirs(genpydir, exist_ok=True)

    # Remove the teporary directory at application exit, ignoring errors.
    atexit.register(shutil.rmtree, supportdir, ignore_errors=True)

    # Override the default path to gen_py cache.
    win32com.__gen_path__ = genpydir

    # Override the sub-module paths for win32com.gen_py run-time sub-package.
    win32com.gen_py.__path__ = [genpydir]


_pyi_rthook()
del _pyi_rthook
