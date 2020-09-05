import pytest
import responses

from pathlib import Path
import requests

from pgark.exceptions import *
import pgark.archivers.wayback as wb


EXAMPLES_DIR = Path("examples/web.archive.org/")


@pytest.fixture
def session():
    return requests.Session()


##############################################
## test check subcommand
@responses.activate
def test_check_success_and_available():
    target_url = "www.whitehouse.gov/issues/immigration/"
    resptext = EXAMPLES_DIR.joinpath("check/available-true.json").read_text()

    responses.add(
        "GET", wb.availability_url(target_url), body=resptext,
    )

    answer, data = wb.check_availability(target_url)

    assert (
        answer
        == "http://web.archive.org/web/20200903230055/https://www.whitehouse.gov/issues/immigration/"
    )
    assert (
        data["url"] == target_url
    )  # TODO: not sure if this is guranteed, if target_url ends up being redirected??
    df = data["archived_snapshots"]["closest"]
    assert df["available"] is True
    assert df["status"] == "200"
    assert df["url"] == answer


@responses.activate
def test_check_success_but_not_available():
    target_url = "http://danwin.com/is/poop"
    resptext = EXAMPLES_DIR.joinpath("check/available-false.json").read_text()

    responses.add(
        "GET", wb.availability_url(target_url), body=resptext,
    )

    answer, data = wb.check_availability(target_url)

    assert answer is None
    assert (
        data["url"] == target_url
    )  # TODO: not sure if this is guranteed, if target_url ends up being redirected??
    assert data["archived_snapshots"] == {}


@pytest.mark.skip(reason="TODO")
@responses.activate
def test_check_success_not_ok():
    """have no idea when this condition would happen, but let's test for it"""
    """should check for CLI error message, not raised error"""
    pass


########################################################################################
## test snapshot: subcommand helpers

### snapshot job_polling helpers
@responses.activate
def test_save_job_polling():
    jid = "af709a09-c909-4883-b6b3-7350f9be8d7c"
    url = wb.jobstatus_url(jid)
    resptext = EXAMPLES_DIR.joinpath("job-status-success.json").read_text()

    responses.add("GET", url, body=resptext)

    resp = wb.get_job_status(jid)
    assert resp["status"] == "success"


### snapshot_submit_request
@responses.activate
def test_snapshot_submit_request(session):
    target_url = "https://plainlanguage.gov/"
    save_url = wb.savepage_url(target_url)
    resptext = EXAMPLES_DIR.joinpath(
        "job-save-success/submit-response.html"
    ).read_text()

    responses.add(
        "POST",
        save_url,
        body=resptext,
        status=200,
        match=[
            responses.urlencoded_params_matcher(
                {"url": target_url, "capture_all": "on"}
            )
        ],
    )

    resp = wb.submit_snapshot_request(session, target_url, headers={})

    assert f'<h2 id="spn-title">Saving page {target_url}</h2>' in resp.text


@responses.activate
def test_snapshot_submit_request_not_ok(session):
    """not sure when this would happen, when server is down?"""
    target_url = "https://plainlanguage.gov/"
    save_url = wb.savepage_url(target_url)
    resptext = EXAMPLES_DIR.joinpath(
        "job-save-success/submit-response.html"
    ).read_text()
    responses.add(
        "POST",
        save_url,
        body=resptext,
        status=503,
        match=[
            responses.urlencoded_params_matcher(
                {"url": target_url, "capture_all": "on"}
            )
        ],
    )

    with pytest.raises(WaybackSubmitError) as err:
        resp = wb.submit_snapshot_request(session, target_url, headers={})
    assert (
        f"Server status was NOT OK; returned 503 for: {save_url}" in err.value.args[0]
    )


##############################################
## test snapshot subcommand
@responses.activate
def test_snapshot_successful():
    #### fixture setup (todo: refactor?)
    srcdir = EXAMPLES_DIR.joinpath("job-save-success")

    target_url = "https://plainlanguage.gov/"
    save_url = wb.savepage_url(target_url)

    submit_resptext = srcdir.joinpath("submit-response.html").read_text()
    expected_job_id = wb.extract_job_id(submit_resptext)
    expected_job_url = wb.jobstatus_url(expected_job_id)

    CURRENT_STATUS_ATTEMPT = 0
    status_paths = [
        srcdir.joinpath("status-0.json"),
        srcdir.joinpath("status-1.json"),
        srcdir.joinpath("status-2.json"),
        srcdir.joinpath("status-3.json"),
        srcdir.joinpath("status-9.json"),
        srcdir.joinpath("status-10.json"),
    ]

    def _poll_callback(request):
        nonlocal CURRENT_STATUS_ATTEMPT
        headers = {}
        resp_body = status_paths[CURRENT_STATUS_ATTEMPT].read_text()
        CURRENT_STATUS_ATTEMPT += 1
        return (200, headers, resp_body)

    #### mock responses
    responses.add(
        "POST",
        save_url,
        body=submit_resptext,
        status=200,
        match=[
            responses.urlencoded_params_matcher(
                {"url": target_url, "capture_all": "on"}
            )
        ],
    )

    responses.add_callback(
        "GET",
        expected_job_url,
        callback=_poll_callback,
    )

    answer, data = wb.snapshot(target_url, user_agent="guy incognito", poll_interval=0)

    # make sure snapshot made the expected number of job status polls, plus the POST submit request
    assert len(responses.calls) == CURRENT_STATUS_ATTEMPT + 1

    # test return values
    assert type(answer) is str
    assert type(data) is dict

    # test that answer is snapshot url
    assert (
        answer
        == wb.BASE_DOMAIN
        + "/web/"
        + data["last_job_status"]["timestamp"]
        + "/"
        + target_url
    )

    # test data response
    assert data["snapshot_status"] == "success"
    assert data["snapshot_url"] == answer
    assert data["snapshot_request"]["user_agent"] == "guy incognito"
    assert data["too_soon"] is False
    assert data["too_soon_message"] == ""
    assert data["job_id"] == expected_job_id
    assert data["job_url"] == expected_job_url

    jd = data["last_job_status"]
    assert jd["status"] == "success"
    assert jd["timestamp"] in data["snapshot_url"]

    # not sure if this is always the case...what happens if there's a redirect?
    assert jd["original_url"] == target_url


@responses.activate
def test_snapshot_too_soon():
    srcdir = EXAMPLES_DIR.joinpath("job-save-too-soon")
    target_url = 'https://plainlanguage.gov/'

    submit_resptext = srcdir.joinpath('submit-response.html').read_text()

    responses.add(
        "POST",
        wb.savepage_url(target_url),
        body=submit_resptext,
        status=200,
        match=[
            responses.urlencoded_params_matcher(
                {"url": target_url, "capture_all": "on"}
            )
        ],
    )

    responses.add(
        "GET",
        wb.jobstatus_url(wb.extract_job_id(submit_resptext)),
        body=srcdir.joinpath('status-0.json').read_text(),
        status=200,
    )

    answer, data = wb.snapshot(target_url, poll_interval=0)

    assert answer == data["snapshot_url"]
    assert data['snapshot_status'] == 'success'
    assert data['too_soon'] is True
    assert data['too_soon_message'] == 'The same snapshot had been made 4 minutes and 18 seconds ago. We only allow new captures of the same URL every 20 minutes.'

@pytest.mark.skip(reason="TODO")
@responses.activate
def test_snapshot_too_many():
    pass
