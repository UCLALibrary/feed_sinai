# -*- coding: utf-8 -*-
"""
Import JSON data into https://sinaimanuscripts.library.ucla.edu/

Input files are stored in https://github.com/UCLALibrary/sinaiportal_data
Output is pushed to a solr index suitable for use by https://github.com/UCLALibrary/sinaimanuscripts
"""

import json
from pathlib import Path
from typing import Any, Iterator, Optional

from pysolr import Solr  # type: ignore

import feed_sinai.sinai_types as st
import logging


class SinaiJsonImporter:
    """Importer class to map data from"""

    base_path: Path
    solr: Solr

    def __init__(self, base_path: str = '.', solr_url: Optional[str] = None):
        self.base_path = Path(base_path)
        self.solr = Solr(solr_url, always_commit=True)

    @staticmethod
    def get_filename(ark: str):
        """Returns a filename based on an item's ark.

        Drops "ark:/21198/" (all records are assigned the UCLA NAAN) and adds the ".json" suffix"
        """

        return ark.replace('ark:/21198/', '').replace('/', '-') + '.json'

    def get_agent(self, ark: str):
        path = self.base_path / 'agents' / self.get_filename(ark)
        return st.Agent.model_validate_json(path.read_text())

    def get_assoc_name_item(self, raw: st.AssocNameItemUnmerged) -> st.AssocNameItemMerged:
        return raw.convert(st.AssocNameItemMerged, agent=self.get_agent(raw.id) if raw.id else None)

    def get_conceptual_work(self, stub: st.WorkStub) -> st.ConceptualWorkMerged:
        path = self.base_path / 'works' / self.get_filename(stub.id)
        raw = st.ConceptualWorkUnmerged.model_validate_json(path.read_text())

        return raw.convert(
            st.ConceptualWorkMerged,
            creator=(
                [self.get_assoc_name_item(assoc_name) for assoc_name in raw.creator]
                if raw.creator
                else None
            ),
        )

    def get_work_brief(self, raw: st.WorkBriefUnmerged) -> st.WorkBriefMerged:
        return raw.convert(
            st.WorkBriefMerged,
            creator=([self.get_agent(id) for id in raw.creator] if raw.creator else None),
        )

    def get_work_wit(self, raw: st.WorkWitItemUnmerged) -> st.WorkWitItemMerged:
        return raw.convert(
            st.WorkWitItemMerged,
            work=(
                self.get_work_brief(raw.work)
                if isinstance(raw.work, st.WorkBrief)
                else self.get_conceptual_work(raw.work)
            ),
        )

    def get_text_unit(self, stub: st.TextUnitStub) -> st.TextUnit:
        path = self.base_path / 'text_units' / self.get_filename(stub.id)
        raw = st.TextUnitUnmerged.model_validate_json(path.read_text())

        return raw.convert(
            st.TextUnitMerged,
            work_wit=[self.get_work_wit(work_wit) for work_wit in raw.work_wit],
        )

    def get_layer(self, layer: st.LayerStub) -> st.InscribedLayerMerged:
        path = self.base_path / 'layers' / self.get_filename(layer.id)
        raw = st.InscribedLayerUnmerged.model_validate_json(path.read_text())

        return raw.convert(
            st.InscribedLayerMerged,
            text_unit=[self.get_text_unit(text_unit) for text_unit in raw.text_unit],
        )

    def get_part(self, raw: st.PartUnmerged) -> st.PartMerged:
        return raw.convert(
            st.PartMerged,
            layer=[self.get_layer(stub) for stub in raw.layer] if raw.layer else None,
        )

    def get_merged_manuscript(self, path: Path) -> st.ManuscriptObjectMerged:
        raw = st.ManuscriptObjectUnmerged.model_validate_json(path.read_text())

        return raw.convert(
            st.ManuscriptObjectMerged,
            part=[self.get_part(stub) for stub in raw.part] if raw.part else None,
            layer=[self.get_layer(stub) for stub in raw.layer] if raw.layer else None,
        )

    def iterate_merged_records(self) -> Iterator[st.ManuscriptObjectMerged]:
        """Yield json records for manuscripts with other data embedded."""

        for path in (self.base_path / 'ms_objs').glob('*.json'):
            try:
                yield self.get_merged_manuscript(path)
            except Exception as e:
                logging.warning(f'Could not merge {path}: {e}')

    def save_merged_records(self) -> None:
        for record in self.iterate_merged_records():
            (self.base_path / 'merged').mkdir(exist_ok=True)
            path = self.base_path / 'merged' / self.get_filename(record.ark)
            path.write_text(record.model_dump_json(exclude_none=True))

    def solr_record(self, ms_obj: st.ManuscriptObjectMerged) -> dict[str, Any]:
        return json.loads(
            st.ManuscriptSolrRecord(
                id=ms_obj.ark,
                manuscript_json_ss=ms_obj.model_dump_json(exclude_none=True),
                descriptive_title_tesim={*ms_obj.deep_get('desc_title')},
                uniform_title_tesim={*ms_obj.deep_get('uniform_title')},
                # date_created_tesim={""},  # TODO
                human_readable_language_tesim={
                    getattr(x, 'label', x) for x in ms_obj.deep_get('lang')
                },
                # name_fields_index_tesim=[*ms_obj.deep_get("")},  # TODO
                # names_sim=[*ms_obj.deep_get("")},  # TODO
            ).model_dump_json(exclude_none=True)
        )

    def load_to_solr(self):
        self.solr.add([self.solr_record(ms) for ms in self.iterate_merged_records()])
