import sys
import time
import argparse
import textwrap
from art import tprint

from .dribbble_user import *

__version__ = "0.0.1"


t1 = time.perf_counter()


def main(argv=None):
    argv = sys.argv if argv is None else argv
    argparser = argparse.ArgumentParser(
        prog="drbl_py",
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent(
            """
            Dribbble-py 0.0.1\n
            Program to scrape dribbble user information\n
             """
        ),
        epilog="""
        Example usage
        -------------\n
        Download  info about a user.\n
            $ drbl_py -u JohnDoe\n

        Download info about a user to a custom JSON file.\n
            $ drbl_py -u JohnDoe -j John\n


        """,
    )

    # User Arguments
    # ---

    argparser.add_argument(
        "-u",
        "--username",
        help=textwrap.dedent(
            """Enter username to scrape.\n
                             """
        ),
        dest="username",
    )
    argparser.add_argument(
        "-m",
        "--get-metadata",
        help=textwrap.dedent(
            """Get metadata about every user shot.\nTakes longer to scrape.\nDefault = No metadata about user shots

                             """
        ),
        action="store_true",
    )

    argparser.add_argument(
        "-j",
        "--json-file",
        help=textwrap.dedent(
            """Name of output JSON filename.\nDefault = username.json\n
            """
        ),
        dest="json_file",
    )

    argparser.add_argument("--version", action="version", version="%(prog)s 0.0.1")
    args = argparser.parse_args()

    if args.username:
        # Set json filename
        if args.json_file is None:
            json_file = args.username + ".json"

        elif args.json_file:
            json_file = args.json_file + ".json"

        tprint("DRIBBBLE-PY")
        print("version {}".format(__version__))
        if args.get_metadata:
            try:
                dribbble_user = DribbbleUser(args.username, json_file)
                dribbble_user.check_user()
                dribbble_user.run_nursery_with_metadata_scraper()
                dribbble_user.export_to_json()

                t2 = time.perf_counter()
                print(f"\nScraping took {t2-t1:0.2f} second(s)...\n")
            except KeyboardInterrupt:
                print("Exiting dribbble-py...\n")
                sys.exit(0)
        else:
            try:
                dribbble_user = DribbbleUser(args.username, json_file)
                dribbble_user.check_user()
                dribbble_user.run_nursery_without_metadata_scraper()
                dribbble_user.export_to_json()

                t2 = time.perf_counter()
                print(f"\nScraping took {t2-t1:0.2f} second(s)...\n")

            except KeyboardInterrupt:
                print("Exiting dribbble-py...\n")
                sys.exit(0)
