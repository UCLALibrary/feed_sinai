from typing import Optional, List

from pydantic import ValidationError
import pytest

import feed_sinai.sinai_types as st


class TestBaseModel:
    class OtherModel(st.BaseModel):
        child: "Optional[OtherModel]" = None
        b: int
        c: str

    class ExampleModel(st.BaseModel):
        children: "Optional[List[ExampleModel | OtherModel]]" = None
        a: int
        b: int

    def test_deep_get(self):
        test_obj = self.ExampleModel.model_validate(
            {
                "a": 1,
                "b": 1,
                "children": [
                    {"a": 2, "b": 3, "children": [{"a": 5, "b": 8}]},
                    {"a": 13, "b": 21},
                    {"child": {"b": 55, "c": "no"}, "b": 34, "c": "nope"},
                ],
            }
        )

        assert test_obj.deep_get("a", "b") == {1, 2, 3, 5, 8, 13, 21, 34, 55}


class TestLabelWithIdentifier:
    def test_happy_path(self):
        result = st.LabelWithIdentifier.model_validate_json(
            '{"id": "abc", "label": "123"}'
        )
        assert result.id == "abc"
        assert result.label == "123"

    def test_extra_field(self):
        with pytest.raises(ValidationError):
            st.LabelWithIdentifier.model_validate_json(
                '{"id": "abc", "label": "123"}, "other": "xyz"'
            )

    def test_missing_id(self):
        with pytest.raises(ValidationError):
            st.LabelWithIdentifier.model_validate_json('{"label": "123"}')

    def test_missing_value(self):
        with pytest.raises(ValidationError):
            st.LabelWithIdentifier.model_validate_json('{"id": "abc"}')

    def test_empty_id(self):
        with pytest.raises(ValidationError):
            st.LabelWithIdentifier.model_validate_json('{"id": ", "label": "123"}')

    def test_empty_value(self):
        with pytest.raises(ValidationError):
            st.LabelWithIdentifier.model_validate_json('{"id": "abc", "label": "}')


# class TestGender:
#     def test_man(self):
#         result = st.Gender({"id": "man", "label": "Man"})
#         assert result == st.Gender.man

#     def test_woman(self):
#         result = st.Gender({"id": "woman", "label": "Woman"})
#         assert result == st.Gender.woman

#     def test_other(self):
#         result = st.Gender({"id": "other", "label": "Other"})
#         assert result == st.Gender.other

#     def test_invalid_gender(self):
#         """With appologies to the xenogender community, we are only tracking 'man', 'woman', and 'other"""
#         with pytest.raises(ValueError):
#             st.Gender({"id": "something", "label": "else"})

#     def test_as_value(self):
#         class TestModel(BaseModel):
#             gender: st.Gender
#         result = TestModel.model_validate_json('{"id": "other", "label": "Other"}')
#         assert result.gender == st.Gender.other


class TestIso:
    def test_good_iso(self):
        result = st.Iso.model_validate_json(
            '{"not_before": "0010", "not_after": "0100"}'
        )
        assert result.not_before == "0010"
        assert result.not_after == "0100"

    def test_no_notafter(self):
        result = st.Iso.model_validate_json('{"not_before": "0010"}')
        assert result.not_before == "0010"
        assert result.not_after is None

    def test_no_notbefore(self):
        with pytest.raises(ValidationError):
            st.Iso.model_validate_json('{"not_after": "0010"}')


class TestDate:
    def test_good_date(self):
        st.Date.model_validate_json(
            """
            {
                "value": "4th c. CE",
                "iso": {
                    "not_before": "0301",
                    "not_after": "0400"
                }
            }
        """
        )


class TestRelConItem:
    def test_good_json(self):
        result = st.RelConItem.model_validate_json(
            """
            {
                "label": "Onuphrius, Saint, -approximately 400",
                "uri": "https://w3id.org/haf/person/232371232899",
                "source": "HAF"
            }
        """
        )
        assert result.label == "Onuphrius, Saint, -approximately 400"
        assert result.source == st.RelatedConceptSource.HAF

    def test_invalid_source(self):
        with pytest.raises(ValidationError):
            st.RelConItem.model_validate_json(
                """
                {
                    "label": "Onuphrius, Saint, -approximately 400",
                    "uri": "https://w3id.org/haf/person/232371232899",
                    "source": "UCLA"
                }
            """
            )


class TestRefnoItem:
    def test_good_json(self):
        result = st.RefnoItem.model_validate_json(
            """
            {
                "label": "Homiliae super psalmos",
                "idno": "2836.001",
                "source": "CPG"
            }
        """
        )
        assert result.idno == "2836.001"


class TestBibItem:
    def test_good_json(self):
        result = st.BibItem.model_validate_json(
            """
            {
                "id": "deb668b6-feec-4828-8749-a97441881226",
                "type": {
                    "id": "ref",
                    "label": "Reference"
                },
                "range": "[141], p. 156"
            }
        """
        )
        assert result.type.id == "ref"


# @pytest.mark.xfail
# class TestRelItem:
#     """Not currently used in the data"""
#     raise NotImplementedError


# @pytest.mark.xfail
# class TestRelAgentItem:
#     """Not currently used in the data"""
#     raise NotImplementedError


# @pytest.mark.xfail
# class TestRelPlaceItem:
#     """Not currently used in the data"""
#     raise NotImplementedError


# @pytest.mark.xfail
# class TestCataloguerItem:
#     """Not currently used in the data"""
#     raise NotImplementedError


class TestAgent:
    def test_good_json(self):
        result = st.Agent.model_validate_json(
            """
        {
            "ark": "ark:/21198/s1d01s",
            "type": {"id": "person", "label": "Person"},
            "pref_name": "Theodore the Studite",
            "alt_name": [
                "Theodore Studites"
            ],
            "gender": {"id": "man", "label": "Man"},
            "floruit": {
                "value": "759 CE-826 CE",
                "iso": {
                    "not_before": "0759",
                    "not_after": "0826"
                }
            },
            "rel_con": [
                {
                    "label": "Theodore, Studites, Saint, 759-826",
                    "uri": "http://viaf.org/viaf/62875165",
                    "source": "VIAF"
                },
                {
                    "label": "Theodore, Studites, Saint, 759-826",
                    "uri": "https://id.loc.gov/authorities/names/n81118597",
                    "source": "LoC"
                },
                {
                    "label": "Theodore, Studites, 759-826",
                    "uri": "https://w3id.org/haf/person/636228715607",
                    "source": "HAF"
                },
                {
                    "label": "Theodorus Studita",
                    "uri": "https://pinakes.irht.cnrs.fr/notices/auteur/2685/",
                    "source": "Pinakes"
                }
            ]
        }
        """
        )
        assert str(result.rel_con[2].uri) == "https://w3id.org/haf/person/636228715607"

    def test_bad_ark(self):
        with pytest.raises(ValidationError, match="String should match pattern"):
            st.Agent.model_validate_json(
                """
            {
                "ark": "21198/s1d01s",
                "type": {"id": "person", "label": "Person"},
                "pref_name": "Theodore the Studite"
            }
            """
            )


class TestWritingItem:
    def test_good_writing_item(self):
        st.WritingItem.model_validate_json(
            """
            {
                "script": [
                    {
                        "id": "nuskhurimt",
                        "label": "Nuskhurimt",
                        "writing_system": "Georgian"
                    }
                ],
                "note": [
                    "Relatively thick and clumsy"
                ]
            }
        """
        )


class TestInkItem:
    def test_good_ink_item(self):
        st.InkItem.model_validate_json(
            """
            { 
                "locus": "ff. 55v-144v", 
                "color": [ 
                    "dark brown" 
                ], 
                "note": [ 
                    "Rubrication of titles in red ink" 
                ] 
            } 
        """
        )


class TestLayoutItem:
    def test_good_layout_item(self):
        st.LayoutItem.model_validate_json(
            """
            {
                "locus": "ff. 3r-54v",
                "columns": "1",
                "lines": "15",
                "dim": "Writing area: 215 x 140 mm",
                "note": [
                    "Possible pricking still visible in outer margins throughout",
                    "Text written inside bordered margins"
                ]
            }
        """
        )


class TestUnitItem:
    def test_good_text_unit_item(self):
        st.TextUnitStub.model_validate_json(
            """
            {
                "id": "ark:/21198/s1w103",
                "label": "Item 1"
            }
        """
        )


class TestAssocNameItem:
    def test_good_assoc_name_item(self):
        st.AssocNameItem.model_validate_json(
            """
            { 
                "id": "ark:/21198/s1v887", 
                "as_written": "ܝܘܚܢܢ ܒܪܝ ܬܐܘܕܘܪܘܣ", 
                "role": { 
                    "id": "scribe", 
                    "label": "Scribe" 
                }, 
                "note": [ 
                    "The ARK is for Ephrem, to demo functionality" 
                ] 
            }
        """
        )


class TestAssocPlaceItem:
    def test_good_assoc_place_item(self):
        st.AssocPlaceItem.model_validate_json(
            """
            {
                "value": "Possibly Jerusalem",
                "event": {
                    "id": "origin",
                    "label": "Place of Origin"
                }
            }
        """
        )


class TestAssocDateItem:
    def test_good_assoc_date_item(self):
        st.AssocDateItem.model_validate_json(
            """
            { 
                "type": { 
                    "id": "origin", 
                    "label": "Origin Date" 
                }, 
                "note": [ 
                    "Paleographic dating" 
                ], 
                "value": "Second half 9th c. CE", 
                "iso": { 
                    "not_before": "0851", 
                    "not_after": "0900" 
                } 
            }
        """
        )


class TestParaItem:
    def test_good_para_item(self):
        st.ParaItem.model_validate_json(
            """
            {
                "type": {
                    "id": "colophon",
                    "label": "Colophon"
                },
                "locus": "99r",
                "lang": [
                    {
                        "id": "class1252",
                        "label": "Syriac"
                    }
                ],
                "as_written": "ܐܫܠܡ ܒܥܘܕܪܢ ܐܠܗܐ ܡܢܘ ܕܬܝܒ̄ܘ ܥܠ ܐܦܝ ܬܫܥ ܫ̈ܥܝܢ ܝܘܡ ܕܬܪܝܐ ܒ̄ܛ ܒܐܕܐܪ ܫܢܬ ܐܠܦ ܘܚܡܫ̄ ܡ̄ܘ ܡ̣ܢ ܕܐܠܣܟܢ̄ܕܪ ܟܬܒܗ̣ ܕܝܢ ܐܢܫ ܡܚܲܝܠܐ ܘܚܛܝܐ ܘܒܨ̇ܝܪܐ ܕܟܠܗܘܢ ܒܢ̈ܝܗܫܐ ܦܝܡ ܣ ܠܡܬ ܥܡ ܨܐܕܝܬ̤ ܒܪ ܨ̇ܗܘܝ ܡ̣ܢ ܩܪܝܬ̤ ܡܒܪܟܬܐ ܘܪܚܡܬ̤ ܠܡܫܝ̣ܚܐ ܨܕܐܢܝ ܡܢܝܚ ܡܪܝܐ ܢܦܫܗ̣ ܥܡ ܟܠܗܘܢ ܩܕܝܫܘ̈ܗܝ ܐܡܝܢ"
            }
        """
        )


class TestRelatedMs:
    def test_good_related_ms(self):
        st.RelatedMs.model_validate_json(
            """
            { 
                "type": { 
                    "id": "filiation", 
                    "label": "Filiation" 
                }, 
                "label": "Copied from Syriac 10", 
                "mss": [
                    { 
                        "label": "Sinai Syriac 10", 
                        "id": "ark:/21198/z1p57n0b" 
                    } 
                ], 
                "note": [ 
                    "This is a dummy note for dev purposes" ,
                    "Otherwise largely lost"
                ] 
            } 
        """
        )

    def test_no_ms_id(self):
        st.RelatedMs.model_validate_json(
            """
            { 
                "type": { 
                    "id": "disjecta", 
                    "label": "Disjecta Membra" 
                }, 
                "label": "Disjecta Membra from the final quire", 
                "note": [ 
                    "The last 4 folios are today Biblioteca Ambrosiana, A 296 inf., ff. 70–73 = Chabot 20 (4 ff.) + Mingana Syr. 632 (1 f.)" ,
                    "Identification of disjecta membra by Rossetto"
                ], 
                "mss": [
                    { 
                        "label": "Biblioteca Ambrosiana, A 296 inf., ff. 70–73 = Chabot 20 (4 ff.)", 
                        "url": "https://archive.org/details/ChabotInventaireDesFragmentsDeMssSyriaquesConservesALaBibliothequeAmbrosienneAMilan/page/n3/mode/2up" 
                    }, 
                    { 
                        "label": "Mingana Syr. 632 (1 f.)", 
                        "url": "http://epapers.bham.ac.uk/160" 
                    } 
                ] 
            }
        """
        )


class TestNoteItem:
    def test_good_note_item(self):
        """ "Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/layers/s18d1p.json"""

        st.NoteItem.model_validate_json(
            """
            {
                "type": {
                    "id": "general",
                    "label": "Other Notes"
                },
                "value": "Many additions and erasures in overtext"
            }
        """
        )


class TestInscribedLayer:
    def test_good_inscribed_layer(self):
        """ "Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/layers/s18d1p.json"""

        st.InscribedLayer.model_validate_json(
            """
            {
                "ark": "ark:/21198/s18d1p",
                "reconstruction": false,
                "label": "Sinai Georgian 34, Overtext (Undetermined (Georgian))",
                "state": {
                    "id": "overtext",
                    "label": "Overtext"
                },
                "writing": [
                    {
                        "script": [
                            {
                                "id": "georgian-undetermined",
                                "label": "Undetermined (Georgian)",
                                "writing_system": "Georgian"
                            }
                        ]
                    }
                ],
                "ink": [
                    {
                        "color": [
                            "black",
                            "red"
                        ],
                        "note": [
                            "Red used for rubrics"
                        ]
                    }
                ],
                "text_unit": [
                    {
                        "id": "ark:/21198/s1308n",
                        "label": "Item 1"
                    }
                ],
                "features": [
                    {
                        "id": "dated",
                        "label": "Dated"
                    }
                ],
                "assoc_date": [
                    {
                        "type": {
                            "id": "origin",
                            "label": "Date of Origin"
                        },
                        "value": "932  CE",
                        "iso": {
                            "not_before": "0932"
                        }
                    }
                ],
                "note": [
                    {
                        "type": {
                            "id": "general",
                            "label": "Other Notes"
                        },
                        "value": "Many additions and erasures in overtext"
                    }
                ],
                "parent": [
                    "ark:/21198/z1h13zxq"
                ]
            }
        """
        )


class TestLayerStub:
    def test_good_LayerStub(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        st.LayerStub.model_validate_json(
            """
            { 
                "id": "ark:/21198/te5fp1ol", 
                "label": "Overtext layer (13th c., Melkite)", 
                "type": { 
                    "id": "overtext", 
                    "label": "Overtext" 
                }, 
                "locus": "ff. 3r-54v" 
            } 
        """
        )


class TestPart:
    def test_good_Part(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        st.Part.model_validate_json(
            """
            { 
                "label": "Part 1", 
                "summary": "Synaxarion (Gospel Lectionary for the movable feast days according to the Byzantine rite)", 
                "locus": "ff. 3-54", 
                "support": [
                    { 
                        "id": "paper", 
                        "label": "Paper" 
                    } 
                ], 
                "extent": "51 ff.", 
                "dim": "235 x 154 mm (average folio)", 
                "layer": [
                    { 
                        "id": "ark:/21198/te5fp1ol", 
                        "label": "Overtext layer (13th c., Melkite)", 
                        "type": { 
                            "id": "overtext", 
                            "label": "Overtext" 
                        }, 
                        "locus": "ff. 3r-54v" 
                    } 
                ], 
                "note": [
                    { 
                        "type": 
                        { 
                            "id": "support", 
                            "label": "Support" 
                        }, 
                        "value": "Oriental paper" 
                    }, 
                    { 
                        "type": 
                        { 
                            "id": "collation", 
                            "label": "Collation" 
                        }, 
                        "value": "Quire signatures in the first part are marked in the bottom margin on the recto side of the first folio of a quire; quires of 8 ff. with the exception of quire II (6 ff.)" 
                    }, 
                    { 
                        "type": 
                        { 
                            "id": "collation", 
                            "label": "Collation" 
                        }, 
                        "value": "F. 11 may be a replacement" 
                    }, 
                    { 
                        "type": 
                        { 
                            "id": "collation", 
                            "label": "Collation" 
                        }, 
                        "value": "One f. missing after f. 17" 
                    } 
                ] 
            }
        """
        )


class TestLocationItem:
    def test_good_LocationItem(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        st.LocationItem.model_validate_json(
            """
            { 
                "id": "sinai-oc", 
                "collection": "Old Collection" ,
                "repository": "St. Catherine's Monastery of the Sinai"
            }
        """
        )


class TestViscodexItem:
    def test_good_ViscodexItem(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        st.ViscodexItem.model_validate_json(
            """
            { 
                "type": { 
                    "id": "manuscript", 
                    "label": "Manuscript" 
                }, 
                "label": "Viscodex for Syriac 12", 
                "url": "https://vceditor.library.upenn.edu/project/668da6f75d69680001457684/viewOnly" 
            }
        """
        )


class TestIiifItem:
    def test_good_IiifItem(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        st.IiifItem.model_validate_json(
            """
            { 
                "type": { 
                    "id": "main", 
                    "label": "Main" 
                }, 
                "manifest": "https://ingest.iiif.library.ucla.edu/ark%3A%2F21198%2Fz15f0f9b/manifest", 
                "text_direction": "right-to-left", 
                "behavior": "paged", 
                "thumbnail": "https://iiif.sinaimanuscripts.library.ucla.edu/iiif/2/ark%3A%2F21198%2Fz15f0f9b%2Fp161m45m/full/!200,200/0/default.jpg" 
            }
        """
        )


class TestManuscriptObject:
    def test_good_ManuscriptObject(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/ms_objs/te5f0f9b.json"""

        result = st.ManuscriptObject.model_validate_json(
            """
            { 
                "ark": "ark:/21198/te5f0f9b", 
                "reconstruction": false, 
                "type": { 
                    "id": "manuscript", 
                    "label": "Manuscript" 
                }, 
                "shelfmark": "Sinai Syriac 12", 
                "summary": "(1st part) Synaxarion (Gospel Lectionary for the movable feast days according to the Byzantine rite); (2nd part) Gospel of Luke (Peshitta version)", 
                "extent": "146 ff.", 
                "weight": "1287.7 g", 
                "dim": "240 x 159 x 81.0 mm", 
                "state": { 
                    "id": "codex", 
                    "label": "Codex" 
                }, 
                "fol": "ff. 1-2a, 2b-45, 45bis-144", 
                "coll": "Fly-leaves: Front board inside (pastedown), ff. 1-2b | Part 1: <I>: ff. 3–10; <II>: ff. 11–16; <III>: ff. 17–23; IV: ff. 24–31; V: ff. 32–39; VI: ff. 40–46; VII: ff. 47–54 | Part 2: <I>: ff. 55–63; <II>: ff. 64–72; <III>: ff. 73–82; <IV>: ff. 83–92; <V>: ff. 93–102; <VI>: ff. 103–112; <VII>: ff. 113–122; <VIII>: ff. 123–132; IX: ff. 133–142; <X>: ff. 143–144", 
                "features": [
                    { 
                        "id": "headpiece", 
                        "label": "Headpiece(s)" 
                    }, 
                    { 
                        "id": "deco-geometric", 
                        "label": "Decoration, Geometric" 
                    }, 
                    { 
                        "id": "deco-vegetative", 
                        "label": "Decoration, Vegetative" 
                    }, 
                    { 
                        "id": "border", 
                        "label": "Border(s)" 
                    } 
                ], 
                "part": [
                    { 
                        "label": "Part 1", 
                        "summary": "Synaxarion (Gospel Lectionary for the movable feast days according to the Byzantine rite)", 
                        "locus": "ff. 3-54", 
                        "support": [
                            { 
                                "id": "paper", 
                                "label": "Paper" 
                            } 
                        ], 
                        "extent": "51 ff.", 
                        "dim": "235 x 154 mm (average folio)", 
                        "layer": [
                            { 
                                "id": "ark:/21198/te5fp1ol", 
                                "label": "Overtext layer (13th c., Melkite)", 
                                "type": { 
                                    "id": "overtext", 
                                    "label": "Overtext" 
                                }, 
                                "locus": "ff. 3r-54v" 
                            } 
                        ], 
                        "note": [
                            { 
                                "type": 
                                { 
                                    "id": "support", 
                                    "label": "Support" 
                                }, 
                                "value": "Oriental paper" 
                            }, 
                            { 
                                "type": 
                                { 
                                    "id": "collation", 
                                    "label": "Collation" 
                                }, 
                                "value": "Quire signatures in the first part are marked in the bottom margin on the recto side of the first folio of a quire; quires of 8 ff. with the exception of quire II (6 ff.)" 
                            }, 
                            { 
                                "type": 
                                { 
                                    "id": "collation", 
                                    "label": "Collation" 
                                }, 
                                "value": "F. 11 may be a replacement" 
                            }, 
                            { 
                                "type": 
                                { 
                                    "id": "collation", 
                                    "label": "Collation" 
                                }, 
                                "value": "One f. missing after f. 17" 
                            } 
                        ] 
                    }, 
                    { 
                        "label": "Part 2", 
                        "summary": "Gospel of Luke (Peshitta version)", 
                        "locus": "ff. 55-144", 
                        "support": [
                            { 
                                "id": "parchment", 
                                "label": "Parchment" 
                            }
                        ], 
                        "extent": "89 ff.", 
                        "dim": "230 x 155 mm (average folio)", 
                        "layer": [
                            { 
                                "id": "ark:/21198/te5fp2ol", 
                                "label": "Overtext layer (early 7th c., Estrangela)", 
                                "type": { 
                                    "id": "overtext", 
                                    "label": "Overtext" 
                                }, 
                                "locus": "ff. 55v-144v" 
                            } 
                        ], 
                        "para": [
                            { 
                                "type": { 
                                    "id": "transfer-of-ownership", 
                                    "label": "Transfer of Ownership" 
                                },
                                "locus": "f. 55r", 
                                "lang": [
                                    { 
                                        "id": "gree1276", 
                                        "label": "Greek" 
                                    } 
                                ], 
                                "script": [
                                    { 
                                        "id": "greek-min", 
                                        "label": "Greek minuscule" ,
                                        "writing_system": "Greek"
                                    } 
                                ], 
                                "label": "Greek inscription", 
                                "as_written": "Κατ ἐκεῖνον τὸν καιρὸν ἦμεν πάντες οἱ ἀπόστολοι ἐν Ἰεροσολύμοις, Σίμων ὁ λεγόμενος Πέτρος καὶ Ἀνδρέας ὁ ἀδελφὸς αὐτοῦ, Ἰάκωβος ὁ τοῦ Ζεβεδαίου καὶ Ἰωάννης ὁ ἀδελφὸς αὐτοῦ, Φίλιππος καὶ Βαρθολομαῖος, Θωμᾶς καὶ Ματθαῖος ὁ τελώνης, Ἰάκωβος Ἁλφαίου καὶ Σίμων ὁ Καναναῖος", 
                                "translation": [ 
                                    "At that season all we the apostles were at Jerusalem, Simon which is called Peter and Andrew his brother, James the son of Zebedee and John his brother, Philip and Bartholomew, Thomas and Matthew the publican, James the son of Alphaeus and Simon the Canaanite", 
                                    "Another translation of the text for demo purposes" 
                                ], 
                                "assoc_name": [
                                    { 
                                        "id": "ark:/21198/s1v30g", 
                                        "as_written": "Πέτρος", 
                                        "role": { 
                                            "id": "former-owner", 
                                            "label": "Former Owner" 
                                        }, 
                                        "note": [ 
                                            "Demo data. Maximus the Confessor sold this manuscript to Paul the Deacon." 
                                        ] 
                                    }, 
                                    { 
                                        "id": "ark:/21198/s1t598", 
                                        "as_written": "Ἀνδρέας", 
                                        "role": { 
                                            "id": "former-owner", 
                                            "label": "Former Owner" 
                                        }, 
                                        "note": [ 
                                            "Demo data. Paul the Deacon bought this manuscript from Maximus the Confessor." 
                                        ] 
                                    } 
                                ], 
                                "assoc_place": [
                                    { 
                                        "value": "Jerusalem", 
                                        "as_written": "Ἰεροσολύμοις", 
                                        "event": { 
                                            "id": "transfer-of-owernship", 
                                            "label": "Place of Ownwership Transfer" 
                                        }, 
                                        "note": [ 
                                            "ARK constructed for demo purposes" 
                                        ] 
                                    } 
                                ], 
                                "assoc_date": [
                                    { 
                                        "type": { 
                                            "id": "transfer-of-ownership", 
                                            "label": "Transfer of Ownership" 
                                        }, 
                                        "as_written": "Κατ ἐκεῖνον τὸν καιρὸν", 
                                        "note": [ 
                                            "There is no real date here, just for demo purposes" 
                                        ], 
                                        "value": "455 CE", 
                                        "iso": { 
                                            "not_before": "0455-01-01" 
                                        } 
                                    } 
                                ], 
                                "note": [ 
                                    "Originally left blank, f. 55r was later was covered with text in Greek minuscule oriented upside down relative to the main contents" 
                                ] 
                            } 
                        ], 
                        "note": [
                            { 
                                "type": { 
                                    "id": "foliation", 
                                    "label": "Foliation" 
                                }, 
                                "value": "Recent foliation in Syriac numerals covering the earlier part (ff. 55–144). The foliation was added after a replacement folio (f. 68) was attached but before two parts were bound together." 
                            }, 
                            { 
                                "type": { 
                                    "id": "collation", 
                                    "label": "Collation" 
                                }, 
                                "value": "Only the quire IX has preserved a quire signature in the bottom margin of the first folio; quires of 10 ff." 
                            }, 
                            { 
                                "type": { 
                                    "id": "collation", 
                                    "label": "Collation" 
                                }, 
                                "value": "The first folio of part 2's first quire, left blank, is lost; a central bifolium in the second was replaced with a single folio ca. 8th–9th c." 
                            } 
                        ], 
                        "related_mss": [
                            { 
                                "type": { 
                                    "id": "disjecta", 
                                    "label": "Disjecta Membra" 
                                }, 
                                "label": "Disjecta Membra from the final quire", 
                                "note": [ 
                                    "The last 4 folios are today Biblioteca Ambrosiana, A 296 inf., ff. 70–73 = Chabot 20 (4 ff.) + Mingana Syr. 632 (1 f.)" ,
                                    "Identification of disjecta membra by Rossetto"
                                ], 
                                "mss": [
                                    { 
                                        "label": "Biblioteca Ambrosiana, A 296 inf., ff. 70–73 = Chabot 20 (4 ff.)", 
                                        "url": "https://archive.org/details/ChabotInventaireDesFragmentsDeMssSyriaquesConservesALaBibliothequeAmbrosienneAMilan/page/n3/mode/2up" 
                                    }, 
                                    { 
                                        "label": "Mingana Syr. 632 (1 f.)", 
                                        "url": "http://epapers.bham.ac.uk/160" 
                                    } 
                                ] 
                            } 
                        ] 
                    } 
                ], 
                "layer": [
                    { 
                        "id": "ark:/21198/te5fmsg1", 
                        "label": "Reinforcement strips from a Melkite paper manuscript", 
                        "type": { 
                            "id": "guest", 
                            "label": "Guest Content" 
                        }, 
                        "locus": "ff. 58–64, 142–144" 
                    }, 
                    { 
                        "id": "ark:/21198/te5fmsg2", 
                        "label": "Reinforcement strips from a Syriac parchment codex", 
                        "type": { 
                            "id": "guest", 
                            "label": "Guest Content" 
                        }, 
                        "locus": "ff. 64–66, 70–72, 105–106, 110–111, 113–114" 
                    }, 
                    { 
                        "id": "ark:/21198/te5fmsg3", 
                        "label": "Reinforcement strips from a parchment Arabic (?) codex", 
                        "type": { 
                            "id": "guest", 
                            "label": "Guest Content" 
                        }, 
                        "locus": "ff. 55–56, 57–58, 58–59" 
                    } 
                ], 
                "para": [
                    { 
                        "type": { 
                            "id": "prayer-request", 
                            "label": "Prayer Request" 
                        }, 
                        "locus": "Front board inside, f. 1", 
                        "lang": [
                            { 
                                "id": "arab1395", 
                                "label": "Arabic" 
                            } 
                        ], 
                        "script": [
                            { 
                                "id": "naskh", 
                                "label": "Naskh" ,
                                "writing_system": "Arabic"
                            } 
                        ], 
                        "label": "Anonymous theological text", 
                        "as_written": "وصلي على كاتبه الحقير", 
                        "translation": [ 
                            "Pray for the despised scribe [of this text]" 
                        ], 
                        "note": [ 
                            "Seems to be a part of a longer letter" 
                        ] 
                    }, 
                    { 
                        "type": { 
                            "id": "reader-note", 
                            "label": "Reader's Note" 
                        }, 
                        "locus": "f. 2a", 
                        "lang": [
                            { 
                                "id": "clas1252", 
                                "label": "Syriac" 
                            } 
                        ], 
                        "script": [
                            { 
                                "id": "melkite", 
                                "label": "Melkite" ,
                                "writing_system": "Syriac"
                            } 
                        ], 
                        "label": "Unidentified Melkite text", 
                        "as_written": "ܗܘ ܕܝܢ ܩܕܝܫܐ ܡܪܝ ܐܦܪܝܡ ܐܝܬܘܗܝ ܗܘ̣ܐ ܒܓܢܣܗ ܣܘܪܝܝܐ. ܐܒܘܗܝ ܕܝܢ ܐܝܬܘܗܝ ܗܘ̣ܐ ܡܢ ܢܨܝܒܝܢ ܕܒܝܬ ܬܚܘ̈ܡܐ: ܥܕܟܝܠ ܓܝܪ ܠܐ ܫܩܝܠܐ ܗܘ̣ܬ ܠܦܪ̈ܣܝܐ: ܐܡܗ ܕܝܢ ܐܝܬܝܗܿ ܗܘ̣ܬ ܡܢ ܐܡܕ ܡܕܝܢܬܐ", 
                        "translation": [ 
                            "Saint Mar Ephrem was Syrian, by way of his family. His father was from Nisibis, on the border, when it had not yet been taken by the Persians; his mother was from the city of Amid", 
                            "Saint Mar Éphrem était par sa famille Syrien. Son père provenait de Nisibe aux confins du pays, non encore prise par les Perses; sa mère provenait de la ville d’Amid" 
                        ], 
                        "assoc_name": [
                            { 
                                "id": "ark:/21198/s1v887", 
                                "as_written": "ܡܪܝ ܐܦܪܝܡ", 
                                "role": { 
                                    "id": "reader", 
                                    "label": "Reader" 
                                }, 
                                "note": [ 
                                    "Ephrem is included here likely as the subject of the hagiography" 
                                ] 
                            } 
                        ], 
                        "assoc_place": [
                            { 
                                "id": "Nisibis", 
                                "as_written": "ܢܨܝܒܝܢ", 
                                "event": { 
                                    "id": "unknown", 
                                    "label": "Unknown" 
                                }, 
                                "note": [ 
                                    "In practice, we likely would not include this place since it's not about the ms itself, this is just for development" 
                                ] 
                            }, 
                            { 
                                "id": "Amid", 
                                "as_written": "ܐܡܕ", 
                                "event": { 
                                    "id": "birth", 
                                    "label": "Place of Birth" 
                                }, 
                                "note": [ 
                                    "In practice, we likely would not include this place since it's not about the ms itself, this is just for development" 
                                ] 
                            } 
                        ], 
                        "assoc_date": [
                            { 
                                "type": { 
                                    "id": "reading", 
                                    "label": "Reading Date" 
                                }, 
                                "as_written": "ܠܦܪ̈ܣܝܐ", 
                                "note": [ 
                                    "There is no real date here, just for demo purposes" 
                                ], 
                                "value": "AG 1092 (= 781/2 CE)", 
                                "iso": { 
                                    "not_before": "0781-01-01", 
                                    "not_after": "0782-01-01" 
                                } 
                            } 
                        ], 
                        "note": [ 
                            "Text yet to be identified, appears to be a hagiographic excerpt" 
                        ] 
                    } 
                ], 
                "has_bind": true, 
                "location": [
                    { 
                        "id": "sinai-oc", 
                        "collection": "Old Collection" ,
                        "repository": "St. Catherine's Monastery of the Sinai"
                    } 
                ], 
                "assoc_date": [
                    { 
                        "type": { 
                            "id": "binding", 
                            "label": "Binding Date" 
                        }, 
                        "note": [ 
                            "Binding dates estimated from origin dates of the two parts" 
                        ], 
                        "value": "After the 13th c. CE", 
                        "iso": { 
                            "not_before": "1301-01-01", 
                            "not_after": "1550-01-01" 
                        } 
                    } 
                ], 
                "assoc_name": [
                    { 
                        "value": "Moses of Nisibis", 
                        "role": { 
                            "id": "former-owner", 
                            "label": "Former Owner" 
                        }, 
                        "note": [ 
                            "From external accounts of the library of Moses of Nisibis, it appears he was once an owner of this manuscript in its current form" 
                        ] 
                    } 
                ], 
                "assoc_place": [
                    { 
                        "value": "Deir al-Suryan", 
                        "event": { 
                            "id": "previous-repository", 
                            "label": "Previous Repository" 
                        }, 
                        "note": [ 
                            "Formed part of the collection of Moses of Nisibis while he was abbat at Deir al-Suryan, before it was eventually transferred to Sinai" 
                        ] 
                    } 
                ], 
                "note": [
                    { 
                        "type": { 
                            "id": "binding", 
                            "label": "Binding" 
                        }, 
                        "value": "Two binding boards" 
                    }, 
                    { 
                        "type": { 
                            "id": "foliation", 
                            "label": "Foliation" 
                        }, 
                        "value": "Ff. 1-2b are paper fly-leaves" 
                    }, 
                    { 
                        "type": { 
                            "id": "binding", 
                            "label": "Binding" 
                        }, 
                        "value": "Reinforcement strips derive from a Melkite paper manuscript (ff. 58–64, 142–144), a Syriac parchment codex (ff. 64–66, 70–72, 105–106, 110–111, 113–114), and a parchment Arabic (?) codex (ff. 55–56, 57–58, 58–59)" 
                    } ,
                    {
                        "type": {
                            "id": "ornamentation",
                            "label": "Ornamentation Note"
                        },
                        "value": "Illustration, St. Matthew in a scriptorium, front board inside"
                    },
                    {
                        "type": {
                            "id": "ornamentation",
                            "label": "Ornamentation Note"
                        },
                        "value": "Decoration on Back Board Inside, triangle with radiating lines"
                    },
                    {
                        "type": {
                            "id": "para",
                            "label": "Paracontent Note"
                        },
                        "value": "Donation inscription at the bottom of f. 171v | Supplication inscription on f. 172v"
                    },
                    {
                        "type": {
                            "id": "general",
                            "label": "Other Notes"
                        },
                        "value": "Three cords as bookmarks (labelled f. 58r-2, photographed laid on f. 58r)"
                    },
                    {
                        "type": {
                            "id": "general",
                            "label": "Other Notes"
                        },
                        "value": "F. 28b is a smaller insert"
                    }
                ], 
                "related_mss": [
                    { 
                        "type": { 
                            "id": "filiation", 
                            "label": "Filiation" 
                        }, 
                        "label": "Copied from Syriac 10", 
                        "mss": [
                            { 
                                "label": "Sinai Syriac 10", 
                                "id": "ark:/21198/z1p57n0b" 
                            } 
                        ], 
                        "note": [ 
                            "This is a dummy note for dev purposes" ,
                            "Otherwise largely lost"
                        ] 
                    } 
                ], 
                "viscodex": [
                    { 
                        "type": { 
                            "id": "manuscript", 
                            "label": "Manuscript" 
                        }, 
                        "label": "Viscodex for Syriac 12", 
                        "url": "https://vceditor.library.upenn.edu/project/668da6f75d69680001457684/viewOnly" 
                    }, 
                    { 
                        "type": { 
                            "id": "reconstruction", 
                            "label": "Reconstruction" 
                        }, 
                        "label": "Visualization of part 2 + disjecta membra", 
                        "url": "https://vceditor.library.upenn.edu/project/668da6005d6968000145728e/viewOnly" 
                    } 
                ], 
                "bib": [
                    { 
                        "id": "deb668b6-feec-4828-8749-a97441881226", 
                        "type": { 
                            "id": "ref", 
                            "label": "Reference Work" 
                        }, 
                        "range": "[50], pg. 152", 
                        "alt_shelf": "Syr. 435",
                        "note": [ 
                            "Kamil misidentifies this manuscript with Syriac 435" 
                        ] 
                    }, 
                    {
                        "id": "ce9cdae8-81ce-4c29-8431-ab599cd5491c",
                        "type": {
                            "id": "ref",
                            "label": "Reference Work"
                        },
                        "range": "pg. 134-344",
                        "note": [
                            "Gwilliam, et al. were the first to note that there are two parts in this manuscript."
                        ]
                    },
                    { 
                        "id": "ec7c937f-655a-4459-b327-3793637b9db9", 
                        "type": { 
                            "id": "otherdigversion", 
                            "label": "Other Digital Version" 
                        }, 
                        "url": "https://www.loc.gov/item/00279386334-ms/", 
                        "note": [ 
                            "LoC microfilms" 
                        ] 
                    } ,
                    {
                        "id": "467167dd-e012-4f87-a1c8-cd8a79c3e8d5",
                        "type": {
                            "id": "cite",
                            "label": "Citation"
                        },
                        "range": "no. 437, pg. 45-50"
                    },
                    {
                        "id": "6e8ae70b-30a1-4bff-87d8-69a54cdc3a7b",
                        "type": {
                            "id": "cite",
                            "label": "Citation"
                        }
                    },
                    {
                        "id": "5256f5da-f751-4cdc-85ce-35b9b20ae818",
                        "type": {
                            "id": "otherdigversion",
                            "label": "Other Digital Version"
                        },
                        "url": "https://www.nli.org.il/en/manuscripts/NNL_ALEPH990038917380205171/NLI",
                        "note": [
                            "Using CPG ID for dev purposes since we are missing a bibl for NLI..."
                        ]
                    }
                ], 
                "iiif": [
                    { 
                        "type": { 
                            "id": "main", 
                            "label": "Main" 
                        }, 
                        "manifest": "https://ingest.iiif.library.ucla.edu/ark%3A%2F21198%2Fz15f0f9b/manifest", 
                        "text_direction": "right-to-left", 
                        "behavior": "paged", 
                        "thumbnail": "https://iiif.sinaimanuscripts.library.ucla.edu/iiif/2/ark%3A%2F21198%2Fz15f0f9b%2Fp161m45m/full/!200,200/0/default.jpg" 
                    } 
                ],
                "desc_provenance": {
                    "program": [
                        {
                            "label": "Sinai Library Digitization Project, Phase 1",
                            "description": "Described as part of the Sinai Library Digitization Project, Phase 1 (2018-2022). The Sinai Library Digitization Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from The Ahmanson Foundation, Arcadia, and the Steinmetz Family Foundation. Phase 1 of the Sinai Library Digitization Project aimed to supply minimal metadata to accompany high-resolution images of the Arabic and Syriac manuscripts held in the Monastery’s library."
                        },
                        {
                            "label": "Syriac Parchment Descriptions Project",
                            "description": "Described as part of the Syriac Parchment Descriptions Project (2022-2025). The Syriac Parchment Descriptions Project was funded by a National Endowment for the Humanities grant. It aimed to provide full and detailed cataloguing of the Syriac manuscripts on parchment in the Sinai collection. Lead Cataloguer: Grigory Kessel; Research Associates: Natalia Smelova and Vevian Zaki."
                        }
                    ],
                    "rights": "UUnless otherwise indicated all metadata associated with this manuscript is copyright the authors and released under Creative Commons Attribution 4.0 International License."
                },
                "image_provenance": {
                    "program": [
                        {
                            "label": "Sinai Palimpests Project",
                            "description": "Imaged as part of the Sinai Palimpsests Project (2006-2017). Digitization for the Sinai Palimpsests Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from Arcadia. The Sinai Palimpsests Project aimed to provide multispectral images of the Undertext Objects in a subset of palimpsested manuscripts in the Sinai collection, as such images may only be available for palimpsested folios.",
                            "camera_operator": [
                                "Damianos Kasotakis"
                            ],
                            "imaging_date": "2009-01",
                            "delivery": "spp_2",
                            "msi_processing": [
                                "Keith Knox"
                            ],
                            "condition_category": "2",
                            "imaging_system": "Preservation Book Cradle by Stokes Imaging",
                            "note": [
                                "Automated processing techniques combine two or more raw images into a single processed image by simple arithmetic."                ]
                        },
                        {
                            "label": "Sinai Library Digitization Project, Phase 1",
                            "description": "Imaged as part of the Sinai Library Digitization Project, Phase 1 (2018-2022). Digitization for the Sinai Library Digitization Project was sponsored by St. Catherine’s Monastery of the Sinai in partnership with the Early Manuscripts Electronic Library and the UCLA Library, and with funding from The Ahmanson Foundation, Arcadia, and the Steinmetz Family Foundation. Phase 1 of the Sinai Library Digitization Project aimed to provide high-resolution images of the Arabic and Syriac manuscripts held in the Monastery’s library.",
                            "camera_operator": [
                                "Lampros Galanis"
                            ],
                            "imaging_date": "2020-01-22/2020-01-23",
                            "delivery": "6.3",
                            "condition_category": "1",
                            "imaging_system": "BC100 - 1 cam."
                        }
                    ],
                    "rights": "Contact the Monastery of St. Catherine's of the Sinai."
                },
                "internal": [ 
                    "This record is used only for purposes of developing the data portal and should therefore not be published, and should be deleted when development is complete" 
                ] 
            }
        """
        )
        assert (
            result.image_provenance.program[0].camera_operator[0]
            == "Damianos Kasotakis"
        )


class TestWorkStub:
    def test_good_WorkStub(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/d58a6555cf08448fa0b0b95e0ff91717992d67f2/text_units/s1cd6h.json"""
        st.WorkStub.model_validate_json(
            """
            {
                "id": "ark:/21198/s12c7r"
            }
        """
        )


class TestWorkBrief:
    def test_good_WorkBrief(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/626274aac4d5f9004db44615827ebc167da00036/export_test/text_units/s1mh4z.json"""
        st.WorkBrief.model_validate_json(
            """
            {
                "desc_title": "Unidentified text"
            }
        """
        )


class TestExcerptItem:
    def test_good_ExcerptItem(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/46584bb30e5f351e73010a4914a71a52e3ea389d/text_units/s1b35q.json"""
        st.ExcerptItem.model_validate_json(
            """
            {
                "type": {
                    "id": "incipit",
                    "label": "Incipit"
                },
                "locus": "f. 8v",
                "as_written": "هذا مبتداء"
            }
        """
        )


class TestContents:
    def test_good_Contents(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/46584bb30e5f351e73010a4914a71a52e3ea389d/text_units/s1c37s.json"""
        st.Contents.model_validate_json(
            """
            {
                "label": "Gospel of Matthew (ff. 3v–39v)"
            }
        """
        )


class TestWorkWitItem:
    def test_good_WorkWitItem_with_WorkStub(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/d58a6555cf08448fa0b0b95e0ff91717992d67f2/text_units/s1cd6h.json"""
        result = st.WorkWitItem.model_validate_json(
            """
            {
                "work": {
                    "id": "ark:/21198/s12c7r"
                }
            }
        """
        )
        assert isinstance(result.work, st.WorkStub)

    def test_good_WorkWitItem_with_WorkBrief(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/d58a6555cf08448fa0b0b95e0ff91717992d67f2/text_units/s1cd6h.json"""
        result = st.WorkWitItem.model_validate_json(
            """
            {
                "work": {
                    "desc_title": "Gospel of Matthew (ff. 3v–39v)"
                }
            }
        """
        )
        assert isinstance(result.work, st.WorkBrief)

    def test_bad_mixed_work_type(self):
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            st.WorkWitItem.model_validate_json(
                """
                {
                    "work": {
                        "id": "ark:/21198/s12c7r",
                        "label": "Gospel of Matthew (ff. 3v–39v)"
                    }
                }
            """
            )


class TestTextUnit:
    def test_good_TextUnit(self):
        """example from https://github.com/UCLALibrary/sinaiportal_data/blob/d58a6555cf08448fa0b0b95e0ff91717992d67f2/text_units/s1cd6h.json"""
        st.TextUnit.model_validate_json(
            """
            {
                "ark": "ark:/21198/s1cd6h",
                "reconstruction": false,
                "label": "Gospel of Matthew, chs. 15-27",
                "lang": [
                    {
                        "id": "class1252",
                        "label": "Syriac"
                    }
                ],
                "work_wit": [
                    {
                        "work": {
                            "id": "ark:/21198/s12c7r"
                        }
                    }
                ],
                "note": [
                    {
                        "type": {
                            "id": "contents",
                            "label": "Contents Note"
                        },
                        "value": "Chs. 15-27"
                    },
                    {
                        "type": {
                            "id": "general",
                            "label": "Other Notes"
                        },
                        "value": "Description by Grigory Kessel"
                    }
                ],
                "parent": [
                    "ark:/21198/s1qd1q"
                ]
            }    
        """
        )


class TestCreation:
    def test_good_Creation(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/32278a93089ee067da48dac6adee5bb1ef888986/export_test/works/s1cc8x.json"""
        st.Creation.model_validate_json(
            """
            {
                "value": "600 CE",
                "iso": {
                    "not_before": "0600"
                }
            }
        """
        )


# # TODO not attested
# class TestIncipit:
#     def test_good_Incipit(self):
#         st.Incipit.model_validate_json("""

#         """)


# # TODO not attested
# class TestExplicit:
#     def test_good_Explicit(self):
#         st.Explicit.model_validate_json("""

#         """)


# # TODO not attested
# class TestRelWorkItem:
#     def test_good_RelWorkItem(self):
#         st.RelWorkItem.model_validate_json("""

#         """)


class TestConceptualWork:
    def test_good_ConceptualWork(self):
        """Example from https://github.com/UCLALibrary/sinaiportal_data/blob/32278a93089ee067da48dac6adee5bb1ef888986/export_test/works/s1cs35.json"""
        st.ConceptualWork.model_validate_json(
            """
            {
                "ark": "ark:/21198/s1cs35",
                "pref_title": "Ezekiel",
                "alt_title": [
                    "Bible. Ezekiel"
                ],
                "genre": [
                    {
                        "id": "biblical-texts",
                        "label": "Biblical texts"
                    }
                ],
                "rel_con": [
                    {
                        "label": "Bible. Ezekiel",
                        "uri": "https://viaf.org/viaf/176193843",
                        "source": "VIAF"
                    },
                    {
                        "label": "Bible. Ezekiel",
                        "uri": "http://id.loc.gov/authorities/names/n79117856",
                        "source": "LoC"
                    }
                ],
                "refno": [],
                "bib": []
            }
        """
        )
