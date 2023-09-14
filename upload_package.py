import argparse
import json
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata, choose_boundary
import requests


parser = argparse.ArgumentParser("Upload apk on mobi control.")
parser.add_argument("sotiapi", help="Uri soti api endpoint.", type=str)
parser.add_argument("srcfile", help="Apk file path", type=str)
parser.add_argument("client_id", help="Soti api client id", type=str)
parser.add_argument("client_secret", help="Soti api client secret.", type=str)
parser.add_argument("username", help="Mobi control username.", type=str)
parser.add_argument("password", help="Mobi control password.", type=str)
args = parser.parse_args()

sotiapi = args.sotiapi
srcfile = args.srcfile
client_id = args.client_id
client_secret = args.client_secret
username = args.username
password = args.password


def encode_multipart_related(fields, boundary=None):
    if boundary is None:
        boundary = choose_boundary()

    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str("multipart/related; boundary=%s" % boundary)

    return body, content_type


def encode_media_related(metadata, media, media_content_type):
    rf1 = RequestField(
        name="metadata",
        data=json.dumps(metadata),
        headers={"Content-Type": "application/vnd.android.application.metadata+json"},
    )
    rf2 = RequestField(
        name="apk",
        data=media,
        headers={
            "Content-Type": media_content_type,
            "Content-Transfer-Encoding": "binary",
        },
    )
    return encode_multipart_related([rf1, rf2])


metadata = {"DeviceFamily": "AndroidPlus"}
token = ""

print("Getting token.\n")
with requests.session() as c:
    resp = c.post(
        f"{sotiapi}/api/token",
        auth=(client_id, client_secret),
        data={"grant_type": "password", "username": username, "password": password},
        verify=True,
    )
    token = resp.json()["access_token"]

body, content_type = encode_media_related(
    metadata,
    open(srcfile, "rb").read(),
    "application/vnd.android.application",
)

print("Upload pakages.\n")
resp = requests.post(
    f"{sotiapi}/api/packages",
    data=body,
    headers={"Content-Type": content_type, "Authorization": f"Bearer {token}"},
    verify=True,
)
print(resp.status_code, "\n")
print("Message: %s" % resp.json())

if not (200 <= resp.status_code < 300):
    raise Exception("Issue was encountered while uploading APK on SOTI !")
