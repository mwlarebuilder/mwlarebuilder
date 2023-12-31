===============================
Hook Configuration Options
===============================

As of version 4.4, MwlareBuilder implements a mechanism for passing
configuration options to the hooks. At the time of writing, this
feature is supported only in :ref:`.spec files <using spec files>` and
has no command-line interface equivalent.

The hook configuration options consist of a dictionary that is passed
to the ``Analysis`` object via the ``hooksconfig`` argument. The keys
of the dictionary represent `hook identifiers` while the values are
dictionaries of hook-specific keys and values that correspond to
hook settings:


.. code-block:: python

    a = Analysis(
        ["program.py"],
        ...,
        hooksconfig={
            "some_hook_id": {
                "foo": ["entry1", "entry2"],
                "bar": 42,
                "enable_x": True,
            },
            "another_hook_id": {
                "baz": "value",
            },
        },
        ...,
    )


.. _supported hooks and options:

Supported hooks and options
===========================

This section lists hooks that implement support for configuration
options. For each hook (or group of hooks), we provide the `hook
identifier` and the list of supported options.

GObject introspection (gi) hooks
--------------------------------

The options passed under `gi` hook identifier control the collection
of GLib/Gtk resources (themes, icons, translations) in various
hooks related to ``GObject introspection`` (i.e., ``hook-gi.*``).

They are especially useful when freezing ``Gtk3``-based applications on
linux, as they allow one to limit the amount of themes and icons collected
from the system ``/usr/share`` directory.

**Hook identifier:** ``gi``

**Options**

 * ``languages`` [*list of strings*]: list of locales (e.g., ˙en_US˙) for
   which translations should be collected. By default, ``gi`` hooks
   collect all available translations.

 * ``icons`` [*list of strings*]: list of icon themes (e.g., `Adwaita`)
   that should be collected. By default, ``gi`` hooks collect all available
   icon themes.

 * ``themes`` [*list of strings*]: list of Gtk themes (e.g., `Adwaita`)
   that should be collected. By default, ``gi`` hooks collect all available
   icon themes.

 * ``module-versions`` [*dict of version strings*]: versions of gi modules to
   use. For example, a key of 'GtkSource' and value to '4' will use
   gtksourceview4.

**Example**

Collect only ``Adwaita`` theme and icons, limit the collected
translations to British English and Simplified Chinese, and use
version 3.0 of Gtk and version 4 of GtkSource:

.. code-block:: python

    a = Analysis(
        ["my-gtk-app.py"],
        ...,
        hooksconfig={
            "gi": {
                "icons": ["Adwaita"],
                "themes": ["Adwaita"],
                "languages": ["en_GB", "zh_CN"],
                "module-versions": {
                    "Gtk": "3.0",
                    "GtkSource": "4",
                },
            },
        },
        ...,
    )

.. note:: Currently the ``module-versions`` configuration is available only for ``GtkSource``, ``Gtk``, and ``Gdk``.

.. _matplotlib hook options:


GStreamer (gi.repository.Gst) hook
----------------------------------

The collection of GStreamer is subject to both the general ``gi`` hook
configuration (for example, collection of translations file as controlled
by the ``languages`` option) and by special hook configuration named
``gstreamer`` [#gstreamer_id]_ that controls collection of GStreamer plugins.

The GStreamer framework comes with a multitude of plugins that are
typically installed as separate packages (``gstreamer-plugins-base``,
``gstreamer-plugins-good``, ``gstreamer-plugins-bad``, and
``gstreamer-plugins-ugly``; the naming varies between packaging systems).
By default, MwlareBuilder collects *all* available plugins as well as their
binary dependencies; therefore, having all GStreamer plugins installed
in the build environment will likely result in collection of many
unnecessary plugins and increased frozen application size due to
potential complex dependency chains of individual plugins and the
underlying shared libraries.

**Hook identifier:** ``gstreamer`` [#gstreamer_id]_

**Options**

 * ``include_plugins`` [*list of strings*]: list of plugin names to
   include in the frozen application. Specifying the include list
   implicitly excludes all plugins that do not appear in the list.

 * ``exclude_plugins`` [*list of strings*]: list of plugin names to
   exclude from the frozen application. If include list is also available,
   the exclude list is applied after it; if not, the exclude list is
   applied to all available plugins.

Both include and exclude list expect base plugin names (e.g., ``audioparsers``,
``matroska`` , ``x264``, ``flac``). Internally, each name is converted into
a pattern (e.g., ``'**/*flac.*'``), and matched using ``fnmatch`` against
actual plugin file names. Therefore, it is also possible to include the
wildcard (``*``) in the plugin name [#gstreamer_plugin_prefix]_.

**Basic example: excluding an unwanted plugin**

Exclude the ``opencv`` GStreamer plugin to prevent pulling OpenCV shared
libraries into the frozen application.

.. code-block:: python

    a = Analysis(
        ["my-gstreamer-app.py"],
        ...,
        hooksconfig={
            "gstreamer": {
                "exclude_plugins": [
                    "opencv",
                ],
            },
        },
        ...,
    )

**Advanced example: including only specific plugins**

When optimizing the frozen application size, it is often more efficient
to explicitly include only the subset of the plugins that are actually
required for the application to function.

Consider the following simple player application:

.. code-block:: python

    # audio_player.py
    import sys
    import os

    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import GLib, Gst

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <filename>")
        sys.exit(-1)

    filename = os.path.abspath(sys.argv[1])
    if not os.path.isfile(filename):
        print(f"Input file {filename} does not exist!")
        sys.exit(-1)

    Gst.init(sys.argv)
    mainloop = GLib.MainLoop()

    playbin = Gst.ElementFactory.make("playbin", "player")
    playbin.set_property('uri', Gst.filename_to_uri(filename))
    playbin.set_property('volume', 0.2)
    playbin.set_state(Gst.State.PLAYING)

    mainloop.run()

Suppose that, although the application is using the generic ``playbin``
and ``player`` elements, we intend for the frozen application to play
only audio files. In that case, we can limit the collected plugins
as follows:


.. code-block:: python

    # The not-completely-optimized list of gstreamer plugins for playing a FLAC
    # (and possibly some other) audio files on linux and Windows.
    gst_include_plugins = [
        # gstreamer
        "coreelements",
        # gstreamer-plugins-base
        "alsa",  # Linux audio output
        "audioconvert",
        "audiomixer",
        "audiorate",
        "audioresample",
        "ogg",
        "playback",
        "rawparse",
        "typefindfunctions",
        "volume",
        "vorbis",
        # gstreamer-plugins-good
        "audioparsers",
        "auparse",
        "autodetect",
        "directsound", # Windows audio output
        "flac",
        "id3demux",
        "lame",
        "mpg123",
        "osxaudio",  # macOS audio output
        "pulseaudio",  # Linux audio output
        "replaygain",
        "speex",
        "taglib",
        "twolame",
        "wavparse",
        # gstreamer-plugins-bad
        "wasapi",  # Windows audio output
    ]

    a = Analysis(
        ["audio_player.py"],
        ...,
        hooksconfig={
            "gstreamer": {
                "include_plugins": gst_include_plugins,
            },
        },
        ...,
    )

Determining which plugins need to be collected may require good knowledge
of GStreamer pipelines and their plugin system, and may result in several
test iterations to see if the required multimedia functionality works as
expected. Unfortunately, there is no free lunch when it comes to optimizing
the size of application that uses a plugin system like that. Keep in mind
that in addition to obviously-named plugins (such as ``flac`` for
FLAC-related functionality), you will likely need to collect at least some
plugins that come from ``gstreamer`` itself (e.g., the ``coreelements``
one) and at least some that are part of ``gstreamer-plugins-base``.


.. [#gstreamer_id] While the hook is called ``gi.repository.Gst``, the
   identifier for Gstreamer-related options was chosen to be simply
   ``gstreamer``.

.. [#gstreamer_plugin_prefix] And it is also possible to get away with
   accidentally specifying the plugin prefix, which is typically `libgst`,
   but can also be `gst`, depending on the toolchain that was used to
   build GStreamer.


Matplotlib hooks
----------------

The hooks for the ``matplotlib`` package allow user to control the backend
collection behavior via ``backends`` option under the ``matplotlib``
identifier, as described below.

**Hook identifier:** ``matplotlib``

**Options**

 * ``backends`` [*string* or *list of strings*]: backend selection method
   or name(s) of backend(s) to collect. Valid string values: ``'auto'``,
   ``'all'``, or a human-readable backend name (e.g., ``'TkAgg'``). To
   specify multiple backends to be collected, use a list of strings
   (e.g., ``['TkAgg', 'Qt5Agg']``).

**Backend selection process**

If ``backends`` option is set to ``'auto'`` (or not specified), the hook
performs auto-detection of used backends, by scanning the code for
:func:`matplotlib.use` function calls with literal arguments. For example,
``matplotlib.use('TkAgg')`` being used in the code results in the
``TkAgg`` backend being collected. If no such calls are found, the default
backend is determined as the first importable GUI-based backend, using the
same priority list as internally used by the :func:`matplotlib.get_backend`
and :func:`matplotlib.pyplot.switch_backend` functions: ``['MacOSX',
'Qt5Agg', 'Gtk3Agg', 'TkAgg', 'WxAgg']``. If no GUI-based backend is
importable, the headless ``'Agg'`` is collected instead.

.. note::
    Due to limitations of the bytecode-scanning approach, only specific
    forms of :func:`matplotlib.use` invocation can be automatically detected.
    The backend must be specified as string literal (as opposed to being
    passed via a variable). The second optional argument, ``force``, can
    also be specified, but it must also be a literal and must not be
    specified as a keyword argument:

    .. code-block:: python

        import matplotlib

        matplotlib.use('TkAgg')  # detected
        matplotlib.use('TkAgg', False)  # detected

        backend = 'TkAgg'
        matplotlib.use(backend)  # not detected

        matplotlib.use('TkAgg', force=False)  # not detected

    In addition to ``matplotlib`` module name, its common alias, ``mpl``
    is also recognized:

    .. code-block:: python

        import matplotlib as mpl
        mpl.use('TkAgg')  # detected


    Importing the function from the module should also work:

    .. code-block:: python

        from matplotlib import use
        use('TkAgg')  # detected


If ``backends`` option is set to ``'all'``, all (importable) backends are
selected, which corresponds to the behavior of MwlareBuilder 4.x and earlier.
The list of importable backends depends on the packages installed in the
environment; for example, the ``Qt5Agg`` backend becomes importable if
either the ``PyQt5`` or the ``PySide2`` package is installed.

Otherwise, the value of the ``backends`` option is treated as a backend
name (if it is a string) or a list of backend names (if it is a list).
In the case of user-provided backend names, no additional validation
is performed; the backends are collected regardless of whether they are
importable or not.

**Example**

.. code-block:: python

    a = Analysis(
        ["my-matplotlib-app.py"],
        ...,
        hooksconfig={
            "matplotlib": {
                "backends": "auto",  # auto-detect; the default behavior
                # "backends": "all",  # collect all backends
                # "backends": "TkAgg",  # collect a specific backend
                # "backends": ["TkAgg", "Qt5Agg"],  # collect multiple backends
            },
        },
        ...,
    )

.. note::
    The ``Qt5Agg`` backend conditionally imports both the ``PyQt5`` and
    the ``PySide2`` package. Therefore, if both are installed in your
    environment, MwlareBuilder will end up collecting both. In addition
    to increasing the frozen application's size, this might also cause
    conflicts between the collected versions of the shared libraries.
    To prevent that, use the :option:`--exclude-module` option to exclude
    one of the two packages (i.e., ``--exclude-module PyQt5`` or
    ``--exclude-module PySide2``).



Adding an option to the hook
============================

Implementing support for hook options requires access to ``hook_api``
object, which is available only when hook implements the ``hook(hook_api)``
function (as described :ref:`here <The hook(hook_api) Function>`).

The value of a hook's configuration option can be obtained using the
:func:`~MwlareBuilder.utils.hooks.get_hook_config` function:

.. code-block:: python

    # hook-mypackage.py
    from MwlareBuilder.utils.hooks import get_hook_config

    # Processing unrelated to hook options, using global hook values
    binaries, datas, hiddenimports = ...

    # Collect extra data
    def hook(hook_api):
        # Boolean option 'collect_extra_data'
        if get_hook_config(hook_api, 'mypackage', 'collect_extra_data'):
            extra_datas = ...  # Collect extra data
            hook_api.add_datas(extra_datas)


After implementing option handling in the hook, please add a section
documenting it under :ref:`supported hooks and options`, to inform
the users of the option's availability and the meaning of its value(s).

The above hook example allows the user to toggle the collection of extra
data from ``mypackage`` by setting the corresponding option in their
:ref:`.spec file <using spec files>`:

.. code-block:: python

    a = Analysis(
        ["program-using-mypackage.py"],
        ...,
        hooksconfig={
            "mypackage": {
                "collect_extra_data": True,
            },
        },
        ...,
    )


.. include:: _common_definitions.txt

.. Emacs config:
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:
