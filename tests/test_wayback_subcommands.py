import pytest
from freezegun import freeze_time
import responses

import json as jsonlib
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
@freeze_time("2020-09-01 14:30:55+0000")
@responses.activate
def test_check_success_and_available():
    target_url = "www.whitehouse.gov/issues/immigration/"
    resptext = EXAMPLES_DIR.joinpath("check/available-true.json").read_text()
    expected_snap_url = "http://web.archive.org/web/20200903230055/https://www.whitehouse.gov/issues/immigration/"
    responses.add(
        "GET", wb.url_for_availability(target_url), body=resptext,
    )

    answer, meta = wb.check_availability(target_url)

    assert answer == expected_snap_url
    assert meta.snapshot_url == expected_snap_url
    assert meta.is_success() is True
    assert meta.was_new_snapshot_created() is False
    assert meta.created_at.strftime("%Y-%m-%d %H:%M:%S%z") == "2020-09-01 14:30:55+0000"

    data = meta.to_dict()

    assert data["request_meta"]["target_url"] == target_url
    assert (
        data["server_payload"]["url"] == target_url
    )  # TODO: not sure if this is guranteed, if target_url ends up being redirected??

    ac = data["server_payload"]["archived_snapshots"]["closest"]
    assert ac["available"] is True
    assert ac["status"] == "200"
    assert ac["url"] == answer


@responses.activate
def test_check_success_but_not_available():
    target_url = "http://danwin.com/is/poop"
    resptext = EXAMPLES_DIR.joinpath("check/available-false.json").read_text()

    responses.add(
        "GET", wb.url_for_availability(target_url), body=resptext,
    )

    answer, meta = wb.check_availability(target_url)

    assert answer is None
    assert meta.snapshot_url is None
    assert meta.request_meta["target_url"] == target_url
    # TODO: not sure if this is guranteed, if target_url ends up being redirected??
    assert meta.server_payload["url"] == target_url

    assert meta.server_payload["archived_snapshots"] == {}


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
    url = wb.url_for_jobstatus(jid)
    resptext = EXAMPLES_DIR.joinpath("job-status-success.json").read_text()
    responses.add("GET", url, body=resptext)

    resp = wb.fetch_job_status(jid)
    assert resp["status"] == "success"


### snapshot_submit_request
@responses.activate
def test_snapshot_submit_request(session):
    target_url = "https://plainlanguage.gov/"
    save_url = wb.url_for_savepage(target_url)
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
    save_url = wb.url_for_savepage(target_url)
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

    with pytest.raises(ServerStatusError) as err:
        resp = wb.submit_snapshot_request(session, target_url, headers={})
    assert (
        f"Server status was NOT OK; returned 503 for: {save_url}" in err.value.args[0]
    )


##############################################
## test snapshot subcommand
@freeze_time("2020-09-01 14:30:55+0000")
@responses.activate
def test_snapshot_successful():
    #### fixture setup (todo: refactor?)
    srcdir = EXAMPLES_DIR.joinpath("job-save-success")

    target_url = "https://plainlanguage.gov/"
    save_url = wb.url_for_savepage(target_url)

    submit_resptext = srcdir.joinpath("submit-response.html").read_text()
    expected_job_id = wb.extract_job_id(submit_resptext)
    expected_job_url = wb.url_for_jobstatus(expected_job_id)

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
        "GET", expected_job_url, callback=_poll_callback,
    )

    answer, meta = wb.snapshot(target_url, user_agent="guy incognito", poll_interval=0)

    # make sure snapshot made the expected number of job status polls, plus the POST submit request
    assert len(responses.calls) == CURRENT_STATUS_ATTEMPT + 1

    # test return values
    assert type(answer) is str
    assert type(meta) is wb.TaskMeta
    assert meta.subcommand == "snapshot"
    assert meta.created_at.strftime("%Y-%m-%d %H:%M:%S%z") == "2020-09-01 14:30:55+0000"

    data = meta.to_dict()
    # test that answer is snapshot url
    assert (
        answer
        == wb.BASE_DOMAIN
        + "/web/"
        + data["server_payload"]["timestamp"]
        + "/"
        + target_url
    )

    # test data response
    assert data["subcommand"] == "snapshot"
    assert data["was_new_snapshot_created"] is True
    assert data["snapshot_url"] == answer
    assert data["request_meta"]["user_agent"] == "guy incognito"

    issues = data["issues"]
    assert issues["too_soon"] is False
    assert issues["too_many_during_period"] is False

    jd = data["server_payload"]
    assert jd["status"] == "success"
    assert jd["timestamp"] in data["snapshot_url"]

    # not sure if this is always the case...what happens if there's a redirect?
    assert jd["original_url"] == target_url


#########################
# warning situations
@responses.activate
def test_snapshot_too_soon():
    srcdir = EXAMPLES_DIR.joinpath("job-save-too-soon")
    target_url = "https://plainlanguage.gov/"

    submit_resptext = srcdir.joinpath("submit-response.html").read_text()

    responses.add(
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

    responses.add(
        "GET",
        wb.url_for_jobstatus(wb.extract_job_id(submit_resptext)),
        body=srcdir.joinpath("status-0.json").read_text(),
        status=200,
    )

    answer, meta = wb.snapshot(target_url, poll_interval=0)

    assert answer == meta.snapshot_url
    assert meta.subcommand == "snapshot"
    assert meta.was_new_snapshot_created() is False
    assert (
        meta.too_soon()
        == "The same snapshot had been made 4 minutes and 18 seconds ago. We only allow new captures of the same URL every 20 minutes."
    )


# @pytest.mark.skip(reason="Implement conditional branch after issue parsing")
@responses.activate
def test_snapshot_too_many_for_period():
    srcdir = EXAMPLES_DIR.joinpath("job-save-too-many-today")
    submit_resptext = srcdir.joinpath("submit-response.html").read_text()
    target_url = "https://nytimes.com/"

    responses.add(
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
    # mock request for availability URL
    responses.add(
        "GET",
        wb.url_for_availability(target_url),
        body=srcdir.joinpath("check-availability.json").read_text(),
    )

    answer, meta = wb.snapshot(target_url, poll_interval=0)

    assert answer == meta.snapshot_url
    assert meta.subcommand == "snapshot"
    assert meta.was_new_snapshot_created() == False
    assert (
        meta.too_many_during_period()
        == """This URL has been already captured 10 times today. Please email us at "info@archive.org" if you would like to discuss this more."""
    )

    # import pdb; pdb.set_trace()
    # server payload is the payload returned by availability API response
    assert meta.server_payload["archived_snapshots"]["closest"]["available"] is True


@freeze_time("2015-11-20")
@responses.activate
def test_save_unless_within_hours():
    target_url = "http://example.com/foo"
    payload = {
        "url": "http://example.com/foo",
        "archived_snapshots": {
            "closest": {
                "available": True,
                "status": "200",
                "timestamp": "20151120111111",
                "url": "http://web.archive.org/web/20151118111111/http://example.com/foo",
            }
        },
    }

    responses.add(
        "GET", wb.url_for_availability(target_url), body=jsonlib.dumps(payload),
    )

    answer, meta = wb.snapshot(target_url, within_hours=24)

    assert answer == meta.snapshot_url
    assert meta.request_meta["within_hours"] == 24
    assert meta.was_new_snapshot_created() is False
    assert meta.server_payload == payload  # brittle as hell!


@pytest.mark.skip(reason="just lazy")
@freeze_time("2015-11-20")
@responses.activate
def test_save_was_not_within_hours():
    pass
