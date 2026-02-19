from .openalex import OpenAlexProvider
from .semantic_scholar import SemanticScholarProvider
from .base import Provider

PROVIDER = {
    "openalex": OpenAlexProvider,
    "semantic_scholar": SemanticScholarProvider,
}

def get_provider(provider_name: str) -> Provider:
    return PROVIDER[provider_name]