import unittest
from unittest.mock import patch, mock_open, MagicMock
from soti_api import SotiApi


class TestSotiApi(unittest.TestCase):

    def setUp(self):
        self.soti_api = SotiApi(
            "http://fakeapi.com",
            "fake_client_id",
            "fake_client_secret",
            "fake_username",
            "fake_password",
        )

    @patch("soti_api.requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"fake_apk_data")
    @patch("soti_api.SotiApi._get_token")
    def test_upload_package(self, mock_get_token, mock_file, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": "success"}
        mock_get_token.return_value = "fake_token"

        self.soti_api.upload_package("fake_apk_path")

        mock_file.assert_called_once_with("fake_apk_path", "rb")
        mock_post.assert_called_once()

        assert (
            mock_post.call_args[1]["headers"]["Authorization"]
            == f"Bearer {self.soti_api.token}"
        )
        assert mock_post.return_value.status_code == 200
        assert mock_post.return_value.json() == {"message": "success"}

    @patch("soti_api.SotiApi._get_token")
    def test_upload_package_failure_with_no_file(self, mock_get_token):
        mock_get_token.return_value = "fake_token"
        with self.assertRaises(Exception) as context:
            self.soti_api.upload_package("fake_apk_path")

        assert "[Errno 2] No such file or directory: 'fake_apk_path'" == str(
            context.exception
        )

    @patch("soti_api.SotiApi._get_token")
    def test_auto_update_package_failure_with_empty_profile_name_or_package_name(
        self, mock_get_token
    ):
        mock_get_token.return_value = "fake_token"

        with self.assertRaises(
            Exception,
        ) as context:
            self.soti_api.auto_update_package("", "")

        assert "Profile name or package name is empty." == str(context.exception)

    @patch("soti_api.requests.get")
    def test_get_profile_id_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"ReferenceId": "fake_profile_id"}]
        self.soti_api.token = "fake_token"
        profile_id = self.soti_api._get_profile_id("fake_profile_name")

        mock_get.assert_called_once_with(
            "http://fakeapi.com/api/profiles",
            params={"NameContains": "fake_profile_name"},
            headers={"Authorization": "Bearer fake_token"},
            verify=True,
        )
        assert profile_id == "fake_profile_id"

    @patch("soti_api.requests.get")
    @patch("soti_api.SotiApi._get_token", return_value="fake_token")
    def test_get_profile_id_failure(self, _, mock_get):
        mock_get.return_value.status_code = 404
        mock_get.return_value.json.return_value = {"error": "Profile not found"}

        with self.assertRaises(
            Exception,
        ) as context:
            self.soti_api._get_profile_id("fake_profile_id")

        assert """Issue was encountered while getting profile id in SOTI !
 {'error': 'Profile not found'} \n""" == str(
            context.exception
        )

    @patch("soti_api.requests.get")
    def test_get_package_id_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [
            {"ReferenceId": "fake_package_id", "LastVersion": {"Version": "1.0.0"}}
        ]
        self.soti_api.token = "fake_token"
        package_id, version = self.soti_api._get_package_id("fake_package_name")

        mock_get.assert_called_once_with(
            "http://fakeapi.com/api/packages",
            params={"packageName": "fake_package_name"},
            headers={"Authorization": "Bearer fake_token"},
            verify=True,
        )
        assert package_id == "fake_package_id"
        assert version == {'Version': '1.0.0'}

    @patch("soti_api.requests.get")
    def test_get_devices_profile_assignment_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "TargetDeviceGroups": [{"DeviceGroupPath": "list/of/device/groups"}]
        }
        self.soti_api.token = "fake_token"
        devices_path = self.soti_api._get_devices_profile_assignment("fake_profile_id")

        mock_get.assert_called_once_with(
            "http://fakeapi.com/api/profiles/fake_profile_id/assignment",
            headers={"Authorization": "Bearer fake_token"},
            verify=True,
        )
        assert devices_path == {'TargetDeviceGroups': [{'DeviceGroupPath': 'list/of/device/groups'}]}

    @patch("soti_api.requests.put")
    def test_update_profile_package_success(self, mock_put):
        mock_put.return_value.status_code = 200
        mock_put.return_value.json.return_value = [
            {"ReferenceId": "new_fake_profile_id"}
        ]
        self.soti_api.token = "fake_token"

        self.soti_api._update_profile_package(
            "fake_profile_id",  "fake_package_id", {"Version": "1.0.0", "$type": "PackageVersion"}
        )

        mock_put.assert_called_once_with(
            "http://fakeapi.com/api/profiles/fake_profile_id/packages",
            json=[{"ReferenceId": "fake_package_id", "Version": "1.0.0", "ActivePackageVersions": [{"Version": "1.0.0"}]}],
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer fake_token",
            },
            verify=True,
        )

    @patch("soti_api.requests.put")
    def test_assign_devices_to_profile_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": "success"}
        self.soti_api.token = "fake_token"

        self.soti_api._assign_devices_to_profile(
            "fake_profile_id", {"message": "success", "AssignmentOptions": {"PackageAssignmentOptions": {"ForceReinstallation": False}}}
        )

        mock_post.assert_called_once_with(
            "http://fakeapi.com/api/profiles/fake_profile_id/assignment",
            json={"message": "success", "AssignmentOptions": {"PackageAssignmentOptions": {"ForceReinstallation": True}}},
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer fake_token",
            },
            verify=True,
        )
