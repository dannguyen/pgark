import pytest
from click.testing import CliRunner
import responses
import requests

import json as jsonlib
from pathlib import Path

import pgark
import pgark.archivers.wayback as wb
from pgark.cli import main as maincli, check as checkcli, save as savecli

EXAMPLES_DIR = Path("examples/web.archive.org/")


runner = CliRunner()


def test_main_cli_default_hello():
    result = runner.invoke(maincli, [])
    assert result.exit_code == 0
    assert "Welcome to pgark" in result.output
    assert "--help" in result.output


def test_version_check():
    assert pgark.__version__ == runner.invoke(maincli, ['--version']).output.strip()


####################
### check subcommand
@responses.activate
def test_check():
    """by default, returns just the available_url"""
    target_url = "www.whitehouse.gov/issues/immigration/"
    datatext = EXAMPLES_DIR.joinpath("check/available-true.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.availability_url(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == data["archived_snapshots"]["closest"]["url"] + "\n"


@responses.activate
def test_check_w_json():
    """by default, returns just the available_url"""
    target_url = "www.whitehouse.gov/issues/immigration/"
    datatext = EXAMPLES_DIR.joinpath("check/available-true.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.availability_url(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url, "-j"])
    assert result.output == datatext


@responses.activate
def test_check_not_available():
    """by default, returns just the available_url"""
    target_url = "http://danwin.com/is/poop"
    datatext = EXAMPLES_DIR.joinpath("check/available-false.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.availability_url(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == "\n"


@responses.activate
def test_check_not_available_w_json():
    """by default, returns just the available_url"""
    target_url = "http://danwin.com/is/poop"
    datatext = EXAMPLES_DIR.joinpath("check/available-false.json").read_text()
    data = jsonlib.loads(datatext)

    responses.add("GET", wb.availability_url(target_url), body=datatext, status=200)

    result = runner.invoke(checkcli, [target_url, "-j"])
    assert result.output == datatext


####################
### save subcommand


@pytest.mark.skip(
    reason="Implement unit test for wayback.snapshot first, before doing cli functional test"
)
def test_save():
    target_url = "https://plainlanguage.gov/"
    # mock the submit request
    # requests_mock.post(wb.savepage_url(target_url), data={'url': target_url, 'capture_all': 'on'}
    #                     text
    #                     )
