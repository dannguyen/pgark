pgark
=====

Python library and CLI for archiving URLs on popular services like
Wayback Machine

Basically a fork of the great
[pastpages/savepagenow](https://github.com/pastpages/savepagenow)

How to use
----------

Install with:

    $ pip install pgark


The available subcommands are:

```
  check  Check if there is a snapshot of [URL] on the [-s/--service].
  save   Attempt to save a snapshot of [URL] using the [-s/--service].
```

(for now, only the Wayback Machine service is implemented, so ignore `-s` flag)



#### Saving a snapshot of a URL

    $ pgark save whitehouse.gov
    http://web.archive.org/web/20200904230109/https://www.whitehouse.gov/

To get the JSON response with pgark-snapshot metadata and the Wayback
Machine API job status response, pass in `-j/--json` flag:

    $ pgark -j save whitehouse.gov

```json
  {
    "snapshot_url": "http://web.archive.org/web/20200904230109/https://www.whitehouse.gov/",
    "...": "...",
    "server_payload": {
      "status": "success",
      "duration_sec": 10.638,
      "job_id": "443e89c2-fd3e-4d01-bd35-abfccc3a124a",
      "...": "..."
    }
  }
```

See an example of the Wayback Machine\'s full JSON response in:
[examples/web.archive.org/job-save-success.json](examples/web.archive.org/job-save-success.json)


#### Checking if a URL is already snapshotted

For a given URL, to get the latest available snapshot for a URL:

    $ pgark check whitehouse.gov

    http://web.archive.org/web/20200904180914/https://www.whitehouse.gov/

To get the JSON response from the Wayback Machine API, pass in the
`-j/--json` flag:

    $ pgark check -j whitehouse.gov


```json
{
    "snapshot_url": "http://web.archive.org/web/20200904180914/https://www.whitehouse.gov/",
    "server_payload": {
    "archived_snapshots": {
      "closest": {
        "timestamp": "20200904180914",
        "status": "200",
        "available": true,
        "url": "http://web.archive.org/web/20200904180914/https://www.whitehouse.gov/"
      }
    },
    "url": "whitehouse.gov"
  }
}
```



Project status
--------------

Just spitballing. Will probably just return to forking savepagenow and
adding any changes/fixes.

See [CHANGELOG](CHANGELOG.rst) for more details

Similar libraries, resources, and inspirations
----------------------------------------------


- Wayback Machine official docs and stuff"
    - https://archive.org/help/wayback_api.php
        - https://github.com/ArchiveLabs/api.archivelab.org
        - - https://archive.org/services/docs/api/wayback-cdx-server.html?highlight=wayback


- Other libraries and utilities:
    - https://github.com/pastpages/savepagenow
    - https://github.com/jsvine/waybackpack
    - https://www.vice.com/en_us/article/wj7mkb/mass-archive-tool-python-wayback-machine-perma-achiveis
      + https://github.com/motherboardgithub/mass_archive
    - https://github.com/sangaline/wayback-machine-scraper


- Other stuff:
    - https://notes.peter-baumgartner.net/2019/08/01/scraping-archived-data-with-the-wayback-machine/
    - https://pywb.readthedocs.io/en/latest/index.html




Development notes
-----------------


To get setup:

```
$ make init
```



To run tests:

```
$ make test
```


To freeze Pipfile.lock and resync with setup.py

```
$ make freeze
```
