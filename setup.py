from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="datasette-copyable",
    description="Datasette plugin for outputting tables in formats suitable for copy and paste",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Simon Willison",
    url="https://github.com/simonw/datasette-copyable",
    project_urls={
        "Issues": "https://github.com/simonw/datasette-copyable/issues",
        "CI": "https://github.com/simonw/datasette-copyable/actions",
        "Changelog": "https://github.com/simonw/datasette-copyable/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["datasette_copyable"],
    entry_points={"datasette": ["copyable = datasette_copyable"]},
    install_requires=["datasette", "tabulate"],
    extras_require={"test": ["pytest", "pytest-asyncio", "httpx", "sqlite-utils"]},
    tests_require=["datasette-copyable[test]"],
    package_data={"datasette_copyable": ["templates/*.html"]},
)
