# pyright: reportInvalidTypeForm=false
# pylint: disable=too-many-lines
"""Pydantic classes for the data model."""

import logging
from functools import cached_property
from typing import (
    Callable,
    Iterator,
    List,
    Literal,
    TypeVar,
    cast,
)

from pydantic import Field, computed_field
from typing_extensions import ParamSpec

import feed_sinai.sinai_types as st

LAYER_FIELDS = Literal['ot_layer', 'guest_layer', 'uto']

P = ParamSpec('P')
T = TypeVar('T')


def filter_none(generator_function: Callable[P, Iterator[T | None]]) -> Callable[P, Iterator[T]]:
    def wrapper(*args: P.args, **kwds: P.kwargs) -> Iterator[T]:
        for item in generator_function(*args, **kwds):
            if item is not None:
                yield item

    return wrapper


class ManuscriptSolrRecord(st.BaseModel):
    ms_obj: st.ManuscriptObjectMerged = Field(..., exclude=True)
    iiif_manifests: tuple[dict, ...] = tuple()

    def __repr__(self) -> str:
        return f'<ManuscriptSolrRecord ark="{self.ark_ssi}">'

    #
    #   Blacklight Stuff
    #

    @computed_field
    def id(self) -> str:
        return self.ms_obj.ark

    @computed_field
    def ark_ssi(self) -> str:
        return self.ms_obj.ark

    @computed_field
    def has_model_ssim(self) -> List[str]:
        return ['Work']

    @computed_field
    def visibility_ssi(self) -> str:
        return 'open'

    @computed_field
    def thumbnail_url_ss(self) -> st.AnyUrl | None:
        """Picks a thumbnail downloading the IIIF manifest.

        Args:
            record: A mapping representing the CSV record.

        Returns:
            A string containing the thumbnail URL
        """

        for iiif in self.ms_obj.iiif:
            if iiif.thumbnail:
                return iiif.thumbnail

        logging.warning(f'no thumbnail for {self.ms_obj.ark}')
        return None

    #
    #   Facets (Main / any)
    #

    @computed_field
    def ms_type_ssi(self) -> str:
        return self.ms_obj.type.label

    @computed_field
    def state_ssi(self) -> str:
        return self.ms_obj.state.label

    @computed_field
    def features_ssim(self) -> set[str]:
        return {
            feature.label for feature in self.ms_obj.deep_get('features', cls=st.ControlledTerm)
        }

    @computed_field()
    def support_ssim(self) -> set[str]:
        return {support.label for part in self.ms_obj.part for support in part.support}

    @computed_field
    def repository_ssim(self) -> set[str]:
        return {location.repository for location in self.ms_obj.location}

    @computed_field
    def collection_ssim(self) -> set[str]:
        return {location.collection for location in self.ms_obj.location if location.collection}

    @computed_field
    def names_ssim(self) -> set[str]:
        return {agent_record.pref_name for agent_record in self.ms_obj.deep_get(cls=st.Agent)}

    @computed_field
    def places_ssim(self) -> set[str]:
        return {place.pref_name for place in self.ms_obj.deep_get(cls=st.Place)}

    @computed_field
    def date_types_ssim(self) -> set[str]:
        return {
            date.type.label
            for date in self.ms_obj.deep_get(cls=st.AssocDateItem)
            if date.type.id != 'origin'
        }

    @computed_field
    def program_ssim(self) -> set[str]:
        return {
            program.label
            for program in (
                self.ms_obj.desc_provenance.program if self.ms_obj.desc_provenance else []
            )
        } | {
            program.label
            for program in (
                self.ms_obj.image_provenance.program if self.ms_obj.image_provenance else []
            )
            if program.label
        }

    @computed_field
    def reconstructed_from_ssim(self) -> set[str]:
        return set(self.ms_obj.reconstructed_from)

    @computed_field
    def ot_script_ssim(self) -> set[str]:
        return {
            script_item.label
            for ot_layer in self.ot_layers()
            for writing_item in ot_layer.layer_record.writing
            for script_item in writing_item.script
        }

    @computed_field
    def ot_writing_system_ssim(self) -> set[str]:
        return {
            script_item.writing_system
            for ot_layer in self.ot_layers()
            for writing_item in ot_layer.layer_record.writing
            for script_item in writing_item.script
        }

    @computed_field
    def ot_genre_ssim(self) -> set[str]:
        return {
            genre.label
            for layer in self.ot_layers()
            for genre in layer.deep_get('genre', cls=st.ControlledTerm)
        }

    @computed_field
    def ot_date_isim(self) -> set[int]:
        return {
            year
            for layer in self.ot_layers()
            for date in layer.layer_record.assoc_date
            if date.type.id == 'origin' and date.iso
            for year in range(date.iso.not_before, date.iso.not_after + 1)
        }

    @computed_field
    def ot_language_ssim(self) -> set[str]:
        return {
            language.label
            for layer in self.ot_layers()
            for text_unit in layer.layer_record.text_unit
            for language in text_unit.text_unit_record.lang
        }

    @computed_field
    def ot_works_ssim(self) -> set[str]:
        return set(self.get_work_titles(layer_type='ot_layer', pref_only=True))

    #
    #   Facets (Guest/Para Only)
    #

    @computed_field
    def para_script_ssim(self) -> set[str]:
        return {
            script.label
            for layer in self.guest_layers()
            for writing_item in layer.layer_record.writing
            for script in writing_item.script
        } | {script.label for para in self.get_para() for script in para.script}

    @computed_field
    def para_writing_system_ssim(self) -> set[str]:
        return {
            script.writing_system
            for layer in self.guest_layers()
            for writing_item in layer.layer_record.writing
            for script in writing_item.script
        } | {script.writing_system for para in self.get_para() for script in para.script}

    @computed_field
    def para_date_isim(self) -> set[int]:
        return {
            year
            for layer in self.guest_layers()
            for date in layer.layer_record.assoc_date
            if date.type.id == 'origin' and date.iso
            for year in range(date.iso.not_before, date.iso.not_after + 1)
        }

    @computed_field
    def para_language_ssim(self) -> set[str]:
        return {
            language.label
            for layer in self.guest_layers()
            for text_unit in layer.layer_record.text_unit
            for language in text_unit.text_unit_record.lang
        } | {language.label for para in self.get_para() for language in para.lang}

    @computed_field
    def para_works_ssim(self) -> set[str]:
        return set(self.get_work_titles(layer_type='guest_layer', pref_only=True))

    @computed_field
    def para_genre_ssim(self) -> set[str]:
        return {
            genre.label
            for layer in self.guest_layers()
            for genre in layer.deep_get('genre', cls=st.ControlledTerm)
        }

    @computed_field
    def para_names_ssim(self) -> set[str]:
        return {
            agent_record.pref_name
            for layer in self.guest_layers()
            for agent_record in layer.deep_get(cls=st.Agent)
        }

    @computed_field
    def para_type_ssim(self) -> set[str]:
        return {subtype.label for para in self.get_para() for subtype in para.subtype}

    #
    #   UTO facets
    #

    @computed_field
    def uto_script_ssim(self) -> set[str]:
        return {script for layer in self.uto_layers() for script in layer.script}

    @computed_field
    def uto_language_ssim(self) -> set[str]:
        return {language for layer in self.uto_layers() for language in layer.lang}

    @computed_field
    def uto_date_isim(self) -> set[int]:
        return {
            year
            for layer in self.uto_layers()
            for date in layer.orig_date
            if date.iso
            for year in range(date.iso.not_before, date.iso.not_after + 1)
        }

    #
    #   Scoped / keyword search
    #

    @computed_field
    def shelfmark_ssi(self) -> str:
        return self.ms_obj.shelfmark

    @computed_field
    def titles_tesim(self) -> set[str]:
        return set(self.get_work_titles(layer_type='ot_layer', pref_only=False))

    @computed_field
    def names_tesim(self) -> set[str]:
        return {
            name
            for assoc_name_item in self.ms_obj.deep_get(cls=st.AssocNameItemMerged)
            for name in [
                assoc_name_item.value,
                assoc_name_item.as_written,
            ]
            if name
        } | {
            name
            for agent in self.ms_obj.deep_get(cls=st.Agent)
            for name in [
                agent.pref_name,
                *agent.alt_name,
            ]
        }

    @computed_field
    def exerpts_tesim(self) -> set[str]:
        return self.get_exerpts(exclude=['guest_layer', 'uto'])

    @computed_field
    def places_tesim(self) -> set[str]:
        return {
            name
            for assoc_place_item in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged)
            for name in [
                assoc_place_item.value,
                assoc_place_item.as_written,
                *(
                    [
                        assoc_place_item.place_record.pref_name,
                        *assoc_place_item.place_record.alt_name,
                    ]
                    if assoc_place_item.place_record
                    else []
                ),
            ]
            if name
        }

    @computed_field
    def contents_tesim(self) -> set[str]:
        exclude: list[LAYER_FIELDS] = ['guest_layer', 'uto']

        return (
            self.ms_obj.deep_get(
                'summary',
                'pref_title',
                'alt_title',
                'desc_title',
                'orig_lang_title',
                cls=str,
                exclude=exclude,
            )
            | self.get_titles(exclude=exclude)
            | {
                text_unit.label
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
            }
            | self.get_exerpts(exclude=exclude)
            | {
                note
                for contents_item in self.ms_obj.deep_get(cls=st.Contents, exclude=exclude)
                for note in contents_item.note
            }
            | {
                note
                for excerpt in self.ms_obj.deep_get(cls=st.ExcerptItem, exclude=exclude)
                for note in excerpt.note
            }
            | {
                note
                for work_wit in self.ms_obj.deep_get(cls=st.WorkWitItemMerged, exclude=exclude)
                for note in work_wit.note
            }
        )

    @computed_field
    def paracontent_tesim(self) -> set[str]:
        exclude: list[LAYER_FIELDS] = ['ot_layer']

        return (
            self.ms_obj.deep_get('summary', cls=str, exclude=exclude)
            | {
                item
                # don't use 'exclude', bc this one is only ParaItems
                for para in self.ms_obj.deep_get(cls=st.ParaItemMerged)
                for item in [
                    para.type.label,
                    *[
                        item
                        for script in para.script
                        for item in [script.label, script.writing_system]
                    ],
                    *[lang.label for lang in para.lang],
                    para.label,
                    para.as_written,
                    *para.translation,
                    *para.note,
                ]
                if item
            }
            | {
                item
                for name in self.ms_obj.deep_get(cls=st.AssocNameItemMerged, exclude=exclude)
                for item in [
                    name.agent_record and name.agent_record.pref_name,
                    name.value,
                    name.as_written,
                    *name.note,
                ]
                if item
            }
            | {
                item
                for place in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged, exclude=exclude)
                for item in [
                    place.place_record and place.place_record.pref_name,
                    place.value,
                    place.as_written,
                    *place.note,
                ]
                if item
            }
            | {
                note
                for date in self.ms_obj.deep_get(cls=st.AssocDateItem, exclude=exclude)
                for note in date.note
            }
        )

    @computed_field
    def full_text_tesim(self) -> set[str]:
        exclude: list[LAYER_FIELDS] = []
        return (
            {
                self.ms_obj.ark,
            }
            | {
                term.label
                for term in self.ms_obj.deep_get('support', cls=st.ControlledTerm, exclude=exclude)
            }
            | {
                item
                for writing in self.ms_obj.deep_get(cls=st.WritingItem, exclude=exclude)
                for script in writing.script
                for item in [script.label, script.writing_system]
            }
            | {
                self.ms_obj.shelfmark,
            }
            | self.ms_obj.deep_get('summary', 'note', cls=str, exclude=exclude)
            | {
                note_item.value
                for note_item in self.ms_obj.deep_get(cls=st.NoteItem, exclude=exclude)
                if note_item.value
            }
            | {
                color
                for ink in self.ms_obj.deep_get(cls=st.InkItem, exclude=exclude)
                for color in ink.color
            }
            | {
                language.label
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for language in text_unit.lang
            }
            | self.get_titles(exclude=exclude)
            | {
                creator.agent_record.pref_name
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for work_wit in text_unit.work_wit
                for creator in work_wit.work.creator
                if creator.agent_record and creator.agent_record.pref_name
            }
            | {
                name
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for work_wit in text_unit.work_wit
                for creator in work_wit.work.creator
                if creator.agent_record
                for name in creator.agent_record.alt_name
            }
            | {
                text_unit.label
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
            }
            | self.get_exerpts(exclude=exclude)
            | {
                note
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for work_wit in text_unit.work_wit
                for contents_item in work_wit.contents
                for note in contents_item.note
            }
            | {
                note
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for work_wit in text_unit.work_wit
                for excerpt in work_wit.excerpt
                for note in excerpt.note
            }
            | {
                note
                for text_unit in self.ms_obj.deep_get(cls=st.TextUnitMerged, exclude=exclude)
                for work_wit in text_unit.work_wit
                for note in work_wit.note
            }
            | {
                item
                for part in self.ms_obj.part
                for para in part.para
                for script in para.script
                for item in [script.label, script.writing_system]
            }
            | {
                language.label
                for part in self.ms_obj.part
                for para in part.para
                for language in para.lang
            }
            | {para.label for part in self.ms_obj.part for para in part.para if para.label}
            | {
                para.as_written
                for part in self.ms_obj.part
                for para in part.para
                if para.as_written
            }
            | {
                translation
                for part in self.ms_obj.part
                for para in part.para
                for translation in para.translation
            }
            | {note for part in self.ms_obj.part for para in part.para for note in para.note}
            | {
                assoc_name.agent_record.pref_name
                for assoc_name in self.ms_obj.deep_get(cls=st.AssocNameItemMerged, exclude=exclude)
                if assoc_name.agent_record
            }
            | {
                place.place_record.pref_name
                for place in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged, exclude=exclude)
                if place.place_record
            }
            | {
                note
                for date in self.ms_obj.deep_get(cls=st.AssocDateItem, exclude=exclude)
                for note in date.note
            }
            | {
                name.value
                for name in self.ms_obj.deep_get(cls=st.AssocNameItemMerged, exclude=exclude)
                if name.value
            }
            | {
                name.as_written
                for name in self.ms_obj.deep_get(cls=st.AssocNameItemMerged, exclude=exclude)
                if name.as_written
            }
            | {
                note
                for name in self.ms_obj.deep_get(cls=st.AssocNameItemMerged, exclude=exclude)
                for note in name.note
            }
            | {
                place.value
                for place in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged, exclude=exclude)
                if place.value
            }
            | {
                place.as_written
                for place in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged, exclude=exclude)
                if place.as_written
            }
            | {
                note
                for place in self.ms_obj.deep_get(cls=st.AssocPlaceItemMerged, exclude=exclude)
                for note in place.note
            }
            | {ms.type.label for ms in self.ms_obj.related_mss}
            | {ms.label for ms in self.ms_obj.related_mss}
            | {note for ms in self.ms_obj.related_mss for note in ms.note}
            | {mss.label for ms in self.ms_obj.related_mss for mss in ms.mss}
            | {para.type.label for part in self.ms_obj.part for para in part.para}
        )

    @computed_field
    def manuscript_json_ss(self) -> str:
        return self.ms_obj.model_dump_json()

    #
    #   Helper methods
    #

    def ot_layers(self) -> Iterator[st.ManuscriptLayerMerged]:
        for part in self.ms_obj.part:
            yield from part.ot_layer
        yield from self.ms_obj.ot_layer

    def guest_layers(self) -> Iterator[st.ManuscriptLayerMerged]:
        for part in self.ms_obj.part:
            yield from part.guest_layer
        yield from self.ms_obj.guest_layer

    def uto_layers(self) -> Iterator[st.UndertextManuscriptLayerMerged]:
        for part in self.ms_obj.part:
            yield from part.uto
        yield from self.ms_obj.uto

    def get_layers(
        self, layer_type: LAYER_FIELDS | None = None
    ) -> Iterator[st.ManuscriptLayerMerged]:
        layer_types = [layer_type] if layer_type else ['ot_layer', 'guest_layer', 'uto']
        for layer_type in layer_types:
            for part in self.ms_obj.part:
                yield from getattr(part, layer_type)
            yield from getattr(self.ms_obj, layer_type)

    def get_work_wits(
        self, layer_type: LAYER_FIELDS | None = None
    ) -> Iterator[st.WorkWitItemMerged]:
        for layer in self.get_layers(layer_type=layer_type):
            for text_unit in layer.layer_record.text_unit:
                yield from text_unit.text_unit_record.work_wit

    @filter_none
    def get_work_titles(
        self, layer_type: LAYER_FIELDS | None = None, pref_only: bool = True
    ) -> Iterator[str | None]:
        for work_wit in self.get_work_wits(layer_type=layer_type):
            if isinstance(work_wit.work, st.ConceptualWork):
                yield work_wit.work.pref_title
                if not pref_only:
                    yield work_wit.work.orig_lang_title
                    yield from work_wit.work.alt_title
            elif isinstance(work_wit.work, st.WorkBrief) and not pref_only:
                yield work_wit.work.desc_title

            for section in work_wit.contents:
                yield section.pref_title
                if not pref_only:
                    yield section.label
                    yield section.pref_title

            if not pref_only:
                yield work_wit.alt_title
                yield work_wit.as_written

    def get_titles(self, exclude: list[LAYER_FIELDS] = []) -> set[str]:
        return (
            {
                title
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for work in layer.deep_get(cls=st.ConceptualWorkMerged)
                for title in [
                    work.pref_title,
                    work.orig_lang_title,
                    *work.alt_title,
                ]
                if title
            }
            | {
                work_brief.desc_title
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for work_brief in layer.deep_get(cls=st.WorkBriefMerged)
                if work_brief.desc_title
            }
            | {
                title
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for work_wit in layer.deep_get(cls=st.WorkWitItemUnmerged)
                for title in [work_wit.alt_title, work_wit.as_written]
                if title
            }
            | {
                title
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for contents_item in layer.deep_get(cls=st.ContentsMerged)
                for title in [contents_item.label, contents_item.pref_title]
                if title
            }
        )

    def get_exerpts(self, exclude: list[LAYER_FIELDS] = []) -> set[str]:
        return (
            {
                text
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for exerpt in layer.deep_get(cls=st.Incipit)
                for text in [
                    exerpt.value,
                    *exerpt.translation,
                ]
            }
            | {
                text
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for exerpt in layer.deep_get(cls=st.Explicit)
                for text in [
                    exerpt.value,
                    *exerpt.translation,
                ]
            }
            | {
                text
                for layer in self.ms_obj.deep_get(cls=st.ManuscriptLayer, exclude=exclude)
                for exerpt in layer.deep_get(cls=st.ExcerptItem)
                for text in [
                    exerpt.as_written,
                    *exerpt.translation,
                ]
                if text
            }
        )

    def get_para(self) -> Iterator[st.ParaItemMerged]:
        """Get all para items from the manuscript."""
        yield from self.ms_obj.para
        for part in self.ms_obj.part:
            yield from part.para
