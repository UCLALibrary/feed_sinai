# -*- coding: utf-8 -*-
"""Convert UCLA Library CSV files for Ursus, our Blacklight installation."""

import csv
from datetime import date, datetime, timezone
from getpass import getuser
import typing
import warnings


# Custom Types

MetadataValue = typing.Union[str, int, date, int]
MetadataValues = typing.Union[
    None,
    MetadataValue,
    list[MetadataValue],
]
MetadataRecord = typing.Dict[str, MetadataValues]

MappingFunction = typing.Callable[[MetadataRecord], MetadataValues]
FieldSource = MappingFunction | str

SOLR_SUFFIXES = {'text': 'te', 'symbol': 's', 'date': 'dt', 'integer': 'i'}
PYTHON_TYPES = {'text': str, 'symbol': str, 'date': date, 'integer': int}


def listify(item: MetadataValues) -> list[MetadataValue]:
    """Wrap item in a list if it is not one already."""
    if item is None:
        return []
    if isinstance(item, list):
        return item
    if isinstance(item, (tuple, typing.Generator)):
        return list(item)
    return [item]


class Field:
    """A field in the Ursus Solr schema."""

    sources: list[FieldSource]
    name: str | None
    field_type: typing.Literal['text', 'symbol', 'date', 'integer']
    stored: bool
    indexed: bool
    multivalued: bool
    facet: bool
    solr_names: list[str]
    value_mapper_fn: typing.Callable[[MetadataValue], MetadataValue]
    derived: bool

    def __init__(
        self,
        *sources: FieldSource,
        field_type='text',
        stored=True,
        indexed=True,
        multivalued=True,
        facet=False,
        solr_names=None,
        value_mapper_fn=None,
        derived=False,
        map_field_fn=None,
    ):
        self.sources = list(sources)
        self.field_type = field_type
        self.stored = stored
        self.indexed = indexed
        self.multivalued = multivalued
        self.facet = facet
        self.solr_names = solr_names
        self.value_mapper_fn = value_mapper_fn or PYTHON_TYPES[field_type]
        self.derived = derived
        if callable(map_field_fn):
            self._map_field_fn = map_field_fn

    def __call__(self, *additional_sources: FieldSource):
        """Adds additional_sources to self.sources. This allows use as a decorator of a source
        function"""

        self.sources.extend(additional_sources)
        return self

    def field_sources_generator(
        self, row: MetadataRecord
    ) -> typing.Iterator[MetadataValue]:
        """Generator function that yields input values for a field based on self.sources."""

        for source in self.sources:
            if isinstance(source, str):
                yield from listify(row.get(source))
            elif callable(source):
                yield from listify(source(row))
            else:
                warnings.warn(
                    'sources must be callable, or strings representing field names'
                )

    def map_field(self, row: MetadataRecord) -> MetadataRecord:
        """Returns the value of the field. Gathers all values from the source field names and
        applies the value mapper function. Can be overridden for a given field via the
        value_mapper_fn parameter."""

        values = [
            self.value_mapper_fn(value) for value in self.field_sources_generator(row)
        ]

        if not values:
            return {}

        return_values: MetadataValues
        if self.multivalued:
            return_values = values
        else:
            if len(values) > 1:
                warnings.warn(
                    'Got multiple values for %s. Using %s and discarding the rest (%s)',
                    self.sources,
                    values[0],
                    values[1:],
                )
            return_values = values[0]

        return {solr_name: return_values for solr_name in self.get_solr_names()}

    def get_solr_names(self) -> list[str]:
        """Returns the solr field name(s)."""

        if self.solr_names:
            return self.solr_names

        suffixes = [
            SOLR_SUFFIXES[self.field_type]
            + ('s' if self.stored else '')
            + ('i' if self.indexed else '')
            + ('m' if self.multivalued else '')
        ]

        if self.facet and self.field_type == 'text':
            suffixes.append(
                's'
                # No second 's' because we don't need to store the duplicate facet field
                + ('i' if self.indexed else '')
                + ('m' if self.multivalued else '')
            )

        self.solr_names = [f'{self.name}_{suffix}' for suffix in suffixes]
        return self.solr_names


class Importer:
    """Base class for importers. Defines a bare minimum of fields, all other fields are left to be
    defined by subclasses."""

    ingest_id: str

    id = Field('Item ARK', field_type='symbol', multivalued=False, solr_names=('id',))
    ark = Field('Item ARK', field_type='symbol', multivalued=False)
    record_origin = Field(
        lambda x: 'feed_sinai', field_type='symbol', multivalued=False
    )

    _mapped_fields: list[Field]
    _derived_fields: list[Field]

    def __init__(self):
        self.ingest_id = f'{datetime.now(timezone.utc).isoformat()}-{getuser()}'

        self._mapped_fields = []
        self._derived_fields = []
        for name in dir(self):
            item = getattr(self, name)
            if isinstance(item, Field):
                item.name = name
                if item.derived:
                    self._derived_fields.append(item)
                else:
                    self._mapped_fields.append(item)

    def map_record(
        self,
        row: MetadataRecord,
    ) -> MetadataRecord:
        """Maps a record from input csv to output suitable for solr."""

        result: MetadataRecord = {
            field_name: values
            for field in self._mapped_fields
            for field_name, values in field.map_field(row).items()
        }

        result.update(
            {
                field_name: values
                for field in self._derived_fields
                for field_name, values in field.map_field(result).items()
            }
        )

        result.update({'ingest_id_ssi': self.ingest_id})

        return result

    def import_csv_files(self, *filenames: str) -> typing.Iterator[MetadataRecord]:
        """Iterate over input fiels, yielding mapped metadata records"""
        for filename in filenames:
            for row in csv.DictReader(open(filename, encoding='utf-8')):
                yield self.map_record(row)
