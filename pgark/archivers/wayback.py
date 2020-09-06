#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pgark.exceptions import *
from pgark import mylogger
from pgark.task_meta import TaskMeta


from datetime import datetime
import json as jsonlib
from lxml.html import fromstring as htmlparse, HtmlElement
from pathlib import Path
import re
import requests
from time import sleep
from typing import NoReturn, Tuple as tyTuple, Union as tyUnion
from urllib.parse import urljoin

BASE_DOMAIN = "http://web.archive.org"
AVAILABLE_ENDPOINT = "https://archive.org/wayback/available"
SAVE_ENDPOINT = urljoin(BASE_DOMAIN, "save/")
JOB_STATUS_ENDPOINT = urljoin(SAVE_ENDPOINT, "status/")

DEFAULT_USER_AGENT = "pgark (https://github.com/dannguyen/pgark)"
DEFAULT_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Encoding": "gzip, deflate,",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": BASE_DOMAIN,
}

DEFAULT_POLL_INTERVAL = 3

DEFAULT_MAX_POLL_ATTEMPTS = 25


def check_availability(
    target_url: str, user_agent: tyUnion[None, str] = DEFAULT_USER_AGENT
) -> tyTuple[tyUnion[None, str], TaskMeta]:
    """

    API info:
        https://archive.org/help/wayback_api.php

    Simple call:
        https://archive.org/wayback/available?url=www.whitehouse.gov/issues/immigration/

    Sample 'server_payload':
    {
        "archived_snapshots": {
            "closest": {
                "available": true,
                "url": "http://web.archive.org/web/20060101064348/http://www.example.com:80/",
                "timestamp": "20060101064348",
                "status": "200"
            }
        }
    }
    """

    task = TaskMeta(target_url=target_url, service="wayback", subcommand="check")
    resp = requests.get(url_for_availability(target_url))
    # TODO: status check blah blah
    if not resp.status_code == 200:
        raise ServerStatusError(f"Did not get OK HTTP status; got: {resp.status_code}")
    else:
        task.set_payload(resp.json())
        # TODO: this should be handled by TaskMeta somehow....
        if ax := task.server_payload["archived_snapshots"]:
            task.snapshot_url = ax["closest"]["url"]

        return task.snapshot_url, task


def snapshot(
    target_url: str,
    within_hours: int = None,
    user_agent: str = DEFAULT_USER_AGENT,
    poll_interval=DEFAULT_POLL_INTERVAL,
    poll_attempts=DEFAULT_MAX_POLL_ATTEMPTS,
    **kwargs,
) -> tyTuple[tyUnion[None, str], TaskMeta]:

    _debug_path = kwargs.get('debug_path')

    mylogger.debug(f"Snapshotting: {target_url}")
    mylogger.debug(f"With user agent: {user_agent}")

    headers = DEFAULT_HEADERS.copy()
    headers["User-Agent"] = user_agent

    session = requests.Session()
    meta = TaskMeta(
        target_url=target_url,
        service="wayback",
        subcommand="snapshot",
        user_agent=user_agent,
    )


    if within_hours and _check_availability_within(within_hours, meta):
        return (meta.snapshot_url, meta)


    # if we get to here, we proceed as normal, and assume that recent_snapshot did not
    # meet within-hours cutoff, if it was even specified
    mylogger.info(f"Making submission request to {SAVE_ENDPOINT} for {target_url}")
    submit_resp = submit_snapshot_request(session, target_url, headers)

    if _debug_path:
        outpath = _debug_path.joinpath('submit-snapshot-response.html')
        outpath.write_text(submit_resp.text)
        mylogger.debug(f'Wrote to: {outpath}', label='snapshot-debug')

        dh = {}
        dh['response'] = dict(submit_resp.headers)
        dh['request'] = dict(submit_resp.request.headers)
        outpath = _debug_path.joinpath('submit-snapshot-headers.json')
        outpath.write_text(jsonlib.dumps(dh, indent=2))
        mylogger.debug(f'Wrote to: {outpath}', label='snapshot-debug')


    meta.set_issues(parse_snapshot_issues(submit_resp.text))
    if meta.too_many_during_period():
        # this means there is no job to capture, and we have to get
        # snapshot URL using check_availability method
        mylogger.debug(
            "Wayback Machine says too many captures for today, so calling availability API..."
        )
        # TODO: do special error handling here? If availability API is down, we should still return
        #   some kind of partial response...
        meta.snapshot_url, ck = check_availability(target_url)
        meta.set_payload(ck.server_payload)
        meta.redirected_task = "check"

    ### /issues
    else:
        for i, jdata in poll_job_status(submit_resp, meta, poll_attempts, poll_interval):
            if _debug_path:
                outpath = _debug_path.joinpath(f"status-{str(i).rjust(2, '0')}.json")
                outpath.write_text(jsonlib.dumps(jdata, indent=2))
                mylogger.debug(f'Wrote to: {outpath}' , label='snapshot-debug')


    if _debug_path:
        outpath = _debug_path.joinpath('taskmeta.json')
        outpath.write_text(jsonlib.dumps(meta.to_dict(), indent=2))
        mylogger.debug(f'Wrote to: {outpath}', label='snapshot-debug')


    answer = meta.snapshot_url
    return (answer, meta)


# def check_history():
#     """
#     TODO: Come up with better name
#     http://web.archive.org/cdx/search/cdx?url=latimes.com&limit=-10&showResumeKey=false&output=json&fastLatest=true
#     """
#     pass


###################################################################
# middle methods


def _check_availability_within(within_hours, taskmeta:TaskMeta) -> bool:
    # do intermediary check availability
    # MESSY MESSY TODO
    target_url = taskmeta.target_url

    mylogger.debug(
        f"Checking availability of most recent snapshot since {within_hours} hours"
    )
    taskmeta.request_meta["within_hours"] = within_hours
    recent_url, rmeta = check_availability(target_url)
    if recent_url:
        urltime = extract_wayback_datetime(recent_url)

        if not taskmeta.created_within(within_hours, dt=urltime):
            mylogger.debug(
                f"Recent snapshot URL did not meet threshold of {within_hours} hours, proceeding with normal save"
            )
            return False
        else:
            mylogger.debug(
                f"Recent snapshot URL within threshold of {within_hours} hours; returning availability response"
            )
            taskmeta.redirected_task = rmeta
            taskmeta.snapshot_url = rmeta.snapshot_url
            taskmeta.set_payload(rmeta.server_payload)
            return True


def fetch_job_status(job_id: tyUnion[str, HtmlElement]) -> dict:
    job_id = job_id if isinstance(job_id, str) else extract_job_id(job_id)
    resp = requests.get(url_for_jobstatus(job_id))
    return resp.json()


def parse_snapshot_issues(html: str) -> dict:
    dd = {}
    soup = htmlparse(html)

    dd["too_soon"] = extract_too_soon_issue(soup)
    dd["too_many_during_period"] = extract_too_many_during_period_issue(soup)

    return dd


def poll_job_status(resp:requests.models.Response, meta:TaskMeta, poll_attempts:int, poll_interval:tyUnion[int, None]) -> NoReturn:
    job_id = extract_job_id(resp.text)
    job_url = url_for_jobstatus(job_id)
    for i in range(poll_attempts):
        mylogger.debug(f"""Polling status, attempt #{i+1}: {job_url}""")

        job_resp = fetch_job_status(job_url)
        yield i, job_resp  # for debugging purposes

        meta.set_payload(job_resp)
        # TODO: figure out a better way to have the Meta class handle this...
        if job_resp.get("status") == "success":
            meta.snapshot_url = url_for_snapshot(
                job_resp["original_url"], job_resp["timestamp"]
            )

        if meta.is_success():
            break
        else:
            if poll_interval:
                sleep(poll_interval)

def submit_snapshot_request(session:requests.sessions.Session, url:str, headers:dict) -> requests.models.Response:
    save_url = url_for_savepage(url)
    sub_headers = headers.copy()
    sub_headers.update({"Referer": SAVE_ENDPOINT})
    resp = session.post(
        save_url, headers=sub_headers, data={"url": url, "capture_all": "on"}
    )
    # todo: error out on status code != 200
    if resp.status_code != 200:
        raise ServerStatusError(
            f"""Server status was NOT OK; returned {resp.status_code} for: {save_url}"""
        )
    else:
        return resp


###################################################################
### extractors and other helpers
def extract_job_id(html: tyUnion[str, HtmlElement]) -> str:
    soup = html if isinstance(html, HtmlElement) else htmlparse(html)
    matches = soup.xpath('//script[contains(text(), "spn.watchJob")]/text()')
    if matches:
        jobm = re.search(r'watchJob\("([^"]+)', matches[0])
        if jobm:
            return jobm.groups()[0]
        else:
            # TODO TK
            raise SaveJobError(
                f"Could not find job ID; malformed watchJob script: {matches[0]}"
            )
    else:
        # tktk
        raise SaveJobError("Could not find job id in response HTML")


def extract_too_soon_issue(html: tyUnion[str, HtmlElement]) -> tyUnion[str, bool]:
    """
    If a snapshot has been made in the last 20 minutes, web.archive.org returns a notice
    in the HTML, e.g.
        The same snapshot had been made 8 minutes and 12 seconds ago. We only allow new captures of the same URL every 20 minutes.
    """
    soup = html if isinstance(html, HtmlElement) else htmlparse(html)
    matches = soup.xpath(
        '//p[contains(text(), "The same snapshot had been made")]/text()'
    )
    if matches:
        return matches[0]
    else:
        return False


def extract_wayback_datetime(txt: str) -> datetime:
    """
    txt is either a 14-char timestamp by itself:
            "20200312180055"
        or part of a URL like:
            "http://web.archive.org/web/20200903230055/https://www.whitehouse.gov/issues/immigration/"

    Returns a datetime object with UTC timezone
    """

    try:
        m = re.search(r"(?:^|/)(\d{14})(?:$|/)", txt)
        ts = m.groups()[0] + " +0000"
        dt = datetime.strptime(ts, "%Y%m%d%H%M%S %z")
    except Exception as e:
        raise ValueError(
            f"Attempted to extract a 14-digit timestamp, but did not find pattern in {txt}"
        )
    else:
        return dt


def extract_too_many_during_period_issue(
    html: tyUnion[str, HtmlElement]
) -> tyUnion[str, bool]:
    """
    If too many snapshots in a time period, web.archive.org returns a notice
    in the HTML, e.g.
        <p>This URL has been already captured 10 times today. Please email us at "info@archive.org" if you would like to discuss this more.</p>

    """
    soup = html if isinstance(html, HtmlElement) else htmlparse(html)

    matches = soup.xpath(
        '//p[contains(text(), "This URL has been already captured")]/text()'
    )
    if len(matches) == 1:
        return matches[0]
    else:
        if len(matches) == 0:
            return False
        else:
            # note: this has never happened, but oh well
            raise AbnormalSubmitResponse(
                f"Looked for 'URL has already been captured' text but received an unexpected number of occurrences: {len(matches)}"
            )


def url_for_availability(target_url: str) -> str:
    return f"{AVAILABLE_ENDPOINT}?url={target_url}"


def url_for_jobstatus(job_id: str) -> str:
    return urljoin(JOB_STATUS_ENDPOINT, job_id)


def url_for_savepage(target_url: str) -> str:
    return SAVE_ENDPOINT + target_url


def url_for_snapshot(target_url: str, timestamp: tyUnion[str, int]) -> str:
    return "/".join([BASE_DOMAIN, "web", str(timestamp), target_url])
