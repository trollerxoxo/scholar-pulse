from pulse.service import rank_papers, deduplicate
from pulse.config import RankingConfig
from datetime import date
from helpers import make_paper, make_query

query = make_query()
config = RankingConfig()

# --- Ranking tests ---

def test_normal_ranking():
    papers = [
        make_paper('1', 'Highly cited + keywords', 500, date(2020, 1, 1), ['digital twin', 'BIM']),
        make_paper('2', 'New, few citations', 5, date(2026, 2, 1), ['digital twin']),
        make_paper('3', 'Medium, no keywords', 100, date(2024, 6, 1), ['concrete', 'steel']),
    ]
    ranked = rank_papers(papers, query, config)
    assert ranked[0].id == '1'
    assert ranked[1].id == '3'
    assert ranked[2].id == '2'

def test_zero_citations():
    papers_zero = [
        make_paper('1', 'Paper A', 0, date(2025, 1, 1), ['BIM']),
        make_paper('2', 'Paper B (newer)', 0, date(2026, 1, 1), ['BIM']),
    ]
    ranked = rank_papers(papers_zero, query, config)
    assert ranked[0].id == '2'
    assert ranked[1].id == '1'

def test_empty_papers():
    ranked = rank_papers([], query, config)
    assert ranked == []

def test_single_paper():
    papers = [make_paper('1', 'Solo', 10, date(2020, 1, 1), ['digital twin', 'BIM'])]
    ranked = rank_papers(papers, query, config)
    assert ranked[0].id == '1'

def test_same_paper_different_recency():
    papers = [
        make_paper('1', 'Old', 10, date(2020, 1, 1), ['digital twin', 'BIM']),
        make_paper('2', 'New', 10, date(2021, 2, 1), ['digital twin', 'BIM']),
    ]
    ranked = rank_papers(papers, query, config)
    assert ranked[0].relevance_score > ranked[1].relevance_score

# --- Dedup tests ---

def test_same_doi_keep_richer_metadata():
    papers = [
        make_paper('ss1', doi='10.1234/test', abstract=''),
        make_paper('oa1', doi='10.1234/test', abstract='Full abstract', pdf_url='http://pdf.com'),
    ]
    result = deduplicate(papers)
    assert len(result) == 1
    assert result[0].id == 'oa1'

def test_deduplicate_no_duplicates():
    papers = [
        make_paper('1', doi='10.1111/a'),
        make_paper('2', doi='10.2222/b'),
    ]
    result = deduplicate(papers)
    assert len(result) == 2

def test_deduplicate_no_DOI_or_Arxiv_or_OpenAlex():
    papers = [
        make_paper('orphan1'),
        make_paper('orphan2'),
    ]
    result = deduplicate(papers)
    assert len(result) == 2

def test_deduplicate_empty_list():
    result = deduplicate([])
    assert result == []

def test_deduplicate_mixed_identifiers():
    papers = [
        make_paper('1', doi='10.1234/same'),
        make_paper('2', doi='10.1234/same', abstract='richer'),
        make_paper('3', doi='10.5678/unique'),
        make_paper('4', arxiv_id='2401.99999'),
    ]
    result = deduplicate(papers)
    assert len(result) == 3
    # The paper with richer metadata (more non-null fields) should win
    winning_ids = {p.id for p in result}
    assert '1' not in winning_ids or '2' not in winning_ids  # only one of the dupes
    assert '3' in winning_ids
    assert '4' in winning_ids