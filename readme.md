# Dribbble-py

A python scraper for dribbble.com

![PyPI](https://img.shields.io/pypi/v/dribbble-py?style=flat-square)
![GitHub](https://img.shields.io/github/license/rand-net/dribbble-py?style=flat-square)

## Disclaimer

Any legal issues regarding the downloading of graphic assets of Dribbble users should be taken up with the responsible forks and content abusers themselves, as we are not affiliated with them.

Dribbble-py does not support or promote downloading of graphic assets of a Dribbble user and using their assets without permission.

In case of copyright infringement, please directly contact the responsible forks or the individuals responsible for the abuse.

This app merely scrapes information about a Dribbble user, publicly available on the website.


## Installation

```
$ pip install -U dribbble-py
```

## Usage

```
$ drbl_py -h

usage: drbl_py [-h] [-u USERNAME] [-j JSON_FILE] [-v VERBOSE] [--version]

Dribble-py 0.0.1

Program to scrape dribbble user information

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Enter username to scrape.


  -m, --get-metadata    Get metadata about every user shot.
                        Takes longer to scrape.
                        Default = No metadata about user shots


  -j JSON_FILE, --json-file JSON_FILE
                        Name of output JSON filename.
                        Default = username.json


 --version             show program's version number and exit

    Example usage
    -------------

    Download info about a user.

        $ drbl_py -u JohnDoe

    Download info about a user to a custom JSON file.

        $ drbl_py -u JohnDoe -j John

```
