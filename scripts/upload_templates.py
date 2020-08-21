import requests
import argparse
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description="Download templates from an api url")

parser.add_argument(
    "--url",
    help="Url for the load balancer",
    default="https://con-pca-dev-public-1660475225.us-east-1.elb.amazonaws.com:8043",
)
parser.add_argument(
    "--token",
    help="Access token to authenticate. Can be found in local storage after logging in with browser.",
)
parser.add_argument(
    "--jsonfile", help="File to output json to", default="templates.json"
)

parser.add_argument("--landing", help="Landing Page UUID")

args = parser.parse_args()

headers = {"Authorization": f"Bearer {args.token}"}


# Get templates from environment to upload to
resp = requests.get(f"{args.url}/api/v1/templates/", headers=headers, verify=False)

print(resp)

old_templates = resp.json()

with open(args.jsonfile, "r") as f:
    new_templates = json.load(f)

print(f"Total New Templates = {len(new_templates)}")


changes = 0
additions = 0

for new_template in new_templates:
    # Find existing templates with same name
    old_template = list(
        filter(lambda x: x["name"] == new_template["name"], old_templates)
    )

    new_template["landing_page_uuid"] = args.landing

    if old_template:
        old_template = old_template[0]
        resp = requests.patch(
            f"{args.url}/api/v1/template/{old_template['template_uuid']}/",
            headers=headers,
            verify=False,
            json=new_template,
        )

        changes += 1

    else:
        resp = requests.post(
            f"{args.url}/api/v1/templates/",
            headers=headers,
            verify=False,
            json=new_template,
        )
        additions += 1

    if resp.status_code not in (202, 200):
        print(resp.text)
        print(f"{old_template=}")
        print(f"{new_template=}")

print(f"Total Changes = {changes}")
print(f"Total Additions = {additions}")
