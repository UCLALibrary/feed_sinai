#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Convert UCLA Library CSV files for Ursus, our Blacklight installation."""

import importlib.metadata
import typing

import click
from pysolr import Solr  # type: ignore

from feed_sinai.sinai_json_importer import SinaiJsonImporter


@click.group()
@click.option(
    "--solr_url",
    default="http://localhost:8983/solr/californica",
    help="URL of a solr instance, e.g. http://localhost:8983/solr/californica",
)
@click.version_option(version=importlib.metadata.version("feed_sinai"))
@click.pass_context
def sinai(ctx, solr_url: typing.Optional[str]):
    """CLI for managing a Solr index for Ursus."""

    ctx.ensure_object(dict)
    ctx.obj["solr_client"] = (
        Solr(solr_url, always_commit=True) if solr_url else Solr("")
    )


@sinai.command("export")
@click.argument(
    "base_path", nargs=1, type=click.Path(exists=True, dir_okay=True, file_okay=False)
)
def export(base_path: str):
    importer = SinaiJsonImporter(base_path=base_path)
    importer.save_merged_records()


if __name__ == "__main__":
    sinai()  # pylint: disable=no-value-for-parameter
