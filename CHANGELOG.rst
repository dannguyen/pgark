*********
CHANGELOG
*********

0.0.2
=====

cli
---

- revamped common flags (e.g. ``-q,-v,-j``) to be shared among subcommands
- added ``--version`` flag to print current version


0.0.1
=====

cli
---

- Has basic logging via ``rich``
- Has ``-V/--verbosity`` and ``-q/--quiet`` flag
- Has ``-v/--version`` call

wayback.check() subcommand
--------------------------

- Basic implementation of call and interface for ``http://archive.org/wayback/available?url=example.com``
    - ``pgark check http://example.com``
    - has ``-j/--json`` flag

wayback.save() subcommand
-------------------------

- Basic implementation of call to web.archive.org/save
    - ``pgark save http://example.com``
     - has ``-j/--json`` flag
    - fixes breakage in current implementation of pastpages/savepagenow, as discussed in Issue `KeyError: 'link in capture' #26 <https://github.com/pastpages/savepagenow/issues/26>`_
