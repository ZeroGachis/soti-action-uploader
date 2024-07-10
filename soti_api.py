import json
import requests
from urllib3.fields import RequestField
from urllib3.filepost import encode_multipart_formdata, choose_boundary


class SotiApi:
    APK_ALREADY_EXISTS = 1611

    def __init__(self, sotiapi, client_id, client_secret, username, password):
        self.soti_api_endpoint = sotiapi
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.metadata = {"DeviceFamily": "AndroidPlus"}
        self._token = None

    @property
    def token(self):
        if not self._token:
            self._token = self._get_token()
        return self._token
    
    @token.setter
    def token(self, value):
        self._token = value


    def upload_package(self, srcfile):
        body, content_type = self._encode_media_related(
            self.metadata,
            open(srcfile, "rb").read(),
            "application/vnd.android.application",
        )

        print("Upload packages.\n")
        resp = requests.post(
            f"{self.soti_api_endpoint}/api/packages",
            data=body,
            headers={
                "Content-Type": content_type,
                "Authorization": f"Bearer {self.token}",
            },
        )

        self._check_response(resp, "uploading APK")

    def auto_update_package(self, profile_name, package_name):

        if not profile_name or not package_name:
            raise Exception("Profile name or package name is empty.")

        package_id, version = self._get_package_id(package_name)
        profile_id = self._get_profile_id(profile_name)
        device_group_path = self._get_devices_profile_assignment(profile_id)
        self._update_profile_package(profile_id, package_id, version)
        self._assign_devices_to_profile(profile_id, device_group_path)


    def _get_token(self):
        print(f"get token")

        resp = requests.post(
            f"{self.soti_api_endpoint}/api/token",
            auth=(self.client_id, self.client_secret),
            data={
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
            },
            verify=True,
        )
        
        self._check_response(resp, "getting token")

        self.token = resp.json()["access_token"]

    def _encode_multipart_related(self, fields, boundary=None):
        if boundary is None:
            boundary = choose_boundary()

        body, _ = encode_multipart_formdata(fields, boundary)
        content_type = str("multipart/related; boundary=%s" % boundary)

        return body, content_type

    def _encode_media_related(self, metadata, media, media_content_type):
        rf1 = RequestField(
            name="metadata",
            data=json.dumps(metadata),
            headers={
                "Content-Type": "application/vnd.android.application.metadata+json"
            },
        )
        rf2 = RequestField(
            name="apk",
            data=media,
            headers={
                "Content-Type": media_content_type,
                "Content-Transfer-Encoding": "binary",
            },
        )
        return self._encode_multipart_related([rf1, rf2])

    def _get_profile_id(self, profile_name):
        print(f"get profile id")
        resp = requests.get(
            f"{self.soti_api_endpoint}/api/profiles",
            params={"NameContains": profile_name},
            headers={"Authorization": f"Bearer {self.token}"},
            verify=True,
        )

        self._check_response(resp, "getting profile id")
        return resp.json()[0]["ReferenceId"]

    def _get_package_id(self, package_name):
        print(f"get package id")
        resp = requests.get(
            f"{self.soti_api_endpoint}/api/packages",
            params={"packageName": package_name},
            headers={"Authorization": f"Bearer {self.token}"},
            verify=True,
        )
        self._check_response(resp, "getting package id")

        return resp.json()[0]["ReferenceId"], resp.json()[0]["LastVersion"]

    def _get_devices_profile_assignment(self, profile_id):
        print(f"get devices profile assign")
        resp = requests.get(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/assignment",
            headers={"Authorization": f"Bearer {self.token}"},
            verify=True,
        )

        self._check_response(resp, "getting devices profile assignment")
        return resp.json()

    def _update_profile_package(self, profile_id, package_id, last_version):
        print(f"update profile package")
        last_version.pop("$type")
        resp = requests.put(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/packages",
            json=[
                {
                    "ReferenceId": package_id,
                    "Version": last_version["Version"],
                    "ActivePackageVersions": [last_version],
                }
            ],
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            verify=True,
        )
        self._check_response(resp, "updating profile package")

    def _assign_devices_to_profile(self, profile_id, assigned_devices):
        print(f"assign devices to profile")
        assigned_devices = remove_dollar_keys(assigned_devices)
        assigned_devices["AssignmentOptions"]["PackageAssignmentOptions"][
            "ForceReinstallation"
        ] = True
        resp = requests.put(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/assignment",
            json=assigned_devices,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            verify=True,
        )
        self._check_response(resp, "assigning devices to profile")

    def _check_response(self, resp, action):
        if not (200 <= resp.status_code < 300):
            raise Exception(
                f"Issue was encountered while {action} in SOTI !\n {resp.json()} \n"
            )
        print(f"Status code OK: {resp.status_code} \n")


def remove_dollar_keys(obj):
    if isinstance(obj, dict):
        return {k: remove_dollar_keys(v) for k, v in obj.items() if "$" not in k}
    elif isinstance(obj, list):
        return [remove_dollar_keys(item) for item in obj]
    else:
        return obj
