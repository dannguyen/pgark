import pytest
import pgark.archivers.wayback as wb
from pathlib import Path

import responses


@pytest.fixture()
def save_dupe_html():
    return Path("examples/web.archive.org/save-too-soon.html").read_text()


@pytest.fixture()
def save_submit_html():
    return Path("examples/web.archive.org/save-submit.html").read_text()


def test_jobstatus_url():
    assert wb.jobstatus_url("abc-789") == "http://web.archive.org/save/status/abc-789"


def test_savepage_url():
    target = "https://example.com/foo"
    assert (
        wb.savepage_url(target) == "http://web.archive.org/save/https://example.com/foo"
    )


def test_snapshot_url():
    target = "https://example.com"
    ts = "1999"
    assert (
        wb.snapshot_url(target, ts)
        == "http://web.archive.org/web/1999/https://example.com"
    )


def test_extract_job_id(save_submit_html):
    jobid = wb.extract_job_id(save_submit_html)
    assert jobid == "16e4e6ee-b97a-4fd2-ae5b-f6ce3aaea59b"


def test_extract_too_soon_message(save_dupe_html):
    msg = wb.extract_too_soon_message(save_dupe_html)
    assert (
        msg
        == """The same snapshot had been made 18 minutes and 39 seconds ago. We only allow new captures of the same URL every 20 minutes."""
    )


def text_extract_non_existent_too_soon_message(save_submit_html):
    msg = wb.extract_too_soon_message(save_submit_html)
    assert msg is False
