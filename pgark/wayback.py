#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pgark.exceptions import *
from pgark.mylog import mylogger

from lxml.html import fromstring as htmlparse
from pathlib import Path
import re
import requests
from time import sleep

from urllib.parse import urljoin

BASE_DOMAIN = "http://web.archive.org"
BASE_ENDPOINT = urljoin(BASE_DOMAIN, 'save/')
JOB_STATUS_ENDPOINT = urljoin(BASE_ENDPOINT, 'status/')

DEFAULT_USER_AGENT = "pgark (https://github.com/dannguyen/pgark)"
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate,',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': BASE_DOMAIN,
}


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




def jobstatus_url(job_id:str) -> str:
    return urljoin(JOB_STATUS_ENDPOINT, job_id)

def savepage_url(target_url:str) -> str:
    return BASE_ENDPOINT + target_url


def get_job_status(job_id:str) -> dict:
    resp = requests.get(jobstatus_url(job_id))
    return resp.json()

def poll_job_status(job_id:str) -> dict:
    # get_job_status()
    pass

def check_availability(target_url:str) -> dict:
    """
    https://archive.org/wayback/available?url=www.whitehouse.gov/issues/immigration/
    """

    # because kenneth r said to send URL literal param directly....
    # https://stackoverflow.com/a/23497903
    resp = requests.get(f'https://archive.org/wayback/available?url={target_url}')
    # TODO: status check blah blah
    return resp.json()

def check_history():
    """
    TODO: Come up with better name
    http://web.archive.org/cdx/search/cdx?url=latimes.com&limit=-10&showResumeKey=false&output=json&fastLatest=true
    """
    pass

def snapshot(target_url:str, user_agent:str = DEFAULT_USER_AGENT) -> dict:

    mylogger.debug(f'Snapshotting: {target_url}')
    mylogger.debug(f'With user agent: {user_agent}')

    s_headers = DEFAULT_HEADERS.copy()
    s_headers['User-Agent'] = user_agent

    def _init_request(session, url):
        _headers = s_headers.copy()
        _headers.update({
            'Referer': BASE_DOMAIN,
        })
        resp = session.post(BASE_ENDPOINT, headers=_headers, data={'url_preload': url})
        return resp

    def _submit_request(session, url):
        save_url = savepage_url(url)
        _headers = s_headers.copy()
        _headers.update({'Referer': BASE_ENDPOINT})
        resp = session.post(save_url, headers=_headers, data={'url': url, 'capture_all': 'on'})
        return resp

    df = {'snapshot_status': 'pending',  'target_url': target_url, 'user_agent': user_agent, 'last_job_status': {}}

    session = requests.Session()
    mylogger.debug(f'Initial request to: {BASE_ENDPOINT}')
    init_resp = _init_request(session, target_url)


    mylogger.debug(f'Submit request...')
    sub_resp  = _submit_request(session, target_url)

    # TKTK
    df['job_id'] = extract_job_id(sub_resp.text)
    df['job_url'] = jobstatus_url(df['job_id'])
    for i in range(MAX_JOB_POLLS):
        mylogger.debug(f"""Polling status, attempt #{i+1}: {df['job_url']}""")

        js = get_job_status(df['job_id'])
        df['last_job_status'] = js
        if js.get('status') == 'success':
            df['snapshot_status'] = 'success'
            break
        else:
            sleep(3)

    return df
