import pytest
import requests

from pathlib import Path
import pgark.wayback as wb

@pytest.fixture
def job_success_id(requests_mock):
    _id = 'af709a09-c909-4883-b6b3-7350f9be8d7c'
    _body = Path('examples/web.archive.org/job-status-success.json').read_text()
    _url = wb.jobstatus_url(_id)
    requests_mock.get(_url, text=_body)

    return _id


def test_save_job_polling(job_success_id):
    resp = wb.get_job_status(job_success_id)
    assert resp['status'] == 'success'


@pytest.mark.skip(reason='not implemented')
def test_snapshot(self):
    pass


####################
### snapshot method

def test_snapshot_submit_request(requests_mock):
    target_url = 'https://plainlanguage.gov/'
    save_url = wb.savepage_url(target_url)

    resptext = text=Path('examples/web.archive.org/job-save-success/submit-response.html').read_text()
    requests_mock.post(
                        save_url,
                        # data={'url': target_url, 'capture_all': 'on'},
                        text=resptext,
                        )

    resp = wb.submit_snapshot_request(requests.Session(), target_url, headers={})


    assert f'<h2 id="spn-title">Saving page {target_url}</h2>' in resp.text
