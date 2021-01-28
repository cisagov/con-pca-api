"""Download Templates from API."""
# Standard Python Libraries
import argparse
import json

# Third-Party Libraries
import requests

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

templates = resp.json()
print(len(templates))
print(templates[0].keys())
for template in templates:
    template.pop("template_uuid")
    template.pop("created_by")
    template.pop("cb_timestamp")
    template.pop("last_updated_by")
    template.pop("lub_timestamp")
    template.pop("landing_page_uuid")

with open(args.outfile, "w") as f:
    f.write(json.dumps(templates, indent=4))
