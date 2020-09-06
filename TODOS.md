
# TODOS




On deck:
- [x] redo tasks/savepage_debug.py, save headers and stuff too
    - [ ] think of more robust design for a debug callback

- [X] wayback.save: add `-wt/--within` to skip saving if the most recent snapshot is within `[HOURS]`
    - [x] basic implementation stuffed in cli
    - [x] failing test test_save_unless_within_hours() to implement later

- [ ] write a few more tests, especially for cli.save subcommand
- [ ] TaskMeta needs some refactoring and better OOP design

----------------------------------

In general

- [X] added pipenv stuff to Makefile; use `make freeze` and `make ship` to publish to pypi
- [X] created TaskMeta class
    - [ ] Should `server_payload` include HTML if HTML is the last/most relevant response?
- [ ] Handle 50x status errors; should be dealt gracefully at CLI level
- [ ] Document issue in which Wayback Machine availability tells us latest attempted snapshot, but returns an older timestamp(?)
- [ ] for too_many_today/too_soon, is there a header returned in the submit phase?




----------------------------------
#### `wayback save`


- [ ] clean up the debug logging in `wayback.snapshot()`
- [ ] how does `snapshot_url` change when target_url has query params and other messiness?
- [ ] in job status (`server_payload`), how does `original_url` differ from `snapshot_url` IF there's a redirect?
- [ ] weird error condition in which job id could not be found in HTML, for a job that was recently done (time.gov)
- [ ] How to handle robots situation?


- [X] wayback.save: when Wayback says "too many captures for today", fall back to availability API check to get nearest snapshot
    - [X] example response: `examples/web.archive.org/job-save-too-many-today`


- 
- [X] In `save` JSON response, rename `snapshot_status` to something different, like `was_new_snapshot_created`
- [?] is `_init_request` phase needed?
    - [X] apparently not?


- current timestamp+URL is returned, even if it's using a cached version. Is there a way to inform user that a new cache was NOT saved?
    - [X] yes, implemented too_soon methods



----------------------------------
#### cli


- [ ] add '--log-json/--oj/--output-json' to output JSON response to a file
- [X] cli: make `--verbosity/--quiet` flag part of subcommands, not just main command
    - apparently do as a decorator? https://stackoverflow.com/questions/40182157/shared-options-and-flags-between-commands
- [X] cli: add version flag `-V/--version`
    
- [x] Write cli `check` method; simply returns JSON. Should do something fancier?
    - [x] option to return just URL; user must set --json flag to get json
    - [wontfix] Check click docs to figure out how to make --json flag common to all subcommands

- Think of a good object oriented way to handle the submethods, if needed...
