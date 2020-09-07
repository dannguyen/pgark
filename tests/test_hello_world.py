"""just a place to test my actual testing libraries and such"""
import pytest
from click.testing import CliRunner
import responses

from pathlib import Path
import requests
import sys

import pgark
import pgark.__about__ as about

from pgark import mylogger


def test_version():
    assert pgark.__version__ == about.__version__


def test_exception_raisin_syntax():
    with pytest.raises(KeyError) as err:
        d = {"a": 9}
        e = d["hello"]

    assert "hello" == err.value.args[0]


@responses.activate
def test_post_responses():
    responses.add(
        "POST",
        "http://example.com",
        body="hello",
        status=200,
        match=[responses.urlencoded_params_matcher({"id": "good"})],
    )

    requests.post("http://example.com", data={"id": "good"})


@responses.activate
def test_hello_responses():
    """testing out responses library"""
    url = "http://asdf9899.com"
    responses.add("GET", url, body="boo!", status=200)
    resp = requests.get(url)
    assert resp.text == "boo!"


def test_mylog(caplog):
    # https://stackoverflow.com/questions/53125305/testing-logging-output-with-pytest
    print("just print")
    mylogger.critical("critical")
    assert "critical" in caplog.text
    assert "just print" not in caplog.text


def test_click_stderr():
    # https://github.com/pallets/click/issues/1193
    import click

    @click.command()
    def cliouts():
        click.echo("stdout")
        click.echo("myloggy", file=sys.stderr)

    runner = CliRunner(mix_stderr=False)

    result = runner.invoke(cliouts)

    assert result.output == "stdout\n"
    assert result.stdout == "stdout\n"
    assert result.stderr.strip() == "myloggy"


# @pytest.mark.skip(reason='wait')
# def test_click_mylogger():
#     import click
#     from pgark import mylogger

#     @click.command()
#     def clifoo():
#         click.echo("just echo")
#         mylogger.info('info')
#         mylogger.critical('critical')

#     runner = CliRunner(mix_stderr=False)

#     result = runner.invoke(clifoo)

#     import pdb; pdb.set_trace()
