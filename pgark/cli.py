import click
from pgark import wayback

@click.group()
@click.option("-s", "--service", type=click.STRING, default='wayback', help="The service, e.g. wayback, permacc")
# @click.option("-c", "--accept-cache", help="Accept and return cached URL", is_flag=True)
# --quiet/-q for quiet levels
def main(url, service):
    """
    Welcome to pgark
    """
    # TODO: actually allow service selection
    pass


@main.command()
@click.argument("url")
@click.option("-u", "--user-agent", type=click.STRING, help="Specify a User-Agent header for the web request")
def save(url, user_agent):
    kwargs = {}
    if user_agent:
        kwargs['user_agent'] = user_agent



    wayback.snapshot(url, **kwargs)

if __name__ == "__main__":
    main()
