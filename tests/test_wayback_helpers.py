import pytest
import pgark.archivers.wayback as wb
from pathlib import Path

import responses


@pytest.fixture()
def too_soon_html():
    return Path("examples/web.archive.org/save-too-soon.html").read_text()


@pytest.fixture()
def save_submit_html():
    return Path("examples/web.archive.org/save-submit.html").read_text()


@pytest.fixture()
def too_many_html():
    return Path(
        "examples/web.archive.org/job-save-too-many-today/submit-response.html"
    ).read_text()


def test_extract_wayback_datetime():
    timestamp = "20200312180055"
    dx = wb.extract_wayback_datetime(timestamp)
    assert dx.year == 2020
    assert dx.month == 3
    assert dx.day == 12
    assert dx.hour == 18
    assert dx.minute == 0
    assert dx.second == 55

    url = "http://web.archive.org/web/20200903234402/https://www.whitehouse.gov/issues/immigration/"
    dy = wb.extract_wayback_datetime(url)
    assert dy.year == 2020
    assert dy.month == 9
    assert dy.day == 3
    assert dy.hour == 23
    assert dy.minute == 44
    assert dy.second == 2


def test_url_for_jobstatus():
    assert (
        wb.url_for_jobstatus("abc-789") == "http://web.archive.org/save/status/abc-789"
    )


def test_url_for_savepage():
    target = "https://example.com/foo"
    assert (
        wb.url_for_savepage(target)
        == "http://web.archive.org/save/https://example.com/foo"
    )


def test_url_for_snapshot():
    target = "https://example.com"
    ts = "1999"
    assert (
        wb.url_for_snapshot(target, ts)
        == "http://web.archive.org/web/1999/https://example.com"
    )


def test_extract_job_id(save_submit_html):
    jobid = wb.extract_job_id(save_submit_html)
    assert jobid == "16e4e6ee-b97a-4fd2-ae5b-f6ce3aaea59b"


def test_extract_too_soon_issue(too_soon_html):
    msg = wb.extract_too_soon_issue(too_soon_html)
    assert (
        msg
        == """The same snapshot had been made 18 minutes and 39 seconds ago. We only allow new captures of the same URL every 20 minutes."""
    )


def test_extract_non_existent_too_soon_issue(save_submit_html):
    msg = wb.extract_too_soon_issue(save_submit_html)
    assert msg is False


def test_extract_too_many_during_period_issue(too_many_html):
    msg = wb.extract_too_many_during_period_issue(too_many_html)
    assert (
        msg
        == """This URL has been already captured 10 times today. Please email us at "info@archive.org" if you would like to discuss this more."""
    )


def test_parse_snapshot_issues(save_submit_html, too_many_html, too_soon_html):
    x = wb.parse_snapshot_issues(save_submit_html)
    assert x["too_soon"] is False
    assert x["too_many_during_period"] is False

    y = wb.parse_snapshot_issues(too_many_html)
    assert y["too_soon"] is False
    assert (
        "This URL has been already captured 10 times today"
        in y["too_many_during_period"]
    )

    z = wb.parse_snapshot_issues(too_soon_html)
    assert "The same snapshot had been made" in z["too_soon"]
    assert z["too_many_during_period"] is False
