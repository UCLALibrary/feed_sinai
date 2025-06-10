# -*- coding: utf-8 -*-
"""
Import JSON data into https://sinaimanuscripts.library.ucla.edu/

Input files are stored in https://github.com/UCLALibrary/sinaiportal_data
Output is pushed to a solr index suitable for use by https://github.com/UCLALibrary/sinaimanuscripts
"""

import json
from pathlib import Path
import typing
import warnings

import feed_sinai.sinai_types as st

from feed_sinai.importer import Importer, MetadataRecord
import logging


class SinaiJsonImporter:
    """Importer class to map data from"""

    base_path: Path

    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = Path(base_path)

    @staticmethod
    def get_filename(ark: str):
        """Returns a filename based on an item's ark.

        Drops "ark:/21198/" (all records are assigned the UCLA NAAN) and adds the ".json" suffix"
        """

        return ark.replace("ark:/21198/", "").replace("/", "-") + ".json"

    def get_conceptual_work(self, stub: st.WorkStub) -> st.ConceptualWork:
        return st.ConceptualWork.model_validate_json(
            (self.base_path / "works" / self.get_filename(stub.id)).read_text()
        )

    def get_work_wit(self, raw: st.WorkWitItemUnmerged) -> st.WorkWitItemMerged:
        interim = st.WorkWitItem.model_validate(raw)
        if isinstance(raw.work, st.WorkStub):
            interim.work = self.get_conceptual_work(raw.work)

        return st.WorkWitItemMerged.model_validate(
            interim.model_dump(serialize_as_any=True)
        )

    def get_text_unit(self, stub: st.TextUnitStub) -> st.TextUnit:
        path = self.base_path / "text_units" / self.get_filename(stub.id)
        raw = st.TextUnitUnmerged.model_validate_json(path.read_text())
        interim = st.TextUnit.model_validate(raw)

        interim.work_wit = [self.get_work_wit(work_wit) for work_wit in raw.work_wit]

        return st.TextUnitMerged.model_validate(
            interim.model_dump(serialize_as_any=True)
        )

    def get_layer(self, layer: st.LayerStub) -> st.InscribedLayerMerged:
        path = self.base_path / "layers" / self.get_filename(layer.id)
        raw = st.InscribedLayerUnmerged.model_validate_json(path.read_text())
        interim = st.InscribedLayer.model_validate(raw)

        interim.text_unit = [
            self.get_text_unit(text_unit) for text_unit in raw.text_unit
        ]

        return st.InscribedLayerMerged.model_validate(
            interim.model_dump(serialize_as_any=True)
        )

    def get_part(self, raw: st.PartUnmerged) -> st.PartMerged:
        interim = st.Part.model_validate(raw)
        interim.layer = [self.get_layer(stub) for stub in raw.layer]

        return st.PartMerged.model_validate(interim.model_dump(serialize_as_any=True))

    def get_merged_manuscript(self, path: Path) -> st.ManuscriptObjectMerged:
        raw = st.ManuscriptObjectUnmerged.model_validate_json(path.read_text())
        interim = st.ManuscriptObject.model_validate(raw)

        interim.part = [self.get_part(stub) for stub in raw.part]
        if raw.layer:
            interim.layer = [self.get_layer(stub) for stub in raw.layer]

        return st.ManuscriptObjectMerged.model_validate(
            interim.model_dump(serialize_as_any=True)
        )

    def iterate_merged_records(self) -> typing.Iterator[st.ManuscriptObjectMerged]:
        """Yield json records for manuscripts with other data embedded."""

        for path in (self.base_path / "ms_objs").glob("*.json"):
            try:
                yield self.get_merged_manuscript(path)
            except Exception as e:
                logging.warning(f"Could not merge {path}: {e}")

    def save_merged_records(self) -> None:
        for record in self.iterate_merged_records():
            (self.base_path / "merged").mkdir(exist_ok=True)
            path = self.base_path / "merged" / self.get_filename(record.ark)
            path.write_text(record.model_dump_json(exclude_none=True))
