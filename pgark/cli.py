import click
import json
from pgark import wayback


@click.group()
@click.option("-s", "--service", type=click.STRING, default='wayback', help="The service, e.g. wayback, permacc")
# @click.option("-c", "--accept-cache", help="Accept and return cached URL", is_flag=True)
# --quiet/-q for quiet levels
def main(service):
    """
    Welcome to pgark
    """
    # TODO: actually allow service selection
    pass

@main.command()
@click.argument("url")
def check(url):
    data = wayback.check_availability(url)
    click.echo(json.dumps(data, indent=2))




@main.command()
@click.argument("url")
@click.option("-u", "--user-agent", type=click.STRING, help="Specify a User-Agent header for the web request")
def save(url, user_agent):
    kwargs = {}
    if user_agent:
        kwargs['user_agent'] = user_agent

    data = wayback.snapshot(url, **kwargs)
    click.echo(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
