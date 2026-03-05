from typing import TypedDict, List, Dict, Any

class ResearchState(TypedDict):
    """State for the research graph."""
    topic: str
    search_queries: List[str]
    search_results: List[Dict]
    notes: List[str]
    outline: str
    sections: Dict[str, str]
    report: str
    sources: List[Dict]
    iteration: int