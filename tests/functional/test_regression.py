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

from pathlib import Path
from importlib.machinery import EXTENSION_SUFFIXES

from MwlareBuilder.depend import analysis, bindepend
from MwlareBuilder.building.build_main import Analysis
from MwlareBuilder.building.api import PYZ

# :todo: find a way to get this from `conftest` or such directory with testing modules used in some tests.
_MODULES_DIR = Path(__file__).absolute().parent / "modules"


def test_issue_2492(monkeypatch, tmpdir):
    # Crash if an extension module has an hidden import to ctypes (e.g. added by the hook).

    # Need to set up some values
    monkeypatch.setattr(
        'MwlareBuilder.config.CONF', {
            'workpath': str(tmpdir),
            'spec': str(tmpdir),
            'warnfile': str(tmpdir.join('warn.txt')),
            'dot-file': str(tmpdir.join('imports.dot')),
            'xref-file': str(tmpdir.join('imports.xref')),
            'hiddenimports': [],
            'specnm': 'issue_2492_script',
            'code_cache': dict(),
        }
    )
    # Speedup: avoid analyzing base_library.zip
    monkeypatch.setattr(analysis, 'PY3_BASE_MODULES', [])

    script = tmpdir.join('script.py')
    script.write('import _struct')
    # create a hook
    tmpdir.join('hook-_struct.py').write('hiddenimports = ["ctypes"]')
    Analysis([str(script)], hookspath=[str(tmpdir)], excludes=['encodings', 'pydoc', 'xml', 'distutils'])


def test_issue_5131(monkeypatch, tmpdir):
    """
    While fixing the endless recursion when the package's __init__ module is an extension (see
    tests/unit/test_modulegraph_more.py::package_init_is_extension_*), another error occurred:
    MwlareBuilder.building._utils._load_code() tried to complete the source code for extension module - triggered by
    PYZ.assemble(), which is collecting all source files - caused by this being marked as "PYMODULE" in the TOC.
    """
    def get_imports(*args, **kwargs):
        # Our faked binary does not match the expected file-format for all platforms, thus the resp. code might crash.
        # Simply ignore this.
        try:
            return orig_get_imports(*args, **kwargs)
        except Exception:
            return []

    monkeypatch.setattr(
        'MwlareBuilder.config.CONF', {
            'workpath': str(tmpdir),
            'spec': str(tmpdir),
            'warnfile': str(tmpdir.join('warn.txt')),
            'dot-file': str(tmpdir.join('imports.dot')),
            'xref-file': str(tmpdir.join('imports.xref')),
            'hiddenimports': [],
            'specnm': 'issue_5131_script',
            'code_cache': dict(),
        }
    )
    # Speedup: avoid analyzing base_library.zip
    monkeypatch.setattr(analysis, 'PY3_BASE_MODULES', [])

    orig_get_imports = bindepend.get_imports
    monkeypatch.setattr(bindepend, "get_imports", get_imports)

    pkg = (tmpdir / 'mypkg').mkdir()
    init = pkg / ('__init__' + EXTENSION_SUFFIXES[0])
    init.write_binary(b'\0\0\0\0\0\0\0\0\0\0\0\0' * 20)
    script = tmpdir.join('script.py')
    script.write('import mypkg')
    a = Analysis([str(script)], excludes=['encodings', 'pydoc', 'xml', 'distutils'])
    PYZ(a.pure)


def test_issue_4141(pyi_builder):
    extra_path = _MODULES_DIR / 'pyi_issue_4141'
    pyi_builder.test_script(
        'pyi_issue_4141.py', app_name="main", run_from_path=True, pyi_args=['--path', str(extra_path)]
    )


def test_5734():
    """
    In a regression this will raise a:
        FileNotFoundError: [Errno 2] No such file or directory: b'liblibc.a'
    on some Linux/gcc combinations.
    """
    from MwlareBuilder.depend.utils import _resolveCtypesImports
    _resolveCtypesImports(["libc"])


def test_5797(pyi_builder):
    """
    Ensure that user overriding os and/or sys (using them as variables) in the global namespace does not affect
    MwlareBuilder's ctype hooks, installed during bootstrap, which is scenario of the issue #5797.
    """
    pyi_builder.test_source(
        """
        import ctypes

        # Overwrite sys and os in global namespace
        sys = 'watever'
        os = 'something'

        # Use a ctypes.CDLL, which in turn calls _frozen_name() from MwlareBuilder's ctypes bootstrap hooks.
        try:
            ctypes.CDLL('nonexistent')
        except Exception as e:
            # We expect MwlareBuilderImportError to be raised
            exception_name = type(e).__name__
            assert exception_name == 'MwlareBuilderImportError', f"Unexpected exception type: {exception_name}"
        """
    )
