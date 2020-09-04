import click
import json as jsonlib

from collections.abc import Mapping
from typing import NoReturn

from pgark.mylog import mylogger
from pgark import wayback


def cliprint(obj) -> NoReturn:
    if isinstance(obj, Mapping):
        obj = jsonlib.dumps(obj, indent=2)
    click.echo(obj)


@click.group()
@click.option("-s", "--service", type=click.Choice(['wayback',]), default='wayback',
    help="The service, e.g. wayback, permacc")
# @click.option("-c", "--accept-cache", help="Accept and return cached URL", is_flag=True)
@click.option('-q', '--quiet', is_flag=True, help="Same as -v/--verbosity 0")
@click.option('-v', "--verbosity", type=click.IntRange(min=0, max=2), default=2,
    help="""\b
            Verbosity of log messages:
              0: Silence (except errors)
              1: Informational messages logged
              2: Verbose debug log messages
              """)

def main(service, quiet, verbosity):
    """
    Welcome to pgark
    """
    # TODO: actually allow service selection
    if quiet == True:
        mylogger.setLevel('ERROR')
    else:
        if verbosity == 2:
            mylogger.setLevel('DEBUG')
        elif verbosity == 1:
            mylogger.setLevel('INFO')
        elif verbosity == 0:
            mylogger.setLevel('ERROR')

    mylogger.debug('Logger level: ', mylogger.get_level())

@main.command()
@click.argument("url")
@click.option('-j', '--json', 'output_json', is_flag=True,
    help="""By default, this subcommand returns the URL of the most recent URL, or nothing at all. Set this flag to return
            the full JSON response""")

def check(url, output_json):
    answer, data = wayback.check_availability(url)
    cliprint(data) if output_json is True else cliprint(answer)


@main.command()
@click.argument("url")
@click.option("-u", "--user-agent", type=click.STRING, help="Specify a User-Agent header for the web request")
@click.option('-j', '--json', 'output_json', is_flag=True,
    help="""By default, this subcommand returns the URL of the most recent URL, or nothing at all. Set this flag to return
            the full JSON response""")

def save(url, user_agent, output_json):
    kwargs = {}
    if user_agent:
        kwargs['user_agent'] = user_agent

    answer, data = wayback.snapshot(url, **kwargs)

    if data['too_soon']:
        mylogger.info(f"{data['too_soon_message']}", label='Wayback Machine response')

    cliprint(data) if output_json is True else cliprint(answer)

if __name__ == "__main__":
    main()
