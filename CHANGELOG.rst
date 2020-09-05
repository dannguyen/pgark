*********
CHANGELOG
*********

0.0.3
=====

General
-------

- Archiver data object
    - subcommands now return expected app/request-specific metadata (e.g. "snapshot_url", "target_url"), while also having a "server_payload" key that contains the last/most relevant JSON payload returned from server
    - data has a ``"issues": {}`` key to contain warnings and other problematic, but not error-level situations, e.g. Wayback machine saying too many snapshots made in a day


wayback.save
------------

- has basic handling of situation in which Wayback Machine says too many captures made that day:
    - Calls availability endpoint and returns most recent snapshot URL



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
