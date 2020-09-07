import pytest
import responses

import json as jsonlib
from pathlib import Path

import pgark
import pgark.archivers.wayback as wb

FIXTURES_DIR = Path("tests/fixtures/_old")


@pytest.fixture
def success_urls():
    target_url = "https://plainlanguage.gov/"
    expected_url = wb.url_for_snapshot(target_url, "20200904183020")
    return (target_url, expected_url)


@pytest.fixture
def save_success_response(success_urls):
    srcdir = FIXTURES_DIR.joinpath("job-save-success")
    target_url = success_urls[0]

    submit_resptext = srcdir.joinpath("submit-response.html").read_text()
    expected_job_url = wb.url_for_jobstatus(submit_resptext)

    status_paths = iter(
        [
            srcdir.joinpath("status-0.json"),
            srcdir.joinpath("status-1.json"),
            srcdir.joinpath("status-9.json"),
            srcdir.joinpath("status-10.json"),
        ]
    )

    with responses.RequestsMock() as rsps:
        rsps.add(
            "POST",
            wb.url_for_savepage(target_url),
            body=submit_resptext,
            status=200,
            match=[
                responses.urlencoded_params_matcher(
                    {"url": target_url, "capture_all": "on"}
                )
            ],
        )

        rsps.add_callback(
            "GET",
            expected_job_url,
            callback=lambda req: (
                200,
                {},
                next(status_paths).read_text(),
            ),  # 2nd arg is a headers dict
        )

        yield rsps



@pytest.fixture
def too_soon_urls():
    target_url = "https://plainlanguage.gov/"
    expected_url = wb.url_for_snapshot(target_url, "20200904183020")
    return (target_url, expected_url)


@pytest.fixture
def too_soon_response(too_soon_urls):
    target_url = too_soon_urls[0]

    srcdir = FIXTURES_DIR.joinpath("job-save-too-soon")
    submit_resptext = srcdir.joinpath("submit-response.html").read_text()

    with responses.RequestsMock() as rsps:
        rsps.add(
            "POST",
            wb.url_for_savepage(target_url),
            body=submit_resptext,
            status=200,
            match=[
                responses.urlencoded_params_matcher(
                    {"url": target_url, "capture_all": "on"}
                )
            ],
        )

        rsps.add(
            "GET",
            wb.url_for_jobstatus(wb.extract_job_id(submit_resptext)),
            body=srcdir.joinpath("status-0.json").read_text(),
            status=200,
        )

        yield rsps
