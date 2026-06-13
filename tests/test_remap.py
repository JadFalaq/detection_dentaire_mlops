from __future__ import annotations

import pytest

from detection_dentaire.data import remap_records


def test_remap_records_maps_raw_classes_to_7_classes():
    records = [
        (4, 0.5, 0.5, 0.2, 0.2),
        (7, 0.4, 0.4, 0.1, 0.1),
        (12, 0.3, 0.3, 0.15, 0.15),
    ]

    remapped = remap_records(records)

    assert remapped == [
        (0, 0.5, 0.5, 0.2, 0.2),
        (1, 0.4, 0.4, 0.1, 0.1),
        (6, 0.3, 0.3, 0.15, 0.15),
    ]


def test_remap_records_raises_on_unknown_class():
    with pytest.raises(ValueError, match="Unknown original class id"):
        remap_records([(99, 0.5, 0.5, 0.2, 0.2)])
