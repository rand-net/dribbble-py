import chompjs
import re
import json
import trio
import httpx
from datetime import datetime
from bs4 import BeautifulSoup
import sys
from dribbble_py.silent_selector import SilentSelector
from dribbble_py.utils import int_k, get_redirect_url, string_to_number

sys.path.append("../dribbble_py")


DRIBBBLE_URL = "https://dribbble.com"


class DribbbleUser:
    """
    Scrapes available data of a dribbble user

    Arguments:
        username: string
        json_file: string

    """

    def __init__(self, username: str, json_file: str):
        self.username = username

        # Set JSON file name
        if json_file is None:
            self.jsonf_file = username
        elif json_file is not None:
            self.json_file = json_file
        self.dribbble_user_data = {}

        self.join_date_format = "%b %Y"
        self.shot_published_date_format = "%b %d, %Y"
        self.preferred_time_format = "%Y-%m-%d"

        self.shots_per_page = 8
        self.project_shots_per_page = 8
        self.members_per_page = 6

        self.scraper_header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4690.0 Safari/537.36/QInxREvS-38"
        }
        # Construct URLs for various pages
        self.user_pages = {
            "main": "/",
            "shots": "/shots",
            "about": "/about",
            "projects": "/projects",
            "goods": "/goods",
            "collections": "/collections",
            "members": "/members?page=",
        }

        self.user_pages = {
            key: DRIBBBLE_URL + "/" + self.username + value
            for key, value in self.user_pages.items()
        }

    def check_user(self) -> bool:
        """
        Check whether a dribbble user exists or not
        """
        try:
            print("\n🔍 Searching for user " + self.username + "...\n")
            user_page = httpx.get(self.user_pages["main"])
            user_page_soup = BeautifulSoup(user_page.text, "lxml")

            sselect = SilentSelector(user_page_soup)
            if (
                sselect.select_one("section.message-404", False, None)
                and sselect.select_one("section.collage-404", False, None)
                and sselect.select_one("div.collage-404-images", False, None)
            ):

                self.dribbble_user_data["user_exists"] = "No"
                print("✗ {} not found\n".format(self.username))
            else:
                self.dribbble_user_data["user_exists"] = "Yes"
                print("✓ {} found\n".format(self.username))
                print("Profile URL     : {}".format(self.user_pages["main"]))

        except httpx.RequestError as ex:
            print(f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}")

        except httpx.HTTPStatusError as ex:
            print(
                f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
            )

    async def scrape_user_pages_with_metadata_nursery(self):
        """
        Scrape all available dribbble user pages with trio nursery
        """
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.scrape_main_page)
            nursery.start_soon(self.scrape_about_page)
            nursery.start_soon(self.scrape_projects_page)
            nursery.start_soon(self.scrape_goods_page)
            nursery.start_soon(self.scrape_members_page)
            nursery.start_soon(self.scrape_collections_page)
            nursery.start_soon(self.scrape_shots_with_metadata_page)

    def run_nursery_with_metadata_scraper(self):
        """
        Run the trio nursery for scraping pages of a dribbble user
        """
        trio.run(self.scrape_user_pages_with_metadata_nursery)

    async def scrape_user_pages_without_metadata_nursery(self):
        """
        Scrape all available dribbble user pages with trio nursery
        """
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.scrape_main_page)
            nursery.start_soon(self.scrape_about_page)
            nursery.start_soon(self.scrape_projects_page)
            nursery.start_soon(self.scrape_goods_page)
            nursery.start_soon(self.scrape_members_page)
            nursery.start_soon(self.scrape_collections_page)
            nursery.start_soon(self.scrape_shots_without_metadata_page)

    def run_nursery_without_metadata_scraper(self):
        """
        Run the trio nursery for scraping pages of a dribbble user
        """
        trio.run(self.scrape_user_pages_without_metadata_nursery)

    async def scrape_main_page(self):
        """
        Scrape data from the main page of a dribbble user
        """

        async with httpx.AsyncClient() as client:

            try:
                user_page = await client.get(
                    self.user_pages["main"], headers=self.scraper_header
                )
                user_page_soup = BeautifulSoup(user_page.text, "lxml")
                sselect = SilentSelector(user_page_soup)

                # shots count
                shots_count = sselect.select_one("li.shots a span.count", True, None)
                self.dribbble_user_data["shots_count"] = string_to_number(shots_count)

                # projects count
                projects_count = sselect.select_one(
                    "li.projects a span.count", True, None
                )
                self.dribbble_user_data["projects_count"] = string_to_number(
                    projects_count
                )

                # collections count
                collections_count = sselect.select_one(
                    "li.collections a span.count", True, None
                )
                self.dribbble_user_data["collections_count"] = string_to_number(
                    collections_count
                )

                # liked shots count
                liked_shots = sselect.select_one("li.liked a span.count", True, None)
                self.dribbble_user_data["liked_shots"] = string_to_number(liked_shots)

                # user description
                self.dribbble_user_data["user_description"] = sselect.select_one(
                    "div.masthead-intro h2", True, None
                )

                # hire status
                self.dribbble_user_data["hire_status"] = bool(
                    sselect.select_one(
                        "div.hire-prompt-trigger.profile-action-item", False, None
                    )
                )

                # members count
                members_count = sselect.select_one("li.members span.count", True, None)
                self.dribbble_user_data["members_count"] = string_to_number(
                    members_count
                )

                # team profile
                team_profile = sselect.select_one(
                    "div.masthead-teams a.team-avatar-link[href]", False, "href"
                )

                if team_profile is not None:
                    self.dribbble_user_data["team_url"] = DRIBBBLE_URL + team_profile
                else:
                    self.dribbble_user_data["team_url"] = None

                # print some of the info
                print(
                    "Shots           : {}".format(
                        self.dribbble_user_data["shots_count"]
                    )
                )
                print(
                    "Projects        : {}".format(
                        self.dribbble_user_data["projects_count"]
                    )
                )
                print(
                    "Collections     : {}".format(
                        self.dribbble_user_data["collections_count"]
                    )
                )
                print(
                    "Liked Shots     : {}".format(
                        self.dribbble_user_data["liked_shots"]
                    )
                )
                print("\n✓ Main page scraped...")

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

    async def scrape_about_page(self):
        """
        Retrieves data from the about page of a dribbble user
        """

        async with httpx.AsyncClient() as client:
            try:
                about_page = await client.get(
                    self.user_pages["about"], headers=self.scraper_header
                )
                about_page_soup = BeautifulSoup(about_page.text, "lxml")
                sselect = SilentSelector(about_page_soup)

                # profile stats - following, followers, tags
                profile_stats = [
                    stat.find("span", class_="count").text
                    for stat in sselect.select(
                        "section.content-section.profile-stats-section.medium-screens-only a "
                    )
                ]

                # user followers
                user_followers_count = profile_stats[0].replace(",", "")
                self.dribbble_user_data["followers"] = string_to_number(
                    user_followers_count
                )

                # user following
                user_following_count = profile_stats[1].replace(",", "")
                self.dribbble_user_data["following"] = string_to_number(
                    user_following_count
                )

                # user tags
                try:
                    self.dribbble_user_data["tags"] = profile_stats[2]
                except IndexError:
                    self.dribbble_user_data["tags"] = None

                # user location
                self.dribbble_user_data["location"] = (
                    str(sselect.select_one("p.location", True, None))
                    .replace("\n", "")
                    .strip()
                )

                # user bio
                self.dribbble_user_data["bio"] = str(
                    sselect.select_one("p.bio-text", True, None)
                ).replace("\n", "")

                # user pro status
                self.dribbble_user_data["is_pro"] = bool(
                    sselect.select_one("p.info-item.pro", False, None)
                )

                # user join date
                join_date_string = (
                    str(sselect.select_one("p.info-item.created span", True, None))
                    .replace("Member since", "")
                    .strip()
                )
                join_date = datetime.strptime(join_date_string, self.join_date_format)
                self.dribbble_user_data["join_date"] = join_date.strftime(
                    self.preferred_time_format
                )

                # user skills
                skills_list = [
                    skill.text for skill in sselect.select("ul.skills-list a")
                ]
                self.dribbble_user_data["skills"] = skills_list

                # social media profiles
                self.dribbble_user_data["social_media_profiles"] = {}
                social_media_redirect_urls = [
                    DRIBBBLE_URL + anchor["href"]
                    for anchor in sselect.select("ul.social-links-list a")
                ]

                for url in social_media_redirect_urls:
                    profile_url, site = get_redirect_url(url)
                    self.dribbble_user_data["social_media_profiles"][site] = profile_url

                # Print some of the info
                print("Followers       :", self.dribbble_user_data["followers"])
                print("Following       :", self.dribbble_user_data["following"])
                print("Location        :", self.dribbble_user_data["location"])
                print("Pro Status      :", self.dribbble_user_data["is_pro"])
                print("Join Date       :", self.dribbble_user_data["join_date"])
                print("Skills          :", self.dribbble_user_data["skills"])

                print("\n✓ About page scraped...")
            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

    async def scrape_shots_without_metadata_page(self):
        """
        Retrieves data from the shots page of a dribbble user
        """

        user_shots = {}

        async with httpx.AsyncClient() as client:
            try:
                shots_page = await client.get(
                    self.user_pages["main"], headers=self.scraper_header
                )
                shots_page_soup = BeautifulSoup(shots_page.text, "lxml")
                sselect = SilentSelector(shots_page_soup)

                # total shots
                shots_count = string_to_number(
                    sselect.select_one("li.shots a span.count", True, None)
                )
                user_shots["shots_count"] = shots_count
                user_shots["shots"] = {}
                shots_urls = []
                shot_names = []

                # number of pages to scrape
                page_counter = 0
                max_pages = (shots_count // self.shots_per_page) + 5

                # iterate over pages
                while page_counter <= max_pages:

                    current_shots_page = (
                        self.user_pages["shots"]
                        + "?page="
                        + str(page_counter)
                        + "&per_page="
                        + str(self.shots_per_page)
                    )
                    async with httpx.AsyncClient() as client_i:

                        # grab all shots info from current page
                        shots_page = await client_i.get(
                            current_shots_page, headers=self.scraper_header
                        )
                        shots_page_soup = BeautifulSoup(shots_page.text, "lxml")
                        sselect_shots = SilentSelector(shots_page_soup)

                        # loop through each found shot
                        for shot_soup in sselect_shots.find_all(
                            "li", "shot-thumbnail", None, False, None
                        ):
                            current_shot = {}

                            sselect_current_shot = SilentSelector(shot_soup)

                            # shot titles
                            current_shot_title = sselect_current_shot.select_one(
                                "div.shot-title", True, None
                            )
                            shot_names.append(current_shot_title)

                            # shot URL
                            current_shot_url = DRIBBBLE_URL + str(
                                sselect_current_shot.select_one(
                                    "a.shot-thumbnail-link", False, "href"
                                )
                            )
                            shots_urls.append(current_shot_url)

                            current_shot["shot_url"] = current_shot_url

                            # shot alt description
                            current_shot[
                                "alt_description"
                            ] = sselect_current_shot.select_one("img", False, "alt")
                            user_shots["shots"][current_shot_title] = current_shot
                    page_counter += 1

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

        self.dribbble_user_data["shots"] = user_shots
        print("\n✓ Shots page scraped...")

    async def scrape_shots_with_metadata_page(self):
        """
        Retrieves data from the shots page of a dribbble user
        """

        user_shots = {}

        async with httpx.AsyncClient() as client:
            try:
                shots_page = await client.get(
                    self.user_pages["main"], headers=self.scraper_header
                )
                shots_page_soup = BeautifulSoup(shots_page.text, "lxml")
                sselect = SilentSelector(shots_page_soup)

                # total shots
                shots_count = string_to_number(
                    sselect.select_one("li.shots a span.count", True, None)
                )
                user_shots["shots_count"] = shots_count
                user_shots["shots"] = {}
                shots_urls = []
                shot_names = []

                # number of pages to scrape
                page_counter = 0
                max_pages = (shots_count // self.shots_per_page) + 5

                # iterate over pages
                while page_counter <= max_pages:

                    current_shots_page = (
                        self.user_pages["shots"]
                        + "?page="
                        + str(page_counter)
                        + "&per_page="
                        + str(self.shots_per_page)
                    )
                    async with httpx.AsyncClient() as client_i:

                        # grab all shots info from current page
                        shots_page = await client_i.get(
                            current_shots_page, headers=self.scraper_header
                        )
                        shots_page_soup = BeautifulSoup(shots_page.text, "lxml")
                        sselect_shots = SilentSelector(shots_page_soup)

                        # loop through each found shot
                        for shot_soup in sselect_shots.find_all(
                            "li", "shot-thumbnail", None, False, None
                        ):
                            current_shot = {}

                            sselect_current_shot = SilentSelector(shot_soup)

                            # shot titles
                            current_shot_title = sselect_current_shot.select_one(
                                "div.shot-title", True, None
                            )
                            shot_names.append(current_shot_title)

                            # shot URL
                            current_shot_url = DRIBBBLE_URL + str(
                                sselect_current_shot.select_one(
                                    "a.shot-thumbnail-link", False, "href"
                                )
                            )
                            shots_urls.append(current_shot_url)

                            current_shot["shot_url"] = current_shot_url

                            # shot alt description
                            current_shot[
                                "alt_description"
                            ] = sselect_current_shot.select_one("img", False, "alt")
                            user_shots["shots"][current_shot_title] = current_shot
                    page_counter += 1

                # Get more data about the shots
                user_shots = await self.get_shots_data(
                    shots_urls, shot_names, user_shots["shots"]
                )

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

        self.dribbble_user_data["shots"] = user_shots
        print("\n✓ About page scraped...")

    async def scrape_projects_page(self):
        """
        Retrieves data from the projects' page of a dribbble user
        """
        user_projects = {}

        async with httpx.AsyncClient() as client:
            try:
                # scrape projects page
                projects_page = await client.get(
                    self.user_pages["projects"], headers=self.scraper_header
                )
                projects_page_soup = BeautifulSoup(projects_page.text, "lxml")
                sselect = SilentSelector(projects_page_soup)

                # project titles
                project_titles = [
                    str(project.text).strip()
                    for project in sselect.select("div.collection-name")
                ]

                # project shot count
                project_shots_count = [
                    int(
                        str(project_shots.text)
                        .replace("Shots", "")
                        .replace("Shot", "")
                        .strip()
                    )
                    for project_shots in sselect.select(
                        "div.shots-group-meta>span.shots-count"
                    )
                ]

                # project updated date
                project_updated_dates = [
                    datetime.strptime(
                        str(project_updated_date.text).replace("Updated", "").strip(),
                        "%B %d, %Y",
                    ).strftime(self.preferred_time_format)
                    for project_updated_date in sselect.select("span.timestamp")
                ]

                # project urls
                project_urls = [
                    DRIBBBLE_URL + str(anchor["href"])
                    for anchor in sselect.select("a.shots-group")
                ]

                # retrieve data about each project and its shots
                for (
                    project_title,
                    project_url,
                    shots_count,
                    project_updated_date,
                ) in zip(
                    project_titles,
                    project_urls,
                    project_shots_count,
                    project_updated_dates,
                ):

                    max_pages = (shots_count // self.project_shots_per_page) + 1
                    page_number = 1

                    project_shots = {}

                    # loop through all pages of a projects
                    while page_number <= max_pages:
                        project_page_url = project_url + "?page=" + str(page_number)
                        page_number += 1

                        # get current project page soup
                        async with httpx.AsyncClient() as client_i:
                            try:
                                individual_project_page = await client_i.get(
                                    project_page_url
                                )
                                individual_project_page_soup = BeautifulSoup(
                                    individual_project_page.text, "lxml"
                                )
                                sselect_project = SilentSelector(
                                    individual_project_page_soup
                                )

                                # loop though each found shot
                                for shot_soup in sselect_project.find_all(
                                    "div", "shot-section-item", None, False, None
                                ):

                                    current_shot = {}
                                    sselect_shot = SilentSelector(shot_soup)

                                    # shot title
                                    current_shot_title = sselect_shot.select_one(
                                        "h3.shot-title a", True, None
                                    )

                                    # shot published date
                                    shot_pub_date = sselect_shot.select_one(
                                        "p.shot-date", True, None
                                    )
                                    current_shot["shot_pub_date"] = datetime.strptime(
                                        shot_pub_date, "%B %d, %Y"
                                    ).strftime(self.preferred_time_format)

                                    # shot description
                                    current_shot[
                                        "shot_description"
                                    ] = sselect_shot.select_one(
                                        "p.shot-description", True, None
                                    )

                                    # shot URL
                                    current_shot[
                                        "shot_url"
                                    ] = DRIBBBLE_URL + sselect_shot.select_one(
                                        "a.shot-link", False, "href"
                                    )

                                    project_shots[current_shot_title] = current_shot

                                # Assign the projects' shots to the project
                                user_projects[project_title] = {}
                                user_projects[project_title][
                                    "updated_date"
                                ] = project_updated_date
                                user_projects[project_title]["shots"] = project_shots

                            except httpx.RequestError as ex:
                                print(
                                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                                )

                            except httpx.HTTPStatusError as ex:
                                print(
                                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                                )

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

        # Add projects to main dict
        self.dribbble_user_data["projects"] = user_projects
        print("\n✓ Projects page scraped...")

    async def scrape_collections_page(self):
        """
        Retrieves data from the collections' page of a dribbble user
        """
        user_collections = {}

        async with httpx.AsyncClient() as client:

            try:
                collections_page = await client.get(
                    self.user_pages["collections"], headers=self.scraper_header
                )
                collections_page_soup = BeautifulSoup(collections_page.text, "lxml")
                sselect = SilentSelector(collections_page_soup)

                # loop through each collection
                for collection in sselect.find_all(
                    "li", "shots-group-item", None, False, None
                ):
                    current_collection = {}

                    sselect_collection = SilentSelector(collection)

                    # collections' name
                    current_collection_name = str(
                        sselect_collection.find(
                            "div", "collection-name", None, True, None
                        )
                    ).strip()

                    # collections' shots count
                    shots_count = str(
                        sselect_collection.find("span", "shots-count", None, True, None)
                    ).strip()
                    shots_count = str(re.sub("Shot*.", "", shots_count)).strip()
                    current_collection["shots_count"] = int(shots_count)

                    # collections' designer Count
                    designer_count = str(
                        sselect_collection.find(
                            "span", "designers-count", None, True, None
                        )
                    ).strip()
                    designer_count = str(
                        re.sub("Designer*.", "", designer_count)
                    ).strip()
                    current_collection["designers_count"] = int(designer_count)

                    # collections' URL
                    collection_url = DRIBBBLE_URL + sselect_collection.find(
                        "a", "shots-group", None, False, "href"
                    )
                    current_collection["collection_url"] = collection_url

                    # assign the collections' data to dict
                    user_collections[current_collection_name] = current_collection

                    # get current collections' page soup
                    async with httpx.AsyncClient() as client_ii:

                        try:
                            collection_shots_page = await client_ii.get(
                                collection_url, headers=self.scraper_header
                            )
                            collection_shots_page_soup = BeautifulSoup(
                                collection_shots_page.text, "lxml"
                            )
                            user_collections[current_collection_name]["shots"] = {}

                            sselect_current_collection = SilentSelector(
                                collection_shots_page_soup
                            )

                            # loop through each found shot
                            for shot in sselect_current_collection.find_all(
                                "li", "shot-thumbnail", None, False, None
                            ):

                                current_shot = {}
                                sselect_shot = SilentSelector(shot)

                                # shot title
                                shot_title = str(
                                    sselect_shot.find(
                                        "div", "shot-title", None, True, None
                                    )
                                ).strip()

                                # shot designer profile URL
                                current_shot[
                                    "designer_profile_url"
                                ] = DRIBBBLE_URL + str(
                                    sselect_shot.select_one(
                                        "a.hoverable.url", False, "href"
                                    )
                                )
                                # shot designer username
                                current_shot["designer_name"] = str(
                                    sselect_shot.find(
                                        "span", "display-name", None, True, None
                                    )
                                ).strip()

                                # shot likes
                                shot_likes = str(
                                    sselect_shot.find(
                                        "span", "js-shot-likes-count", None, True, None
                                    )
                                ).strip()
                                if "k" in shot_likes or "K" in shot_likes:
                                    current_shot["shot_likes"] = int_k(shot_likes)
                                else:
                                    current_shot["shot_likes"] = int(shot_likes)

                                # shot views
                                shot_views = str(
                                    (
                                        sselect_shot.find(
                                            "span",
                                            "js-shot-views-count",
                                            None,
                                            True,
                                            None,
                                        )
                                    )
                                ).strip()

                                if "k" in shot_views or "K" in shot_views:
                                    current_shot["shot_views"] = int_k(shot_views)
                                else:
                                    current_shot["shot_views"] = int(shot_views)

                                # designer pro status
                                if (
                                    sselect_shot.find(
                                        "span", "badge-pro", None, False, None
                                    )
                                    is not None
                                ):
                                    is_pro = True
                                else:
                                    is_pro = False
                                current_shot["is_pro"] = is_pro

                                # shot URL
                                current_shot["shot_url"] = sselect_shot.find(
                                    "img", None, None, False, "src"
                                )

                                # assign current collection dict to collections
                                user_collections[current_collection_name]["shots"][
                                    shot_title
                                ] = current_shot

                        except httpx.RequestError as ex:
                            print(
                                f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                            )

                        except httpx.HTTPStatusError as ex:
                            print(
                                f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                            )

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

        self.dribbble_user_data["collections"] = user_collections
        print("\n✓ Collections page scraped...")

    async def scrape_members_page(self):
        """
        Retrieves data from the members' page of a dribbble user
        """

        user_members = {}

        async with httpx.AsyncClient() as client:
            try:

                # get members count
                member_page = await client.get(
                    self.user_pages["main"], headers=self.scraper_header
                )
                member_page_soup = BeautifulSoup(member_page.text, "lxml")
                sselect = SilentSelector(member_page_soup)

                members_count = sselect.select_one(
                    "li.members a span.count", True, None
                )

                if members_count is not None:
                    members_count = int(members_count)
                else:
                    members_count = 0

                # scrape if members are available
                if members_count > 0:
                    member_page_count = 1

                    if members_count < self.members_per_page:
                        max_pages = 1
                    elif members_count > self.members_per_page:
                        max_pages = (members_count // self.members_per_page) + 1

                    while member_page_count <= max_pages:

                        # construct members page URL
                        current_user_members_page_url = (
                            self.user_pages["members"]
                            + str(member_page_count)
                            + "&per_page="
                            + str(self.members_per_page)
                        )

                        # get current member page soup
                        async with httpx.AsyncClient() as client:
                            try:
                                members_page = await client.get(
                                    current_user_members_page_url,
                                    headers=self.scraper_header,
                                )
                                members_page_soup = BeautifulSoup(
                                    members_page.text, "lxml"
                                )
                                sselect = SilentSelector(members_page_soup)

                                # loop through each found member
                                if sselect.find_all(
                                    "li", "scrolling-row", None, False, None
                                ):
                                    for member in sselect.find_all(
                                        "li", "scrolling-row", None, False, None
                                    ):
                                        current_member = {}

                                        sselect_member = SilentSelector(member)

                                        # member username
                                        member_username = str(
                                            sselect_member.select_one(
                                                "span.designer-card-username a.designer-link",
                                                False,
                                                "href",
                                            )
                                        ).replace("/", "")

                                        # member profile URL
                                        current_member["profile_url"] = (
                                            DRIBBBLE_URL + "/" + member_username
                                        )

                                        # member pofile name
                                        profile_name = sselect_member.select_one(
                                            "span.designer-card-username a.designer-link",
                                            True,
                                            None,
                                        )

                                        current_member["profile_name"] = profile_name

                                        # member location
                                        current_member[
                                            "location"
                                        ] = sselect_member.select_one(
                                            "span.designer-card-location", True, None
                                        )

                                        # member pro status
                                        current_member["is_pro"] = bool(
                                            sselect_member.select_one(
                                                "span.badge.badge-pro", False, None
                                            )
                                        )

                                        user_members[member_username] = current_member
                                    member_page_count += 1
                                else:
                                    break

                            except httpx.RequestError as ex:
                                print(
                                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                                )

                            except httpx.HTTPStatusError as ex:
                                print(
                                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                                )

                    user_members["members_count"] = members_count
                    self.dribbble_user_data["members"] = user_members

                else:
                    self.dribbble_user_data["members"] = None

                print("\n✓ Members page scraped...")
            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

    async def scrape_goods_page(self):
        """
        Retrieves data from the goods' page of a dribbble user

        """

        user_goods = {}
        async with httpx.AsyncClient() as client:
            try:
                goods_page = await client.get(
                    self.user_pages["goods"], headers=self.scraper_header
                )
                goods_page_soup = BeautifulSoup(goods_page.text, "lxml")
                sselect = SilentSelector(goods_page_soup)

                # goods' Names
                goods_names = [
                    name.text
                    for name in sselect.select(
                        "div.shot-details-container>div.font-label"
                    )
                ]

                # goods' prices
                goods_prices = [
                    str(price.text).strip()
                    for price in sselect.select(
                        "div.shot-details-container>div.price-label>span"
                    )
                ]

                # goods' urls
                goods_urls = [
                    DRIBBBLE_URL
                    + "/shots/"
                    + str(goods_id_soup.get("data-thumbnail-id"))
                    for goods_id_soup in sselect.find_all(
                        "li", "shot-thumbnail-container", None, False, None
                    )
                ]

                for goods_url, goods_name, goods_price in zip(
                    goods_urls, goods_names, goods_prices
                ):
                    current_user_good = {}

                    # Construct Goods shot URL
                    current_user_good["url"] = goods_url
                    current_user_good["price"] = goods_price
                    user_goods[goods_name] = current_user_good

                # Get more data about the goods on sale
                user_goods = await self.get_shots_data(
                    goods_urls, goods_names, user_goods
                )

            except httpx.RequestError as ex:
                print(
                    f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                )

            except httpx.HTTPStatusError as ex:
                print(
                    f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                )

        self.dribbble_user_data["goods_for_sale"] = user_goods
        print("\n✓ Goods page scraped...")

    async def get_shots_data(
        self, shot_urls: list, shot_names: list, shots_dict: dict
    ) -> dict:
        """
        Retrieves data about a list of given shots
        """
        for shot_url, shot_name in zip(shot_urls, shot_names):

            # get current shot page HTML
            async with httpx.AsyncClient() as client:
                try:
                    shot_page = await client.get(shot_url, headers=self.scraper_header)
                    shot_page_soup = BeautifulSoup(shot_page.text, "lxml")
                    sselect = SilentSelector(shot_page_soup)
                    current_shot_data = {}

                    # get shot color palette
                    shot_color_palette = [
                        color.find("a").text
                        for color in sselect.select("ul.color-chips.group li")
                    ]
                    current_shot_data["color_palette"] = shot_color_palette

                    # extract JSON  from script tag
                    shot_data_script = sselect.select("body script")[6]
                    shot_data_js = shot_data_script.text
                    shot_data_js = "".join(shot_data_js.split("\n")[3:])
                    shot_data_json = chompjs.parse_js_object(
                        shot_data_js, json_params={"strict": False}
                    )
                    shot_data_dict = dict(shot_data_json)

                    # shot metadata
                    current_shot_data["likes"] = shot_data_dict["shotData"][
                        "likesCount"
                    ]
                    shot_published_date = datetime.strptime(
                        shot_data_dict["shotData"]["postedOn"],
                        self.shot_published_date_format,
                    ).strftime(self.preferred_time_format)

                    current_shot_data["published_date"] = shot_published_date
                    current_shot_data["saves_count"] = shot_data_dict["shotData"][
                        "savesCount"
                    ]
                    current_shot_data["isAnimated"] = shot_data_dict["shotData"][
                        "isAnimated"
                    ]
                    current_shot_data["isAnimatedGif"] = shot_data_dict["shotData"][
                        "isAnimatedGif"
                    ]
                    current_shot_data["tags"] = shot_data_dict["shotData"]["tags"]
                    current_shot_data["views_count"] = shot_data_dict["shotData"][
                        "viewsCount"
                    ]

                except httpx.RequestError as ex:
                    print(
                        f"\nAn error occurred while requesting {ex.request.url!r}.\n {ex}"
                    )

                except httpx.HTTPStatusError as ex:
                    print(
                        f"\nError response {ex.response.status_code} while requesting {ex.request.url!r}."
                    )

            shots_dict[shot_name]["metadata"] = current_shot_data
        return shots_dict

    def export_to_json(self):
        """
        Exports the scraped user data as a JSON file

        """

        # Convert dict to JSON
        dribbble_json = json.dumps(self.dribbble_user_data)

        # Write to JSON file
        with open(self.json_file, "w") as json_file:
            json_file.write(dribbble_json)

        print("\nResults saved to {}".format(self.json_file))
