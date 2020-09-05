import click
from collections.abc import Mapping
from datetime import datetime, timezone
import json as jsonlib
from typing import NoReturn

import pgark
from pgark.mylog import mylogger
from pgark.archivers import wayback

OPTIONS_COMMON = [
    click.option(
        "-s",
        "--service",
        type=click.Choice(["wayback",]),
        default="wayback",
        help="The service, e.g. wayback, permacc",
    ),
]

OPTIONS_OUTPUT = [
    click.option(
        "-j",
        "--json",
        "output_json",
        is_flag=True,
        help="""By default, this subcommand returns a snapshot URL if successful, and nothing if not successful. Set this flag to return
            the full JSON response""",
    ),
    click.option("-q", "--quiet", is_flag=True, help="Same as -v/--verbosity 0"),
    click.option(
        "-v",
        "--verbosity",
        type=click.IntRange(min=0, max=2),
        default=2,
        help="""\b
                Verbosity of log messages:
                  0: Silence (except errors)
                  1: Informational messages logged
                  2: Verbose debug log messages
                  """,
    ),
]


def _callback_print_version(ctx, param, value) -> NoReturn:
    """
    https://click.palletsprojects.com/en/3.x/options/#callbacks-and-eager-options
    """
    if not value or ctx.resilient_parsing:
        return
    cliprint(pgark.__version__)
    ctx.exit()


def _set_verbosity(**kwargs):
    """TODO: should be decorator?"""
    if kwargs.get("quiet") is True:
        mylogger.setLevel("ERROR")
    else:
        vb = kwargs.get("verbosity")
        if vb == 2:
            mylogger.setLevel("DEBUG")
        elif vb == 1:
            mylogger.setLevel("INFO")
        elif vb == 0:
            mylogger.setLevel("ERROR")

    mylogger.debug("Logger level: ", mylogger.get_level())


def add_options(*option_sets):
    def _decorate(func):
        for options in reversed(option_sets):
            for opt in reversed(options):
                func = opt(func)
        return func

    return _decorate


def cliprint(obj) -> NoReturn:
    if isinstance(obj, Mapping):
        obj = jsonlib.dumps(obj, indent=2)
    click.echo(obj)


@click.group()
@click.option(
    "-v",
    "--version",
    callback=_callback_print_version,
    is_eager=True,
    is_flag=True,
    help="Print the version of pgark",
)
def main(**kwargs):
    """
    Welcome to pgark
    """
    if kwargs.get("version"):
        cliprint(pgark.__version__)
        return


@main.command()
@add_options(OPTIONS_COMMON, OPTIONS_OUTPUT)
@click.argument("url")
def check(url, **kwargs):
    """
    Check if there is a snapshot of [URL] on the [-s/--service]. Returns the most recent snapshot URL if so; otherwise, returns nothing
    """
    _set_verbosity(**kwargs)

    answer, data = wayback.check_availability(url)
    cliprint(data) if kwargs["output_json"] is True else cliprint(answer)


@main.command()
@add_options(OPTIONS_COMMON, OPTIONS_OUTPUT)
@click.argument("url")
@click.option(
    "-wt", "--within", "within_hours",
    type=click.INT,
    help="Check the [service] for the most recent snapshot; if it is `--within [HOURS]` from right now, then *do not* create a new snapshot. Recent snapshot URL and data payload returned similar to using the `check` subcommand",
)
@click.option(
    "-u",
    "--user-agent",
    type=click.STRING,
    help="Specify a User-Agent header for the web request",
)
def save(url, within_hours, user_agent, **kwargs):
    """
    Attempt to save a snapshot of [URL] using the [-s/--service]. Returns the snapshot URL if successful
    """
    _set_verbosity(**kwargs)

    # todo: this should be part of wayback.save, as opposed to the CLI
    if within_hours:
        mylogger.debug("Checking availability of most recent snapshot since {within_hours} hours")
        recent_url, rdata = wayback.check_availability(url)
        if recent_url:
            mylogger.debug(f"Most recent snapshot available: {recent_url}")
            dt_recent = wayback.extract_wayback_datetime(recent_url)
            delta_seconds = (pgark.get_today() - dt_recent).seconds
            delta_hours = delta_seconds / (60 * 60)

            mylogger.debug(f"Recent snapshot within: {delta_seconds} seconds, i.e. {delta_hours} hours")

            # thius definitely needs to be refactored into wayback.save -- cli shoul dhave
            # no knowledge of this data object
            if delta_hours < within_hours:
                mylogger.debug(f"Recent snapshot URL within threshold of {within_hours} hours; returning availability response")
                data = {
                        'was_new_snapshot_created': False,
                        'snapshot_url': recent_url,
                        'target_url': url,
                        'issues': {},
                        'server_payload': rdata,
                     }
                answer = data['snapshot_url']
                #TODO: dry this out
                if kwargs["output_json"]:
                    cliprint(data)
                else:
                    cliprint(answer)
                return ## refactor this later


            else:
                mylogger.debug("Recent snapshot URL did not meet threshold of {within_hours} hours, proceeding with normal save")

    # if we get to here, we proceed as normal, and assume that recent_snapshot did not
    # meet within-hours cutoff, if it was even specified

    snapshot_kwargs = {}
    if user_agent:
        snapshot_kwargs["user_agent"] = user_agent

    answer, data = wayback.snapshot(url, **snapshot_kwargs)
    for i_key, i_value in data["issues"].items():
        if i_value:
            mylogger.info(f"{i_key}: {i_value}", label="Wayback Machine notice")

    if kwargs["output_json"]:
        cliprint(data)
    else:
        cliprint(answer)


if __name__ == "__main__":
    main()
