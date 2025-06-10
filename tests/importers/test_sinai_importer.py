# pylint: disable=no-self-use

import json

import pytest

from feed_sinai.sinai_json_importer import SinaiJsonImporter
import feed_sinai.sinai_types as st

# feed_sinai.mapper = importlib.import_module("feed_sinai.mapper.dlp")

BASE_PATH = "tests/sinaiportal_json_export"
IMPORTER = SinaiJsonImporter(base_path=BASE_PATH)


class TestSinaiJsonImporter:
    def test_get_filename(self):
        assert IMPORTER.get_filename("ark:/21198/z1h13zxq") == "z1h13zxq.json"

    class TestGetTextUnit:
        def test_good_text_unit(self):
            stub = st.TextUnitStub.model_validate_json(
                """
                {
                    "id": "ark:/21198/s1308n",
                    "label": "Item 1"
                }
            """
            )
            result = IMPORTER.get_text_unit(stub)
            assert result.model_dump(exclude_none=False) == {
                "ark": "ark:/21198/s1308n",
                "bib": None,
                "cataloguer": None,
                "features": None,
                "internal": None,
                "label": "Liturgical collection",
                "lang": [
                    {
                        "id": "nucl1302",
                        "label": "Georgian",
                    },
                ],
                "locus": None,
                "note": None,
                "para": None,
                "parent": [
                    "ark:/21198/s18d1p",
                ],
                "reconstructed_from": None,
                "reconstruction": False,
                "summary": None,
                "work_wit": [
                    {
                        "alt_title": None,
                        "as_written": None,
                        "bib": None,
                        "contents": None,
                        "excerpt": None,
                        "locus": None,
                        "note": None,
                        "work": {
                            "creator": None,
                            "desc_title": "Liturgical collection",
                            "genre": [
                                {
                                    "id": "liturgical-texts",
                                    "label": "Liturgical texts",
                                },
                            ],
                        },
                    },
                ],
                "desc_provenance": None,
            }

        def test_loads_all_text_units(self):
            n_files = 0
            for path in (IMPORTER.base_path / "text_units").glob("*.json"):
                stub = st.TextUnitStub(id="ark:/21198/" + path.stem, label="whatevs")
                IMPORTER.get_text_unit(stub)
                n_files += 1
            assert n_files == 15

    class TestGetLayer:
        def test_good_layer(self):
            stub = st.LayerStub.model_validate_json(
                """
                {
                    "id": "ark:/21198/ten0p1ol",
                    "label": "Overtext layer (late 9th c., Kufic)",
                    "type": {
                        "id": "overtext",
                        "label": "Overtext"
                        },
                    "locus": "ff. 128-143"
                }
            """
            )
            result = IMPORTER.get_layer(stub).model_dump(
                    exclude_none=True, round_trip=True
                )
            assert result == {
                "ark": "ark:/21198/ten0p1ol",
                "reconstruction": False,
                "state": {"id": "overtext", "label": "Overtext"},
                "label": "Arabic NF M 28, Part 1, Overtext",
                "locus": "ff. 128-143",
                "summary": "Gospels, late 9th c., Arabic (Kufic)",
                "extent": "16 ff.",
                "writing": [
                    {
                        "script": [
                            {
                                "id": "kufic",
                                "label": "Kufic",
                                "writing_system": "Arabic",
                            }
                        ],
                        "locus": "ff. 128-143",
                    }
                ],
                "ink": [{"locus": "ff. 128-143", "note": ["Titles in red ink"]}],
                "text_unit": [
                    {
                        "ark": "ark:/21198/ten0p1olt1",
                        "reconstruction": False,
                        "label": "Arabic Gospels",
                        "locus": "ff. 128r-143v",
                        "lang": [{"id": "arab1395", "label": "Arabic"}],
                        "work_wit": [
                            {
                                "work": {
                                    "ark": "ark:/21198/s12c7r",
                                    "pref_title": "Matthew",
                                    "alt_title": ["Bible. Matthew"],
                                    "genre": [
                                        {
                                            "id": "biblical-texts",
                                            "label": "Biblical texts",
                                        },
                                        {"id": "gospel-books", "label": "Gospel books"},
                                    ],
                                    "rel_con": [
                                        {
                                            "label": "Bible. Matthew",
                                            "uri": st.AnyUrl(st.AnyUrl("https://viaf.org/viaf/188427863")),
                                            "source": st.RelatedConceptSource.VIAF,
                                        },
                                        {
                                            "label": "Bible. Matthew",
                                            "uri": st.AnyUrl(st.AnyUrl("http://id.loc.gov/authorities/names/n79056834")),
                                            "source": st.RelatedConceptSource.LoC,
                                        },
                                    ],
                                    "refno": [],
                                    "bib": [],
                                },
                                "locus": "ff. 128r-130",
                            },
                            {
                                "work": {
                                    "ark": "ark:/21198/s1630k",
                                    "pref_title": "Mark",
                                    "alt_title": ["Bible. Mark"],
                                    "genre": [
                                        {
                                            "id": "biblical-texts",
                                            "label": "Biblical texts",
                                        },
                                        {"id": "gospel-books", "label": "Gospel books"},
                                    ],
                                    "rel_con": [
                                        {
                                            "label": "Bible. Mark",
                                            "uri": st.AnyUrl("https://viaf.org/viaf/179823714"),
                                            "source": st.RelatedConceptSource.VIAF,
                                        },
                                        {
                                            "label": "Bible. Mark",
                                            "uri": st.AnyUrl("http://id.loc.gov/authorities/names/n78095773"),
                                            "source": st.RelatedConceptSource.LoC,
                                        },
                                    ],
                                    "refno": [],
                                    "bib": [],
                                },
                                "locus": "ff. 130v-135r",
                            },
                            {
                                "work": {
                                    "ark": "ark:/21198/s1k88r",
                                    "pref_title": "Luke",
                                    "alt_title": ["Bible. Luke"],
                                    "genre": [
                                        {
                                            "id": "biblical-texts",
                                            "label": "Biblical texts",
                                        },
                                        {"id": "gospel-books", "label": "Gospel books"},
                                    ],
                                    "rel_con": [
                                        {
                                            "label": "Bible. Luke",
                                            "uri": st.AnyUrl("http://viaf.org/viaf/257061095"),
                                            "source": st.RelatedConceptSource.VIAF,
                                        }
                                    ],
                                    "refno": [],
                                    "bib": [],
                                },
                                "locus": "ff. 135r-140r",
                            },
                            {
                                "work": {
                                    "ark": "ark:/21198/s1388d",
                                    "pref_title": "John",
                                    "alt_title": ["Bible. John"],
                                    "genre": [
                                        {
                                            "id": "biblical-texts",
                                            "label": "Biblical texts",
                                        },
                                        {"id": "gospel-books", "label": "Gospel books"},
                                    ],
                                    "rel_con": [
                                        {
                                            "label": "Bible. John",
                                            "uri": st.AnyUrl("https://viaf.org/viaf/57145910123927021804"),
                                            "source": st.RelatedConceptSource.VIAF,
                                        },
                                        {
                                            "label": "Bible. John",
                                            "uri": st.AnyUrl("http://id.loc.gov/authorities/names/n79060414"),
                                            "source": st.RelatedConceptSource.LoC,
                                        },
                                    ],
                                    "refno": [],
                                    "bib": [],
                                },
                                "locus": "ff. 140v-143v",
                            },
                        ],
                        "features": [],
                        "note": [
                            {
                                "type": {"id": "contents", "label": "Contents Note"},
                                "value": "The Gospels continue in Arabic NF M 8 and NF M 27",
                            }
                        ],
                        "desc_provenance": {
                            "program": [
                                {
                                    "label": "Sinai Palimpests Project",
                                    "description": "Described as part of the Sinai Palimpsests Project (2006-2017). The Sinai Palimpsests Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from Arcadia. The Project provides scholarly identification and description of the undertext objects in a subset of palimpsested manuscripts in the Sinai collection, with minimal metadata for the overtexts of the host manuscripts.",
                                }
                            ]
                        },
                        "parent": ["ark:/21198/ten0p1ol"],
                        "internal": [
                            "Test record, delete after development is complete"
                        ],
                    }
                ],
                "assoc_date": [
                    {
                        "type": {"id": "origin", "label": "Origin Date"},
                        "note": ["Paleographic dating"],
                        "value": "Second half 9th c. CE",
                        "iso": {"not_before": "0851", "not_after": "0900"},
                    }
                ],
                "note": [
                    {
                        "type": {"id": "ornamentation", "label": "Ornamentation"},
                        "value": "Decorative headpieces throughout",
                    },
                    {
                        "type": {"id": "condition", "label": "Condition"},
                        "value": "Several damaged folios were repaired and reinforced more recently",
                    },
                ],
                "bib": [
                    {
                        "id": st.UUID("36ac2d29-349f-496d-b4ea-aff4e605c4ba"),
                        "type": {"id": "ref", "label": "Reference Work"},
                        "range": "p. 48-90",
                    }
                ],
                "parent": ["ark:/21198/ten02zkr"],
                "desc_provenance": {
                    "program": [
                        {
                            "label": "Sinai Palimpests Project",
                            "description": "Described as part of the Sinai Palimpsests Project (2006-2017). The Sinai Palimpsests Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from Arcadia. The Project provides scholarly identification and description of the undertext objects in a subset of palimpsested manuscripts in the Sinai collection, with minimal metadata for the overtexts of the host manuscripts.",
                        }
                    ]
                },
                "internal": ["Test record for development purposes; please delete."],
            }

        def test_loads_all_layers(self):
            n_files = 0
            for path in (IMPORTER.base_path / "layers").glob("*.json"):
                stub = st.LayerStub(
                    id="ark:/21198/" + path.stem,
                    label="whatevs",
                    type={"id": "what", "label": "ever"},
                )
                IMPORTER.get_layer(stub)
                n_files += 1
            assert n_files == 15

    class TestGetMergedManuscript:
        def test_good_manuscript(self):
            with open(f"{BASE_PATH}/outputs/z1h13zxq.json", encoding="utf-8") as f:
                expected = json.load(f)

            result = IMPORTER.get_merged_manuscript(
                IMPORTER.base_path / "ms_objs/z1h13zxq.json"
            )

            assert json.loads(result.model_dump_json(exclude_none=True)) == expected

        @pytest.mark.xfail  # Don't seem to have good data here yet
        def test_loads_all_manuscripts(self):
            n_files = 0
            for path in (IMPORTER.base_path / "ms_objs").glob("*.json"):
                IMPORTER.get_merged_manuscript(path)
                n_files += 1
            assert n_files == 15
