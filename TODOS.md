
# TODOS

Just done: published 0.0.1 to pypi: https://pypi.org/project/pgark/0.0.1/


- [ ] cli: make `--verbosity/--quiet` flag part of subcommands, not just main command
    - apparently do as a decorator? https://stackoverflow.com/questions/40182157/shared-options-and-flags-between-commands
- [ ] cli: add version flag `-V/--version`
    
- [x] Write cli `check` method; simply returns JSON. Should do something fancier?
    - [x] option to return just URL; user must set --json flag to get json
    - [wontfix] Check click docs to figure out how to make --json flag common to all subcommands

## `wayback save`

- [ ] add flag to perform check for nearest snapshot from right now


- how does `snapshot_url` change when target_url has query params and other messiness?
- in job status (`last_job_status`), how does `original_url` differ from `snapshot_url` IF there's a redirect?

- [?] is `_init_request` phase needed?
    - [ ] apparently not?

- current timestamp+URL is returned, even if it's using a cached version. Is there a way to inform user that a new cache was NOT saved?
    - [X] yes, implemented too_soon methods

- [ ] handle error condition when too many pages have been saved: `examples/web.archive.org/job-save-too-many`

- [ ] clean up the debug logging in `wayback.snapshot()`

- [ ] weird error condition in which job id could not be found in HTML, for a job that was recently done (time.gov)




- Think of a good object oriented way to handle the submethods, if needed...


- features:
    - save: create snapshot
    - latest/check: get latest url
    - status: get JSON inventory of url; use CDX endpoint
    - http://web.archive.org/cdx/search/cdx?url=latimes.com&limit=-10&showResumeKey=false&output=json&fastLatest=true

    - save waybackpack machine https://github.com/jsvine/waybackpack


