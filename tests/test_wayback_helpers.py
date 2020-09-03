import pytest
import pgark.wayback as wb
from pathlib import Path

@pytest.fixture()
def save_submit_html():
    return Path('examples/web.archive.org/save-submit.html').read_text()


def test_jobstatus_url():
    assert wb.jobstatus_url('abc-789') == 'http://web.archive.org/save/status/abc-789'

def test_savepage_url():
    target = 'https://example.com/foo'
    assert wb.savepage_url(target) == 'http://web.archive.org/save/https://example.com/foo'


def test_extract_job_id(save_submit_html):
    jobid = wb.extract_job_id(save_submit_html)
    assert jobid == '16e4e6ee-b97a-4fd2-ae5b-f6ce3aaea59b'
