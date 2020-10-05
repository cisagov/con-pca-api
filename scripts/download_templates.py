import requests
import argparse
import json

parser = argparse.ArgumentParser(description="Download templates from an api url")

parser.add_argument(
    "--url",
    help="Url for the load balancer",
    default="https://con-pca-stage-public-570261247.us-east-1.elb.amazonaws.com:8043",
)
parser.add_argument(
    "--token",
    help="Access token to authenticate. Can be found in local storage after logging in with browser.",
)
parser.add_argument(
    "--outfile", help="File to output json to", default="templates.json"
)

args = parser.parse_args()

resp = requests.get(
    f"{args.url}/api/v1/templates/",
    headers={"Authorization": f"Bearer {args.token}"},
)

with open(args.outfile, "w") as f:
    f.write(json.dumps(resp.json(), indent=4))
