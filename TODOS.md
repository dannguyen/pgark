# TODOS

- Write cli `check` method; simply returns JSON. Should do something fancier?
    - option to return just URL; user must set --json flag to get json
- Think of a good object oriented way to handle the submethods, if needed...
- Check click docs to figure out how to make --json flag common to all subcommands


- features:
    - save: create snapshot
    - latest/check: get latest url
    - status: get JSON inventory of url; use CDX endpoint
    - http://web.archive.org/cdx/search/cdx?url=latimes.com&limit=-10&showResumeKey=false&output=json&fastLatest=true

    - save waybackpack machine https://github.com/jsvine/waybackpack


