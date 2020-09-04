#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pgark.exceptions import *
from pgark.mylog import mylogger

from lxml.html import fromstring as htmlparse
from pathlib import Path
import re
import requests
from time import sleep
from typing import NoReturn, Tuple as tyTuple, Union as tyUnion

from urllib.parse import urljoin

BASE_DOMAIN = "http://web.archive.org"
AVAILABLE_ENDPOINT = 'https://archive.org/wayback/available'
SAVE_ENDPOINT = urljoin(BASE_DOMAIN, 'save/')
JOB_STATUS_ENDPOINT = urljoin(SAVE_ENDPOINT, 'status/')

DEFAULT_USER_AGENT = "pgark (https://github.com/dannguyen/pgark)"
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate,',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': BASE_DOMAIN,
}

DEFAULT_POLL_INTERVAL = 3


MAX_JOB_POLLS = 20

def extract_job_id(html:str) -> str:
    soup = htmlparse(html)
    matches = soup.xpath('//script[contains(text(), "spn.watchJob")]/text()')
    if matches:
        jobm = re.search(r'watchJob\("([^"]+)', matches[0])
        if jobm:
            return jobm.groups()[0]
        else:
            # TODO TK
            raise SaveJobError(f"Could not find job ID; malformed watchJob script: {matches[0]}")
    else:
        # tktk
        raise SaveJobError("Could not find job id in response HTML")


def extract_too_soon_message(html:str) -> tyUnion[str,bool]:
    """
    If a snapshot has been made in the last 20 minutes, web.archive.org returns a notice
    in the HTML, e.g.
        The same snapshot had been made 8 minutes and 12 seconds ago. We only allow new captures of the same URL every 20 minutes.
    """
    soup = htmlparse(html)
    matches = soup.xpath('//p[contains(text(), "The same snapshot")]/text()')
    if matches:
        return matches[0]
    else:
        return False


def availability_url(target_url:str) -> str:
    return f'{AVAILABLE_ENDPOINT}?url={target_url}'

def jobstatus_url(job_id:str) -> str:
    return urljoin(JOB_STATUS_ENDPOINT, job_id)

def savepage_url(target_url:str) -> str:
    return SAVE_ENDPOINT + target_url

def snapshot_url(target_url:str, timestamp:tyUnion[str,int]) -> str:
    return '/'.join( [BASE_DOMAIN, 'web', str(timestamp), target_url])

def get_job_status(job_id:str) -> dict:
    resp = requests.get(jobstatus_url(job_id))
    return resp.json()



def check_availability(target_url:str) -> tyTuple[tyUnion[None, str], dict]:
    """
    https://archive.org/wayback/available?url=www.whitehouse.gov/issues/immigration/
    """

    # because kenneth r said to send URL literal param directly....
    # https://stackoverflow.com/a/23497903
    resp = requests.get(availability_url(target_url))
    # TODO: status check blah blah
    if not resp.status_code == 200:
        raise ServiceError(f"Did not get OK HTTP status; got: {resp.status_code}")
    else:
        data = resp.json()
        answer = data['archived_snapshots']['closest']['url'] if data.get('archived_snapshots') else None
        return (answer, data)



# TODO: this step is apparently not needed?
# def submit_init_request(session, url):
#     _headers = s_headers.copy()
#     _headers.update({
#         'Referer': BASE_DOMAIN,
#     })
#     resp = session.post(SAVE_ENDPOINT, headers=_headers, data={'url_preload': url})
#     return resp


def submit_snapshot_request(session, url, headers):
    save_url = savepage_url(url)
    sub_headers = headers.copy()
    sub_headers.update({'Referer': SAVE_ENDPOINT})
    resp = session.post(save_url, headers=sub_headers, data={'url': url, 'capture_all': 'on'})
    # todo: error out on status code != 200
    if resp.status_code != 200:
        raise WaybackSubmitError(f"""Server status was NOT OK; returned {resp.status_code} for: {save_url}""")
    else:
        return resp


def snapshot(target_url:str, user_agent:str = DEFAULT_USER_AGENT,
    poll_interval=DEFAULT_POLL_INTERVAL) -> tyTuple[tyUnion[None, str], dict]:
    mylogger.debug(f'Snapshotting: {target_url}')
    mylogger.debug(f'With user agent: {user_agent}')

    headers = DEFAULT_HEADERS.copy()
    headers['User-Agent'] = user_agent

    df = {  'snapshot_status': 'pending',
            'snapshot_url': None,
            'too_soon': False,
            'too_soon_message': '',
            'snapshot_request': {
                'target_url': target_url,
                'user_agent': user_agent,
            },
            'job_id': None,
            'job_url': None,
            'last_job_status': {}
        }

    session = requests.Session()


    # TODO: this step is apparently not needed?
    # mylogger.debug(f'Initial request to: {SAVE_ENDPOINT}')
    # init_resp = _init_request(session, target_url)

    mylogger.info(f'Making submission request to {SAVE_ENDPOINT} for {target_url}')
    sub_resp  = submit_snapshot_request(session, target_url, headers)
    #check to see if dupe
    if _tx := extract_too_soon_message(sub_resp.text):
        df['too_soon'] = True
        df['too_soon_message'] = _tx

    # TKTK
    df['job_id'] = extract_job_id(sub_resp.text)
    df['job_url'] = jobstatus_url(df['job_id'])
    for i in range(MAX_JOB_POLLS):
        mylogger.debug(f"""Polling status, attempt #{i+1}: {df['job_url']}""")

        js = get_job_status(df['job_id'])
        df['last_job_status'] = js

        if js.get('status') == 'success':
            df['snapshot_status'] = 'success'
            df['snapshot_url'] = snapshot_url(js['original_url'], js['timestamp'])
            break
        else:
            if poll_interval:
                sleep(poll_interval)

    answer = df['snapshot_url']
    return (answer, df)



# def check_history():
#     """
#     TODO: Come up with better name
#     http://web.archive.org/cdx/search/cdx?url=latimes.com&limit=-10&showResumeKey=false&output=json&fastLatest=true
#     """
#     pass
