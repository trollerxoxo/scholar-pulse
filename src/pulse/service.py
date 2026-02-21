from pulse.models import Paper, Query
from pulse.config import RankingConfig
import math
from datetime import date

def rank_papers(papers: list[Paper], query: Query, config: RankingConfig) -> list[Paper]:
    
    if not papers:
        return []
    
    max_citations_in_set = max(p.citation_count for p in papers)
    if max_citations_in_set > 0:
        wc = config.weight_citation
        wr = config.weight_recency
        wk = config.weight_keyword
    else:
        wk = config.weight_keyword + (config.weight_citation/2)
        wr = config.weight_recency + (config.weight_citation/2)
        wc = 0

    query_keyword = set(keyword.lower() for keyword in query.keywords)
    
    for paper in papers:
        if max_citations_in_set > 0:
            C_norm = math.log( 1 + paper.citation_count) / math.log(1 + max_citations_in_set)
        else:
            C_norm = 0

        paper_keyword = set(keyword.lower() for keyword in paper.keywords)
        matching_keywords = query_keyword.intersection(paper_keyword)
        S = len(matching_keywords)/len(query_keyword) if query_keyword else 0
       

        days_since_publication = (date.today() - paper.published_date).days
        Recency = 1 / (days_since_publication + 1)
        
        R = wc * C_norm + wr * Recency + wk * S
       
        paper.relevance_score = R

    return sorted(papers, key=lambda p: p.relevance_score, reverse=True)

def deduplicate(papers: list[Paper]) -> list[Paper]:
    unique_papers = {}
    for paper in papers:
        key = paper.doi or paper.arxiv_id or paper.openalex_id or paper.id
        
        if key:
            if key not in unique_papers:
                unique_papers[key] = paper
            else:
                existing = unique_papers[key]   
                existing_metadata_field_count = sum((1 for value in existing.model_dump().values() if value not in [None, ""]))
                new_metadata_field_count = sum((1 for value in paper.model_dump().values() if value not in [None, ""]))
                if new_metadata_field_count > existing_metadata_field_count:
                    unique_papers[key] = paper
    return list(unique_papers.values())