import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "readme.md").read_text()

setup(
    name="dribbble-py",
    version="0.0.1",
    description="Dribbble Downloader",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rand-net/dribbble-py",
    author="rand-net",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["dribbble_py"],
    include_package_data=True,
    entry_points={"console_scripts": ["drbl_py = dribbble_py.cli:main"]},
    install_requires=[
        "art",
        "beautifulsoup4",
        "chompjs",
        "requests",
        "lxml",
        "httpx",
        "trio",
    ],
    keywords=["dribbble", "dribbble-scraper", "scraper", "graphic-design", "design"],
)
