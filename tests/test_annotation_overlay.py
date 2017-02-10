from . import tmp_dataset_fixture  # NOQA


def test_annotation_overlay_functional(tmp_dataset_fixture):  # NOQA

    my_dataset = tmp_dataset_fixture
    my_overlay = my_dataset.empty_overlay()

    item_hash = "b640cee82f798bb38a995b6bd30e8d71a12d7d7c"
    my_overlay[item_hash]["latitude"] = 57.4
    my_overlay[item_hash]["longitude"] = 0.3

    my_dataset.persist_overlay(name="geo_locations", overlay=my_overlay)

    result = my_dataset.overlays["geo_locations"][item_hash]

    assert result == {"latitude": 57.4, "longitude": 0.3}


def test_empty_overlay(tmp_dataset_fixture):

    actual_overlay = tmp_dataset_fixture.empty_overlay()

    assert isinstance(actual_overlay, dict)

    assert len(actual_overlay) == 7

    assert "b640cee82f798bb38a995b6bd30e8d71a12d7d7c" in actual_overlay

    assert actual_overlay.values()[0] == {}
