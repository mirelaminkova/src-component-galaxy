#!/usr/bin/env python3
import argparse
from bioblend import galaxy

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--galaxy",
                    required=True,
                    dest="galaxy_url",
                    help="Target Galaxy instance URL/IP address (required "
                            "if not defined in the tools list file)",)
parser.add_argument("-a", "--apikey",
                    required=True,
                    dest="api_key",
                    help="Galaxy admin user API key (required if not "
                            "defined in the tools list file)",)
parser.add_argument("-e", "--email",
                    required=True,
                    dest="user_email",
                    help="The email of the user to be managed.",)
parser.add_argument("-d", "--delete",
                    action="store_true",
                    help="Whether to delete the user instead of creating it",)
args = parser.parse_args()

gi = galaxy.GalaxyInstance(url=args.galaxy_url, key=args.api_key)
uc = galaxy.users.UserClient(gi)
admin = uc.create_remote_user(user_email=args.user_email)

if args.delete:
    uc.delete_user(admin['id'])
else:
    api_key = uc.get_or_create_user_apikey(admin['id'])
    print(api_key)
