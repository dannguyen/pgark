
# TODOS

Most recent: 

- [X] wayback.save: when Wayback says "too many captures for today", fall back to availability API check to get nearest snapshot

----------------------------------

In general

- [ ] Should `server_payload` include HTML if HTML is the last/most relevant response?


----------------------------------
#### `wayback save`
- [ ] wayback.save: add flag to only save UNLESS a snapshot was found within x-days/time


- [ ] clean up the debug logging in `wayback.snapshot()`
- how does `snapshot_url` change when target_url has query params and other messiness?
- in job status (`server_payload`), how does `original_url` differ from `snapshot_url` IF there's a redirect?

- [in progress] handle error condition when too many pages have been saved: `examples/web.archive.org/job-save-too-many`
- 
- [X] In `save` JSON response, rename `snapshot_status` to something different, like `was_new_snapshot_created`
- [?] is `_init_request` phase needed?
    - [X] apparently not?


- current timestamp+URL is returned, even if it's using a cached version. Is there a way to inform user that a new cache was NOT saved?
    - [X] yes, implemented too_soon methods



- [ ] weird error condition in which job id could not be found in HTML, for a job that was recently done (time.gov)




----------------------------------
#### cli

- [X] cli: make `--verbosity/--quiet` flag part of subcommands, not just main command
    - apparently do as a decorator? https://stackoverflow.com/questions/40182157/shared-options-and-flags-between-commands
- [X] cli: add version flag `-V/--version`
    
- [x] Write cli `check` method; simply returns JSON. Should do something fancier?
    - [x] option to return just URL; user must set --json flag to get json
    - [wontfix] Check click docs to figure out how to make --json flag common to all subcommands

- Think of a good object oriented way to handle the submethods, if needed...
