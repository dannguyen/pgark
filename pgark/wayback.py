#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pgark.exceptions import *


from lxml.html import fromstring as htmlparse
from pathlib import Path
import re
import requests
from urllib.parse import urljoin

BASE_DOMAIN = "http://web.archive.org"
BASE_ENDPOINT = urljoin(BASE_DOMAIN, 'save')

DEFAULT_USER_AGENT = "pgark (https://github.com/dannguyen/pgark)"
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate,',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': BASE_DOMAIN,
}


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


def poll_job_status(job_id:str):
    pass

def savepage_url(target_url:str) -> str:
    return '/'.join([BASE_ENDPOINT, target_url])


def snapshot(target_url:str, user_agent:str = DEFAULT_USER_AGENT):
    session = requests.Session()
    init_headers = DEFAULT_HEADERS.copy()
    init_headers.update({
        'User-Agent': user_agent,
        'Referer': BASE_DOMAIN,

    })

    init_resp = session.post(BASE_ENDPOINT, headers=init_headers, data={'url_preload': target_url})
    # TODO: test that init_resp is good

    save_url = savepage_url(target_url)
    save_headers = init_headers.copy()
    save_headers.update({'Referer': BASE_ENDPOINT})
    save_payload = {'url': target_url, 'capture_all': 'on'}

    save_resp = session.post(save_url, headers=save_headers, data=save_payload)
    # TKTK
    job_id = extract_job_id(save_resp.text)
    # TODO: make this a method that performs the actual request
    poll_job_status(job_id)
