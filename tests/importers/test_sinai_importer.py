# pylint: disable=no-self-use

import json

import pytest

from feed_sinai.sinai_json_importer import SinaiJsonImporter
import feed_sinai.sinai_types as st
from tests.importers import test_sinai_types

# feed_sinai.mapper = importlib.import_module("feed_sinai.mapper.dlp")

BASE_PATH = 'tests/sinaiportal_json_export'
IMPORTER = SinaiJsonImporter(base_path=BASE_PATH)


def test_get_filename() -> None:
    assert IMPORTER.get_filename('ark:/21198/z1h13zxq') == 'z1h13zxq.json'


def test_get_agent() -> None:
    result = IMPORTER.get_agent('ark:/21198/s1b59x')
    assert isinstance(result, st.Agent)
    assert result.model_dump(exclude_none=True) == {
        'ark': 'ark:/21198/s1b59x',
        'type': {'id': 'person', 'label': 'Person'},
        'pref_name': 'Onuphrius',
        'alt_name': [],
        'gender': {'id': 'man', 'label': 'Man'},
        'death': {
            'value': 'ca. 400 CE',
            'iso': {'not_before': 375, 'not_after': 425},
        },
        'rel_con': [
            {
                'label': 'Onuphrius, Saint, -approximately 400',
                'uri': st.AnyUrl('http://viaf.org/viaf/20485021'),
                'source': st.RelatedConceptSource.VIAF,
            },
            {
                'label': 'Onuphrius, Saint, -approximately 400',
                'uri': st.AnyUrl('https://id.loc.gov/authorities/names/n92113349'),
                'source': st.RelatedConceptSource.LoC,
            },
            {
                'label': 'Onuphrius, Saint, -approximately 400',
                'uri': st.AnyUrl('https://w3id.org/haf/person/232371232899'),
                'source': st.RelatedConceptSource.HAF,
            },
            {
                'label': 'Onuphrius anachoreta in Aegypto',
                'uri': st.AnyUrl('https://pinakes.irht.cnrs.fr/notices/saint/691/'),
                'source': st.RelatedConceptSource.Pinakes,
            },
        ],
    }


def test_get_assoc_name_item() -> None:
    unmerged = test_sinai_types.TestAssocNameItem.EPHREM.convert(st.AssocNameItemUnmerged)
    result = IMPORTER.get_assoc_name_item(unmerged)
    assert isinstance(result, st.AssocNameItemMerged)
    assert result.agent and result.agent.alt_name == ['Ephrem the Syrian', 'ܐܦܪܝܡ']


class TestGetWork:
    def test_good_get_work(self) -> None:
        stub = st.WorkStub(id='ark:/21198/s1b015')
        result = IMPORTER.get_conceptual_work(stub)
        assert isinstance(result, st.ConceptualWorkMerged)
        assert result.pref_title == '2 John'

    def test_loads_all_works(self) -> None:
        n_files = 0
        for path in (IMPORTER.base_path / 'works').glob('*.json'):
            stub = st.WorkStub(id='ark:/21198/' + path.stem)
            IMPORTER.get_conceptual_work(stub)
            n_files += 1
        assert n_files == 129


def test_get_work_brief() -> None:
    raw = st.WorkBriefUnmerged(desc_title='Abc123', creator=['ark:/21198/s1b59x'])
    result = IMPORTER.get_work_brief(raw)
    assert isinstance(result, st.WorkBriefMerged)
    assert result.creator and isinstance(result.creator[0], st.Agent)
    assert result.creator[0].pref_name == 'Onuphrius'


class TestGetWorkWit:
    def test_get_work_wit_with_stub(self) -> None:
        raw = st.WorkWitItemUnmerged(
            work=st.WorkStub(id='ark:/21198/s1b015'),
        )
        result = IMPORTER.get_work_wit(raw)
        assert isinstance(result, st.WorkWitItemMerged)
        assert isinstance(result.work, st.ConceptualWorkMerged)
        assert result.work.pref_title == '2 John'

    def test_get_work_wit_with_workbrief(self) -> None:
        raw = st.WorkWitItemUnmerged(
            work=st.WorkBriefUnmerged(desc_title='Test Work', creator=['ark:/21198/s1b59x'])
        )
        result = IMPORTER.get_work_wit(raw)
        assert isinstance(result, st.WorkWitItemMerged)
        assert isinstance(result.work, st.WorkBriefMerged)
        assert result.work.creator and isinstance(result.work.creator[0], st.Agent)
        assert result.work.creator[0].pref_name == 'Onuphrius'


class TestGetTextUnit:
    def test_good_text_unit(self) -> None:
        stub = st.TextUnitStub.model_validate_json(
            """
            {
                "id": "ark:/21198/s1308n",
                "label": "Item 1"
            }
        """
        )
        result = IMPORTER.get_text_unit(stub)
        assert result.model_dump(exclude_none=True) == {
            'ark': 'ark:/21198/s1308n',
            'label': 'Liturgical collection',
            'lang': [{'id': 'nucl1302', 'label': 'Georgian'}],
            'parent': ['ark:/21198/s18d1p'],
            'reconstruction': False,
            'work_wit': [
                {
                    'work': {
                        'desc_title': 'Liturgical collection',
                        'genre': [
                            {
                                'id': 'liturgical-texts',
                                'label': 'Liturgical texts',
                            },
                        ],
                    },
                },
            ],
        }

    def test_loads_all_text_units(self) -> None:
        n_files = 0
        for path in (IMPORTER.base_path / 'text_units').glob('*.json'):
            stub = st.TextUnitStub(id='ark:/21198/' + path.stem, label='whatevs')
            IMPORTER.get_text_unit(stub)
            n_files += 1
        assert n_files == 15


class TestGetLayer:
    def test_good_layer(self) -> None:
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
        result = IMPORTER.get_layer(stub).model_dump(exclude_none=True, round_trip=True)
        assert result == {
            'ark': 'ark:/21198/ten0p1ol',
            'reconstruction': False,
            'state': {'id': 'overtext', 'label': 'Overtext'},
            'label': 'Arabic NF M 28, Part 1, Overtext',
            'locus': 'ff. 128-143',
            'summary': 'Gospels, late 9th c., Arabic (Kufic)',
            'extent': '16 ff.',
            'writing': [
                {
                    'script': [
                        {
                            'id': 'kufic',
                            'label': 'Kufic',
                            'writing_system': 'Arabic',
                        }
                    ],
                    'locus': 'ff. 128-143',
                }
            ],
            'ink': [{'locus': 'ff. 128-143', 'note': ['Titles in red ink']}],
            'text_unit': [
                {
                    'ark': 'ark:/21198/ten0p1olt1',
                    'reconstruction': False,
                    'label': 'Arabic Gospels',
                    'locus': 'ff. 128r-143v',
                    'lang': [{'id': 'arab1395', 'label': 'Arabic'}],
                    'work_wit': [
                        {
                            'work': {
                                'ark': 'ark:/21198/s12c7r',
                                'pref_title': 'Matthew',
                                'alt_title': ['Bible. Matthew'],
                                'genre': [
                                    {
                                        'id': 'biblical-texts',
                                        'label': 'Biblical texts',
                                    },
                                    {'id': 'gospel-books', 'label': 'Gospel books'},
                                ],
                                'rel_con': [
                                    {
                                        'label': 'Bible. Matthew',
                                        'uri': st.AnyUrl(
                                            st.AnyUrl('https://viaf.org/viaf/188427863')
                                        ),
                                        'source': st.RelatedConceptSource.VIAF,
                                    },
                                    {
                                        'label': 'Bible. Matthew',
                                        'uri': st.AnyUrl(
                                            st.AnyUrl(
                                                'http://id.loc.gov/authorities/names/n79056834'
                                            )
                                        ),
                                        'source': st.RelatedConceptSource.LoC,
                                    },
                                ],
                                'refno': [],
                                'bib': [],
                            },
                            'locus': 'ff. 128r-130',
                        },
                        {
                            'work': {
                                'ark': 'ark:/21198/s1630k',
                                'pref_title': 'Mark',
                                'alt_title': ['Bible. Mark'],
                                'genre': [
                                    {
                                        'id': 'biblical-texts',
                                        'label': 'Biblical texts',
                                    },
                                    {'id': 'gospel-books', 'label': 'Gospel books'},
                                ],
                                'rel_con': [
                                    {
                                        'label': 'Bible. Mark',
                                        'uri': st.AnyUrl('https://viaf.org/viaf/179823714'),
                                        'source': st.RelatedConceptSource.VIAF,
                                    },
                                    {
                                        'label': 'Bible. Mark',
                                        'uri': st.AnyUrl(
                                            'http://id.loc.gov/authorities/names/n78095773'
                                        ),
                                        'source': st.RelatedConceptSource.LoC,
                                    },
                                ],
                                'refno': [],
                                'bib': [],
                            },
                            'locus': 'ff. 130v-135r',
                        },
                        {
                            'work': {
                                'ark': 'ark:/21198/s1k88r',
                                'pref_title': 'Luke',
                                'alt_title': ['Bible. Luke'],
                                'genre': [
                                    {
                                        'id': 'biblical-texts',
                                        'label': 'Biblical texts',
                                    },
                                    {'id': 'gospel-books', 'label': 'Gospel books'},
                                ],
                                'rel_con': [
                                    {
                                        'label': 'Bible. Luke',
                                        'uri': st.AnyUrl('http://viaf.org/viaf/257061095'),
                                        'source': st.RelatedConceptSource.VIAF,
                                    }
                                ],
                                'refno': [],
                                'bib': [],
                            },
                            'locus': 'ff. 135r-140r',
                        },
                        {
                            'work': {
                                'ark': 'ark:/21198/s1388d',
                                'pref_title': 'John',
                                'alt_title': ['Bible. John'],
                                'genre': [
                                    {
                                        'id': 'biblical-texts',
                                        'label': 'Biblical texts',
                                    },
                                    {'id': 'gospel-books', 'label': 'Gospel books'},
                                ],
                                'rel_con': [
                                    {
                                        'label': 'Bible. John',
                                        'uri': st.AnyUrl(
                                            'https://viaf.org/viaf/57145910123927021804'
                                        ),
                                        'source': st.RelatedConceptSource.VIAF,
                                    },
                                    {
                                        'label': 'Bible. John',
                                        'uri': st.AnyUrl(
                                            'http://id.loc.gov/authorities/names/n79060414'
                                        ),
                                        'source': st.RelatedConceptSource.LoC,
                                    },
                                ],
                                'refno': [],
                                'bib': [],
                            },
                            'locus': 'ff. 140v-143v',
                        },
                    ],
                    'features': [],
                    'note': [
                        {
                            'type': {'id': 'contents', 'label': 'Contents Note'},
                            'value': 'The Gospels continue in Arabic NF M 8 and NF M 27',
                        }
                    ],
                    'desc_provenance': {
                        'program': [
                            {
                                'label': 'Sinai Palimpests Project',
                                'description': 'Described as part of the Sinai Palimpsests Project (2006-2017). The Sinai Palimpsests Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from Arcadia. The Project provides scholarly identification and description of the undertext objects in a subset of palimpsested manuscripts in the Sinai collection, with minimal metadata for the overtexts of the host manuscripts.',
                            }
                        ]
                    },
                    'parent': ['ark:/21198/ten0p1ol'],
                    'internal': ['Test record, delete after development is complete'],
                }
            ],
            'assoc_date': [
                {
                    'type': {'id': 'origin', 'label': 'Origin Date'},
                    'note': ['Paleographic dating'],
                    'value': 'Second half 9th c. CE',
                    'iso': {'not_before': 851, 'not_after': 900},
                }
            ],
            'note': [
                {
                    'type': {'id': 'ornamentation', 'label': 'Ornamentation'},
                    'value': 'Decorative headpieces throughout',
                },
                {
                    'type': {'id': 'condition', 'label': 'Condition'},
                    'value': 'Several damaged folios were repaired and reinforced more recently',
                },
            ],
            'bib': [
                {
                    'id': st.UUID('36ac2d29-349f-496d-b4ea-aff4e605c4ba'),
                    'type': {'id': 'ref', 'label': 'Reference Work'},
                    'range': 'p. 48-90',
                }
            ],
            'parent': ['ark:/21198/ten02zkr'],
            'desc_provenance': {
                'program': [
                    {
                        'label': 'Sinai Palimpests Project',
                        'description': 'Described as part of the Sinai Palimpsests Project (2006-2017). The Sinai Palimpsests Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from Arcadia. The Project provides scholarly identification and description of the undertext objects in a subset of palimpsested manuscripts in the Sinai collection, with minimal metadata for the overtexts of the host manuscripts.',
                    }
                ]
            },
            'internal': ['Test record for development purposes; please delete.'],
        }

    def test_loads_all_layers(self) -> None:
        n_files = 0
        for path in (IMPORTER.base_path / 'layers').glob('*.json'):
            stub = st.LayerStub(
                id='ark:/21198/' + path.stem,
                label='whatevs',
                type={'id': 'what', 'label': 'ever'},
            )
            IMPORTER.get_layer(stub)
            n_files += 1
        assert n_files == 15


class TestGetMergedManuscript:
    def test_good_manuscript(self) -> None:
        with open(f'{BASE_PATH}/outputs/z1h13zxq.json', encoding='utf-8') as f:
            expected = json.load(f)

        result = IMPORTER.get_merged_manuscript(IMPORTER.base_path / 'ms_objs/z1h13zxq.json')

        assert json.loads(result.model_dump_json(exclude_none=True)) == expected

    @pytest.mark.xfail  # Don't seem to have good data here yet
    def test_loads_all_manuscripts(self) -> None:
        n_files = 0
        for path in (IMPORTER.base_path / 'ms_objs').glob('*.json'):
            IMPORTER.get_merged_manuscript(path)
            n_files += 1
        assert n_files == 15


class TestIterateMergedRecords:
    pass


class TestSaveMergedRecords:
    pass


class TestSolrRecord:
    def test_years(self) -> None:
        pass
