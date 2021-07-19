"""Script for interacting with API simply."""
# Standard Python Libraries
import configparser
from pprint import pprint

# Third-Party Libraries
import click
import requests


@click.group()
@click.pass_context
def cli(ctx):
    """CLI."""
    return


def main():
    """Run main."""
    cli.add_command(request)
    cli.add_command(configure)
    cli()
    return


@click.command("request")
@click.option(
    "--method", required=True, prompt=True, type=click.Choice(["GET", "DELETE"])
)
@click.option("--path", required=True, prompt=True)
def request(method, path):
    """Request."""
    try:
        config = get_config()
        path = f"{config['url']}/{path}/"
        auth = get_auth(config["token"])
    except Exception:
        print("CLI not configured, run configure")
        return

    if method == "GET":
        resp = requests.get(path, headers=auth)
        print(f"Server responsed with code {resp.status_code}")
        try:
            pprint(resp.json())
        except Exception:
            print(resp.text)
    elif method == "DELETE":
        resp = requests.delete(path, headers=auth)
        print(f"Server responsed with code {resp.status_code}")


@click.command("configure")
@click.option("--url", required=True, prompt=True)
@click.option("--token", required=True, prompt=True)
def configure(url, token):
    """Configure."""
    config = configparser.ConfigParser()
    config["DEFAULT"] = {"url": url, "token": token}
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def get_config():
    """Get config for API."""
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["DEFAULT"]


def get_auth(token):
    """Get auth header."""
    return {"Authorization": f"Bearer {token}"}


if __name__ == "__main__":
    main()
