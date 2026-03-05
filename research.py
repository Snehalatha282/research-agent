from langgraph.graph import StateGraph, END
from models import ResearchState
from tools import ResearchTools
from config import GROQ_API_KEY, MAX_ITERATIONS
from langchain_core.messages import HumanMessage  # Changed import

class ResearchWorkflow:
    def __init__(self):
        """Initialize the research workflow."""
        self.tools = ResearchTools(GROQ_API_KEY)
        self.graph = self._create_graph()
    
    def _create_graph(self):
        """Create LangGraph workflow."""
        workflow = StateGraph(ResearchState)
        
        # Add nodes
        workflow.add_node("generate_queries", self.generate_queries)
        workflow.add_node("search_web", self.search_web)
        workflow.add_node("analyze_content", self.analyze_content)
        workflow.add_node("create_outline", self.create_outline)
        workflow.add_node("write_report", self.write_report)
        
        # Add edges
        workflow.set_entry_point("generate_queries")
        workflow.add_edge("generate_queries", "search_web")
        workflow.add_edge("search_web", "analyze_content")
        workflow.add_edge("analyze_content", "create_outline")
        workflow.add_edge("create_outline", "write_report")
        workflow.add_edge("write_report", END)
        
        return workflow.compile()
    
    def generate_queries(self, state: ResearchState) -> ResearchState:
        """Generate search queries using LLM."""
        prompt = f"""Generate 3 specific search queries for researching: {state['topic']}
        
        Make them specific and targeted to get good results.
        Return one query per line, nothing else:"""
        
        try:
            response = self.tools.llm.invoke([HumanMessage(content=prompt)])
            queries = [q.strip() for q in response.content.split('\n') 
                      if q.strip() and not q[0].isdigit()][:3]
            
            # If no queries found, use defaults
            if not queries:
                queries = [
                    f"{state['topic']} overview 2024",
                    f"{state['topic']} latest developments",
                    f"{state['topic']} key facts and analysis"
                ]
        except:
            queries = [
                f"{state['topic']} overview",
                f"{state['topic']} latest",
                f"{state['topic']} analysis"
            ]
        
        print(f"\n🔍 Generated queries:")
        for i, q in enumerate(queries, 1):
            print(f"   {i}. {q}")
        
        return {**state, "search_queries": queries}
    
    def search_web(self, state: ResearchState) -> ResearchState:
        """Execute web searches."""
        all_results = []
        
        for query in state["search_queries"]:
            print(f"  🔎 Searching: {query[:50]}...")
            results = self.tools.web_search_sync(query)
            all_results.extend(results)
            import time
            time.sleep(1)  # Be polite to servers
        
        print(f"  ✅ Found {len(all_results)} results")
        return {**state, "search_results": all_results}
    
    def analyze_content(self, state: ResearchState) -> ResearchState:
        """Analyze and extract key information."""
        notes = []
        sources = []
        
        for i, result in enumerate(state["search_results"]):
            print(f"  📝 Analyzing result {i+1}...")
            
            # Extract key points
            key_points = self.tools.extract_key_points(
                result["content"], 
                state["topic"]
            )
            
            if key_points and "Error" not in key_points:
                notes.append(f"📌 From {result.get('title', 'Source')}:\n{key_points}")
                sources.append({
                    "url": result["url"],
                    "title": result.get("title", f"Source {i+1}")
                })
        
        print(f"  ✅ Extracted {len(notes)} key insights")
        return {**state, "notes": notes, "sources": sources}
    
    def create_outline(self, state: ResearchState) -> ResearchState:
        """Create report outline."""
        if not state["notes"]:
            outline = """Executive Summary
Introduction
Main Findings
Analysis
Conclusion
Recommendations"""
            return {**state, "outline": outline}
        
        notes_text = "\n\n".join(state["notes"])
        
        prompt = f"""Create a report outline for "{state['topic']}" with these sections:
        
        Based on these notes:
        {notes_text[:2000]}
        
        Return the outline with these main sections:
        - Executive Summary
        - Introduction
        - Main Findings (with 2-3 subsections)
        - Analysis
        - Conclusion
        - Recommendations
        
        Keep it simple and structured."""
        
        try:
            response = self.tools.llm.invoke([HumanMessage(content=prompt)])
            outline = response.content
        except:
            outline = """Executive Summary
Introduction
Main Findings
- Key Discovery 1
- Key Discovery 2
- Key Discovery 3
Analysis
Conclusion
Recommendations"""
        
        return {**state, "outline": outline}
    
    def write_report(self, state: ResearchState) -> ResearchState:
        """Write the final report."""
        if not state["notes"]:
            report = f"""# Research Report: {state['topic']}

## Executive Summary
No research data could be gathered for this topic. Please try a more specific topic or check your internet connection.

## Conclusion
Unable to generate report due to lack of research data.
"""
            return {**state, "report": report}
        
        notes_text = "\n\n".join(state["notes"])
        sources_text = "\n".join([f"- {s['title']}: {s['url']}" for s in state["sources"]])
        
        prompt = f"""Write a comprehensive research report on "{state['topic']}".

Research findings:
{notes_text[:3000]}

Sources:
{sources_text}

Format the report with:
# Title: {state['topic']} - Research Report

## Executive Summary
(2-3 paragraphs summarizing key findings)

## Introduction
(Background and context)

## Main Findings
(Synthesize the key points from research)

## Analysis
(Interpretation of findings)

## Conclusion
(Summary and implications)

## References
(List all sources)

Make it professional, well-structured, and based on the research findings."""
        
        try:
            response = self.tools.llm.invoke([HumanMessage(content=prompt)])
            report = response.content
        except Exception as e:
            report = f"""# Research Report: {state['topic']}

## Executive Summary
Research completed but report generation encountered an error.

## Research Notes
{notes_text[:1000]}

## Sources
{sources_text}
"""
        
        return {**state, "report": report}