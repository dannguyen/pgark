import pytest
from pgark.wayback import *


def test_savepage_url():
    target = 'https://example.com/foo'
    assert savepage_url(target) == 'http://web.archive.org/save/https://example.com/foo'


def test_extract_job_id():
    srcpath = Path('examples/web.archive.org/save-submit.html')
    jobid = extract_job_id(srcpath.read_text())
    assert jobid == '16e4e6ee-b97a-4fd2-ae5b-f6ce3aaea59b'

@pytest.mark.skip(reason='not implemented')
def test_snapshot(self):
    pass
