import pytest
from click.testing import CliRunner
import responses
import requests

import json as jsonlib
from pathlib import Path

import pgark
import pgark.archivers.wayback as wb
from pgark.cli import main as maincli, check as checkcli, save as savecli


from tests.foofixtures import *

FIXTURES_DIR = Path("tests/fixtures/_old")

wb.DEFAULT_POLL_INTERVAL = 0
runner = CliRunner(mix_stderr=False)


def test_main_cli_default_hello():
    result = runner.invoke(maincli, [])
    assert result.exit_code == 0
    assert "Welcome to pgark" in result.output
    assert "--help" in result.output


def test_version_check():
    assert pgark.__version__ == runner.invoke(maincli, ["--version"]).output.strip()


####################
### check subcommand
@responses.activate
def test_check():
    """by default, returns just the available_url"""
    target_url = "www.whitehouse.gov/issues/immigration/"
    datatext = FIXTURES_DIR.joinpath("check/available-true.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.url_for_availability(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == data["archived_snapshots"]["closest"]["url"] + "\n"
    assert result.exit_code == 0


@responses.activate
def test_check_w_json():
    """by default, returns just the available_url"""
    target_url = "www.whitehouse.gov/issues/immigration/"
    datatext = FIXTURES_DIR.joinpath("check/available-true.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.url_for_availability(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url, "-j"])
    jd = jsonlib.loads(result.output)
    assert jd["request_meta"]["target_url"] == target_url
    ad = jd["server_payload"]["archived_snapshots"]["closest"]
    assert jd["snapshot_url"] == ad["url"]
    assert ad["available"] is True


@responses.activate
def test_check_not_available():
    """by default, returns just the available_url"""
    target_url = "http://danwin.com/is/poop"
    datatext = FIXTURES_DIR.joinpath("check/available-false.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.url_for_availability(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == "\n"


@responses.activate
def test_check_not_available_w_json():
    """by default, returns just the available_url"""
    target_url = "http://danwin.com/is/poop"
    datatext = FIXTURES_DIR.joinpath("check/available-false.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.url_for_availability(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url, "-j"])
    jd = jsonlib.loads(result.output)

    assert jd["request_meta"]["target_url"] == target_url
    assert not jd["snapshot_url"]
    assert jd["server_payload"]["archived_snapshots"] == {}


####################
### save subcommand



def test_cli_save(caplog, success_urls, save_success_response):
    target_url, expected_snap_url = success_urls

    result = runner.invoke(savecli, [target_url])
    assert result.output.strip() == expected_snap_url
    # let user know via mylogger.info that we're attempting a request to the given URL
    assert (
        f"Request endpoint: {wb.SAVE_ENDPOINT} target_url: {target_url}" in caplog.text
    )


def test_cli_save_with_json(caplog, success_urls, save_success_response):
    target_url, expected_snap_url = success_urls

    result = runner.invoke(savecli, [target_url, "-j", "--quiet"])
    meta = jsonlib.loads(result.output.strip())

    assert meta["snapshot_url"] == expected_snap_url
    assert meta["was_new_snapshot_created"] is True
    assert meta["request_meta"]["target_url"] == target_url



def test_cli_save_with_issues(caplog, too_soon_urls, too_soon_response):
    """
    for too_soon, should still get a snapshot_url, but also should get info level log output

    how to capture stderr in pytest:
    https://docs.pytest.org/en/stable/capture.html
    """
    target_url, expected_snap_url = too_soon_urls

    result = runner.invoke(savecli, [target_url, "--verbosity", "1"])

    assert result.output.strip() == expected_snap_url
    assert "too_soon" in caplog.text
    assert (
        "snapshot had been made 4 minutes and 18 seconds ago. We only allow new captures of the same URL every 20 minutes."
        in caplog.text
    )


#################################################### just basic flag stuff
def test_cli_version():
    result = runner.invoke(maincli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == pgark.__version__


############# verbosity testing
def test_cli_quietness(caplog, too_soon_urls, too_soon_response):
    target_url = too_soon_urls[0]
    result = runner.invoke(savecli, [target_url, "-q",])
    assert "too_soon" not in caplog.text
    assert "INFO" not in caplog.text


def test_cli_verbose_1(caplog, too_soon_urls, too_soon_response):
    target_url = too_soon_urls[0]
    result = runner.invoke(savecli, [target_url, "-v", "1"])
    assert "too_soon" in caplog.text
    assert "INFO" in caplog.text


def test_cli_verbose_2(caplog, too_soon_urls, too_soon_response):
    target_url = too_soon_urls[0]
    result = runner.invoke(savecli, [target_url, "-v", "2"])
    assert "DEBUG" in caplog.text


############################################################################
## error handling


@responses.activate
def test_check_unavailable(caplog):
    target_url = "http://example.com"
    responses.add(
        "GET", f"https://archive.org/wayback/available?url={target_url}", status=503,
    )
    result = runner.invoke(checkcli, [target_url,])

    assert "ERROR" in caplog.text
    assert "Received a not-OK HTTP status 503" in caplog.text
