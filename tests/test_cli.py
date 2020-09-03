import pytest
import click
from click.testing import CliRunner
from pathlib import Path

from pgark.cli import main as maincli

runner = CliRunner()


def test_main_hello():
    result = runner.invoke(maincli, [])
    assert result.exit_code == 0
    assert 'Welcome to pgark' in result.output
    assert '--help' in result.output
