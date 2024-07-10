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
        self.token = ""
        self.metadata = {"DeviceFamily": "AndroidPlus"}

    def upload_package(self, srcfile):
        self._ensure_token()
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
        print(resp.status_code, "\n")

        if resp.status_code == 422:
            if resp.json()["ErrorCode"] == self.APK_ALREADY_EXISTS:
                print("APK already exists in SOTI")
                return

        print("Message: %s" % resp.json())

        self._check_response(resp, "uploading APK")

    def auto_update_package(self, profile_name, package_name):
        self._ensure_token()

        if not profile_name or not package_name:
            raise Exception("Profile name or package name is empty.")

        package_id, version = self._get_package_id(package_name)
        profile_id = self._get_profile_id(profile_name)
        device_group_path = self._get_devices_profile_assignment(profile_id)
        self._update_profile_package(profile_id, package_id, version)
        self._assign_devices_to_profile(profile_id, device_group_path)

    def _ensure_token(self):
        if not self.token:
            self._get_token()

    def _get_token(self):
        with requests.session() as c:
            resp = c.post(
                f"{self.soti_api_endpoint}/api/token",
                auth=(self.client_id, self.client_secret),
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                },
                verify=True,
            )
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

        print(f"Status code OK: {resp.status_code}")
        return resp.json()[0]["ReferenceId"], resp.json()[0]["LastVersion"]["Version"]

    def _get_devices_profile_assignment(self, profile_id):
        print(f"get devices profile assign")
        resp = requests.get(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/assignment",
            headers={"Authorization": f"Bearer {self.token}"},
            verify=True,
        )

        self._check_response(resp, "getting devices profile assignment")

        return resp.json()["TargetDeviceGroups"][0]["DeviceGroupPath"]

    def _update_profile_package(self, profile_id, package_id, version):
        print(f"update profile package")
        resp = requests.put(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/packages",
            data=[{"ReferenceId": package_id, "Version": version}],
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            verify=True,
        )

        self._check_response(resp, "updating profile package")

        print(f"Status code OK: {resp.status_code}")

        return resp.json()[0]["ReferenceId"]

    def _assign_devices_to_profile(self, profile_id, device_group_path):
        print(f"assign devices to profile")
        resp = requests.post(
            f"{self.soti_api_endpoint}/api/profiles/{profile_id}/assignment/targetDeviceGroups",
            data=[device_group_path],
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}",
            },
            verify=True,
        )

        self._check_response(resp, "assigning devices to profile")

        print(f"Status code OK: {resp.status_code}")

    def _check_response(self, resp, action):
        if not (200 <= resp.status_code < 300):
            raise Exception(
                f"Issue was encountered while {action} in SOTI !\n {resp.json()}"
            )
