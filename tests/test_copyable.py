from datasette.app import Datasette
import pytest
import httpx
import sqlite_utils


@pytest.fixture(scope="session")
def ds(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["dogs"].insert_all(
        [
            {"id": 1, "name": "Cleo", "age": 5, "weight": 51.2},
            {"id": 2, "name": "Pancakes", "age": 4, "weight": 35.5},
        ],
        pk="id",
    )
    return Datasette([db_path])


@pytest.mark.asyncio
async def test_plugin_is_installed(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-copyable" in installed_plugins


@pytest.mark.asyncio
async def test_plugin_adds_copyable_extension(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/dogs")
        assert 200 == response.status_code
        assert ".copyable" in response.text


@pytest.mark.asyncio
async def test_copyable_page_tsv(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/dogs.copyable")
        assert 200 == response.status_code
        assert "<h1>Copy as tsv</h1>" in response.text
        assert (
            '<textarea class="copyable">id\tname\tage\tweight\r\n1\tCleo\t5\t51.2\r\n2\tPancakes\t4\t35.5\r\n</textarea>'
            in response.text
        )


@pytest.mark.asyncio
async def test_raw_page_tsv(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/test/dogs.copyable?_raw=1")
        assert 200 == response.status_code
        assert (
            "id\tname\tage\tweight\r\n1\tCleo\t5\t51.2\r\n2\tPancakes\t4\t35.5\r\n"
            == response.text
        )


@pytest.mark.asyncio
async def test_copyable_page_github(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get(
            "http://localhost/test/dogs.copyable?_table_format=github"
        )
        assert 200 == response.status_code
        assert "<h1>Copy as github</h1>" in response.text
        assert (
            '<textarea class="copyable">|   id | name     |   age |   weight |\n|------|----------|-------|----------|\n|    1 | Cleo     |     5 |     51.2 |\n|    2 | Pancakes |     4 |     35.5 |</textarea>'
            in response.text
        )


@pytest.mark.asyncio
async def test_raw_page_github(ds):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get(
            "http://localhost/test/dogs.copyable?_table_format=github&_raw=1"
        )
        assert 200 == response.status_code
        assert (
            "|   id | name     |   age |   weight |\n|------|----------|-------|----------|\n|    1 | Cleo     |     5 |     51.2 |\n|    2 | Pancakes |     4 |     35.5 |"
            == response.text
        )
