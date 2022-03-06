from unittest import IsolatedAsyncioTestCase
import unittest
import sys


sys.path.append("../dribbble_py")
from dribbble_py import *


class TestDribbbleUser(IsolatedAsyncioTestCase):
    def test_check_user(self):
        print("Testing check user...")
        drbl_usr = DribbbleUser("theosm", None)
        drbl_usr.check_user()
        possible_outcomes = ["Yes", "No"]
        self.assertTrue(
            any(
                outcome
                for outcome in possible_outcomes
                if (outcome in drbl_usr.dribbble_user_data["user_exists"])
            )
        )

    async def test_scrape_main_page(self):
        print("Testing scrape_main_page... ")
        drbl_usr = DribbbleUser("TonyBabel", None)
        await drbl_usr.scrape_main_page()
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["projects_count"], 0)
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["shots_count"], 0)
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["collections_count"], 0)
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["liked_shots"], 0)
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["members_count"], 0)

    async def test_scrape_about_page(self):
        print("Testing scrape_about_page... ")
        drbl_usr = DribbbleUser("TonyBabel", None)
        await drbl_usr.scrape_about_page()
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["followers"], 0)
        self.assertGreaterEqual(drbl_usr.dribbble_user_data["following"], 0)


if __name__ == "__main__":
    unittest.main()
