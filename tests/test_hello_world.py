"""just a place to test my actual testing libraries and such"""
import pytest
from click.testing import CliRunner
import responses

from pathlib import Path
import requests

import pgark
import pgark.__about__ as about


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
