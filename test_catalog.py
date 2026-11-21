import pytest

from errors import (
    CorruptedFileError,
    DuplicateIDError,
    InvalidItemError,
    UnsupportedVersionError,
)
from main import Catalog, MediaItem


def test_create_correct_item():
    movie = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)

    assert isinstance(movie, MediaItem)
    assert movie.id == "001"
    assert movie.name == "Marvel"
    assert movie.category == "Action"
    assert movie.year == 2026
    assert movie.director == "tarantino"
    assert movie.views == 1234


def test_create_invalid_entity():
    with pytest.raises(InvalidItemError):
        MediaItem("001", "", "Action", 2026, "tarantino", 1234)


def test_add_item():
    movie = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    catalog = Catalog()
    catalog.add(movie)
    assert next(iter(catalog)) == movie


def test_get_item():
    movie = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    catalog = Catalog()
    catalog.add(movie)
    assert catalog.get("001") == movie


def test_delete_item():
    movie = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    catalog = Catalog()
    catalog.add(movie)
    catalog.remove("001")
    assert catalog.__len__() == 0


def test_duplicate_id():
    with pytest.raises(DuplicateIDError):
        movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
        movie2 = MediaItem("001", "DC", "Action", 2019, "Daniel", 12343737)
        catalog = Catalog()
        catalog.add(movie1)
        catalog.add(movie2)


def test_search_by_category():
    movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    movie2 = MediaItem("002", "DC", "Action", 2019, "Daniel", 12343737)
    catalog = Catalog()
    catalog.add(movie1)
    catalog.add(movie2)
    assert catalog.find_by_category("Action") == [movie1, movie2]


def test_search_by_name():
    movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    movie2 = MediaItem("002", "Marvel", "Action", 2019, "Daniel", 12343737)
    catalog = Catalog()
    catalog.add(movie1)
    catalog.add(movie2)
    assert catalog.find_by_name("Marvel") == [movie1, movie2]


def test_iteration_order():
    movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    movie2 = MediaItem("002", "DC", "Action", 2019, "Daniel", 12343737)
    movie3 = MediaItem("003", "Dune", "Modern", 2024, "John", 93883737)
    catalog = Catalog()
    catalog.add(movie1)
    catalog.add(movie2)
    catalog.add(movie3)
    result = []
    result = list(catalog)
    assert result == [movie1, movie2, movie3]


def test_trip_JSON():
    movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    movie2 = MediaItem("002", "DC", "Action", 2019, "Daniel", 12343737)
    movie3 = MediaItem("003", "Dune", "Modern", 2024, "John", 93883737)
    catalog = Catalog()
    catalog.add(movie1)
    catalog.add(movie2)
    catalog.add(movie3)
    catalog.save()
    catalog_new = Catalog()
    catalog_new.load("catalog.json")
    assert catalog._items == catalog_new._items


def test_corrupted_json_file():
    with pytest.raises(CorruptedFileError):
        catalog = Catalog()
        catalog.load("data.json")


def test_unknown_version():
    with pytest.raises(UnsupportedVersionError):
        catalog = Catalog()
        catalog.load("ver.json")


def test_absence_of_partial_changes_following_a_loading_error():
    movie1 = MediaItem("001", "Marvel", "Action", 2026, "tarantino", 1234)
    movie2 = MediaItem("002", "DC", "Action", 2019, "Daniel", 12343737)
    movie3 = MediaItem("003", "Dune", "Modern", 2024, "John", 93883737)
    catalog = Catalog()
    catalog.add(movie1)
    catalog.add(movie2)
    catalog.add(movie3)
    original_items = catalog._items.copy()

    original_index = {
        category: ids.copy()
        for category, ids in catalog._category_index.items()
    }

    with pytest.raises(CorruptedFileError):
        catalog.load("error_json_item.json")

    assert catalog._items == original_items
    assert catalog._category_index == original_index