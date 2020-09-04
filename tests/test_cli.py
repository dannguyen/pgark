import pytest
from click.testing import CliRunner
import responses
import requests

import json as jsonlib
from pathlib import Path

from pgark.cli import main as maincli, check as checkcli, save as savecli
import pgark.wayback as wb


runner = CliRunner()


def test_main_hello():
    result = runner.invoke(maincli, [])
    assert result.exit_code == 0
    assert 'Welcome to pgark' in result.output
    assert '--help' in result.output


@responses.activate
def test_hello_responses():
    """testing out responses library"""
    url = 'http://asdf9899.com'
    responses.add('GET',
                  url,
                  body='boo!',
                  status=200)
    resp = requests.get(url)
    assert resp.text == 'boo!'




####################
### check subcommand
def test_check(requests_mock):
    """by default, returns just the available_url"""
    target_url = 'www.whitehouse.gov/issues/immigration/'
    datatext = Path('examples/web.archive.org/available-true.json').read_text()
    data = jsonlib.loads(datatext)

    requests_mock.get(wb.AVAILABLE_ENDPOINT + target_url, text=datatext)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == data['archived_snapshots']['closest']['url'] + '\n'



@responses.activate
def test_check_w_json():
    """by default, returns just the available_url"""
    target_url = 'www.whitehouse.gov/issues/immigration/'
    datatext = Path('examples/web.archive.org/available-true.json').read_text()
    data = jsonlib.loads(datatext)

    responses.add(responses.GET, wb.AVAILABLE_ENDPOINT + target_url,
                  body=datatext,
                  status=200)

#    requests_mock.get(wb.AVAILABLE_ENDPOINT + target_url, text=datatext)

    result = runner.invoke(checkcli, [target_url, '-j'])
    assert result.output == datatext


def test_check_not_available(requests_mock):
    """by default, returns just the available_url"""
    target_url = 'http://danwin.com/is/poop'
    datatext = Path('examples/web.archive.org/available-false.json').read_text()
    data = jsonlib.loads(datatext)

    requests_mock.get(wb.AVAILABLE_ENDPOINT + target_url, text=datatext)

    result = runner.invoke(checkcli, [target_url])
    assert result.output == "\n"


def test_check_not_available_w_json(requests_mock):
    """by default, returns just the available_url"""
    target_url = 'http://danwin.com/is/poop'
    datatext = Path('examples/web.archive.org/available-false.json').read_text()
    data = jsonlib.loads(datatext)

    requests_mock.get(wb.AVAILABLE_ENDPOINT + target_url, text=datatext)

    result = runner.invoke(checkcli, [target_url, '-j'])
    assert result.output == datatext



####################
### save subcommand

@pytest.mark.skip(reason="Implement unit test for wayback.snapshot first, before doing cli functional test")
def test_save(requests_mock):
    target_url = 'https://plainlanguage.gov/'
    # mock the submit request
    # requests_mock.post(wb.savepage_url(target_url), data={'url': target_url, 'capture_all': 'on'}
    #                     text
    #                     )
