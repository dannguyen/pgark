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
