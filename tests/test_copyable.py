from datasette.app import Datasette
import pytest
import sqlite_utils


@pytest.fixture(scope="session")
def ds(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["species"].insert({"id": 1, "name": "Dog"}, pk="id")
    db["dogs"].insert_all(
        [
            {"id": 1, "name": "Cleo", "age": 5, "weight": 51.2, "species": 1},
            {"id": 2, "name": "Pancakes", "age": 4, "weight": 35.5, "species": 1},
        ],
        pk="id",
        foreign_keys=("species",),
    )
    return Datasette([db_path])


@pytest.mark.asyncio
async def test_plugin_is_installed(ds):
    response = await ds.client.get("/-/plugins.json")
    assert 200 == response.status_code
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-copyable" in installed_plugins


@pytest.mark.asyncio
async def test_plugin_adds_copyable_extension(ds):
    response = await ds.client.get("/test/dogs")
    assert 200 == response.status_code
    assert ".copyable" in response.text


@pytest.mark.asyncio
async def test_copyable_page_tsv(ds):
    response = await ds.client.get("/test/dogs.copyable")
    assert 200 == response.status_code
    assert "<h1>Copy as tsv</h1>" in response.text
    assert (
        '<textarea class="copyable">id\tname\tage\tweight\tspecies\r\n'
        "1\tCleo\t5\t51.2\t1\r\n"
        "2\tPancakes\t4\t35.5\t1"
        "\r\n</textarea>"
    ) in response.text


@pytest.mark.asyncio
async def test_raw_page_tsv(ds):
    response = await ds.client.get("/test/dogs.copyable?_raw=1")
    assert 200 == response.status_code
    assert (
        "id\tname\tage\tweight\tspecies\r\n"
        "1\tCleo\t5\t51.2\t1\r\n"
        "2\tPancakes\t4\t35.5\t1\r\n"
    ) == response.text


@pytest.mark.asyncio
async def test_copyable_page_github(ds):
    response = await ds.client.get("/test/dogs.copyable?_table_format=github")
    assert 200 == response.status_code
    assert "<h1>Copy as github</h1>" in response.text
    assert (
        '<textarea class="copyable">'
        "|   id | name     |   age |   weight |   species |\n"
        "|------|----------|-------|----------|-----------|\n"
        "|    1 | Cleo     |     5 |     51.2 |         1 |\n"
        "|    2 | Pancakes |     4 |     35.5 |         1 |</textarea>"
    ) in response.text


@pytest.mark.asyncio
async def test_raw_page_github(ds):
    response = await ds.client.get("/test/dogs.copyable?_table_format=github&_raw=1")
    assert 200 == response.status_code
    assert (
        "|   id | name     |   age |   weight |   species |\n"
        "|------|----------|-------|----------|-----------|\n"
        "|    1 | Cleo     |     5 |     51.2 |         1 |\n"
        "|    2 | Pancakes |     4 |     35.5 |         1 |"
    ) == response.text


@pytest.mark.asyncio
async def test_raw_page_tsv_with_labels(ds):
    response = await ds.client.get("/test/dogs.copyable?_labels=on&_raw=1")
    assert 200 == response.status_code
    assert (
        "id\tname\tage\tweight\tspecies\r\n"
        "1\tCleo\t5\t51.2\tDog\r\n"
        "2\tPancakes\t4\t35.5\tDog\r\n"
    ) == response.text


@pytest.mark.asyncio
async def test_copyable_page_github_with_labels(ds):
    response = await ds.client.get(
        "/test/dogs.copyable?_table_format=github&_labels=on"
    )
    assert 200 == response.status_code
    assert "<h1>Copy as github</h1>" in response.text
    assert (
        '<textarea class="copyable">'
        "|   id | name     |   age |   weight | species   |\n"
        "|------|----------|-------|----------|-----------|\n"
        "|    1 | Cleo     |     5 |     51.2 | Dog       |\n"
        "|    2 | Pancakes |     4 |     35.5 | Dog       |</textarea>"
    ) in response.text
