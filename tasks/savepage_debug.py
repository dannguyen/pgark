#!/usr/bin/env python3
import json
from urllib.parse import urljoin
from requests.utils import parse_header_links
import requests
from pathlib import Path
from sys import argv
from time import sleep


from pgark.archivers.wayback import *



def main():
    """hack routine that does wayback.save the manual way, while saving each
        response by wayback into the dest_dir

        TO BE DEPRECATED
    """
    target_url = argv[1]
    dest_dir = Path('examples', argv[2])
    dest_dir.mkdir(exist_ok=True, parents=True)

    user_agent = 'Mozilla'

    session = requests.Session()
    init_headers = DEFAULT_HEADERS.copy()
    init_headers.update({
        'User-Agent': user_agent,
        'Referer': BASE_DOMAIN,
    })
    init_resp = session.post(SAVE_ENDPOINT, headers=init_headers, data={'url_preload': target_url})
    # TODO: test that init_resp is good
    dest_dir.joinpath('init-response.html').write_text(init_resp.text)


    save_url = url_for_savepage(target_url)
    save_headers = init_headers.copy()
    save_headers.update({'Referer': SAVE_ENDPOINT})
    save_payload = {'url': target_url, 'capture_all': 'on'}
    save_resp = session.post(save_url, headers=save_headers, data=save_payload)
    dest_dir.joinpath('submit-response.html').write_text(save_resp.text)

    # TKTK

    job_id = extract_job_id(save_resp.text)
    job_url = url_for_jobstatus(job_id)
    print(f'{job_id=}\n{job_url=}')


    stats = []
    for i in range(20):
        jobx = fetch_job_status(job_id)
        dest_path = dest_dir.joinpath(f'status-{i}.json')
        dest_path.write_text(json.dumps(jobx, indent=2))
        print(dest_path)
        if jobx['status'] == 'success':
            print('SUCCESS')
            break
        else:
            sleep(3)



if __name__ == '__main__':
    main()
