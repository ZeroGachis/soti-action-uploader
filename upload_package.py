import argparse

from soti_api import SotiApi

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Upload apk on mobi control.")
    parser.add_argument("sotiapi", help="Uri soti api endpoint.", type=str)
    parser.add_argument("srcfile", help="Apk file path", type=str)
    parser.add_argument("client_id", help="Soti api client id", type=str)
    parser.add_argument("client_secret", help="Soti api client secret.", type=str)
    parser.add_argument("username", help="Mobi control username.", type=str)
    parser.add_argument("password", help="Mobi control password.", type=str)
    parser.add_argument(
        "--auto-update",
        help="Auto update device's profile package.",
        action="store_true",
        default=False,
    )
    parser.add_argument("--profile-name", help="Profile name.", type=str, default="")
    parser.add_argument("--package-name", help="Package name.", type=str, default="")
    args = parser.parse_args()

    soti_api = SotiApi(
        args.sotiapi, args.client_id, args.client_secret, args.username, args.password
    )

    soti_api.upload_package(args.srcfile)
    if args.auto_update:
        soti_api.auto_update_package(args.profile_name, args.package_name)
