# mypy: disable-error-code=truthy-function
from pathlib import Path

import pytest

from feed_sinai.sinai_json_importer import SinaiJsonImporter
from feed_sinai.solr_record import ManuscriptSolrRecord
from tests.importers.test_sinai_importer import importer

BASE_PATH = 'tests/export_test'
IMPORTER = SinaiJsonImporter(base_path=BASE_PATH)
SOLR_RECORD = ManuscriptSolrRecord(
    ms_obj=IMPORTER.get_merged_manuscript(Path('tests/export_test/ms_objs/te5f0f9b.json'))
)


@pytest.fixture
def result() -> ManuscriptSolrRecord:
    return SOLR_RECORD


def test_id(result: ManuscriptSolrRecord) -> None:
    assert result.id == 'ark:/21198/te5f0f9b'


def test_ark(result: ManuscriptSolrRecord) -> None:
    assert result.ark == 'ark:/21198/te5f0f9b'


def test_has_model_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.has_model_ssim == ['Work']


def test_visibility_ssi(result: ManuscriptSolrRecord) -> None:
    assert result.visibility_ssi == 'open'


def test_year_isim(result: ManuscriptSolrRecord) -> None:
    assert result.year_isim == {
        *range(601, 700),
        700,  # range is INCLUSIVE of 700
        1292,
    }


def test_manuscript_json_ss(result: ManuscriptSolrRecord) -> None:
    assert result.manuscript_json_ss


def test_ms_type_ssi(result: ManuscriptSolrRecord) -> None:
    assert result.ms_type_ssi


def test_state_ssi(result: ManuscriptSolrRecord) -> None:
    assert result.state_ssi


def test_features_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.features_ssim


def test_support_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.support_ssim


def test_repository_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.repository_ssim


def test_collection_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.collection_ssim


def test_names_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.names_ssim


def test_places_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.places_ssim


def test_date_types_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.date_types_ssim


def test_program_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.program_ssim


def test_ot_script_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_script_ssim


def test_ot_writing_system_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_writing_system_ssim


def test_ot_genre_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_genre_ssim


def test_ot_date_isim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_date_isim


def test_ot_language_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_language_ssim


def test_ot_works_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_works_ssim


def test_ot_names_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.ot_names_ssim


def test_para_script_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_script_ssim


def test_para_writing_system_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_writing_system_ssim


def test_para_genre_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_genre_ssim


def test_para_date_isim(result: ManuscriptSolrRecord) -> None:
    assert result.para_date_isim == set()


def test_para_language_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_language_ssim


def test_para_works_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_works_ssim == set()


def test_para_names_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_names_ssim == set()


def test_para_type_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.para_type_ssim


def test_uto_script_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.uto_script_ssim == set()


def test_uto_date_isim(result: ManuscriptSolrRecord) -> None:
    assert result.uto_date_isim == set()


def test_uto_language_ssim(result: ManuscriptSolrRecord) -> None:
    assert result.uto_language_ssim == set()


def test_shelfmark_ssi(result: ManuscriptSolrRecord) -> None:
    assert result.shelfmark_ssi


def test_titles_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.titles_tesim


def test_names_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.names_tesim


def test_exerpts_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.exerpts_tesim


def test_places_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.places_tesim


def test_contents_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.contents_tesim


def test_paracontent_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.paracontent_tesim


def test_full_text_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.full_text_tesim


def test_all_fields_tesim(result: ManuscriptSolrRecord) -> None:
    assert result.all_fields_tesim
