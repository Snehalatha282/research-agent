from research import ResearchWorkflow
from models import ResearchState
from datetime import datetime
import json
import os

class ResearchAgent:
    def __init__(self):
        """Initialize the research agent."""
        self.workflow = ResearchWorkflow()
        self.history = []
        
        # Create output directory
        os.makedirs("reports", exist_ok=True)
    
    def research(self, topic: str) -> dict:
        """Research a topic and generate report."""
        print(f"\n🔍 Researching: {topic}")
        print("=" * 50)
        
        # Initialize state
        initial_state = ResearchState(
            topic=topic,
            search_queries=[],
            search_results=[],
            notes=[],
            outline="",
            sections={},
            report="",
            sources=[],
            iteration=0
        )
        
        # Run the workflow
        try:
            final_state = self.workflow.graph.invoke(initial_state)
            
            # Save to history
            result = {
                "topic": topic,
                "report": final_state.get("report", "No report generated"),
                "sources": final_state.get("sources", []),
                "timestamp": datetime.now().isoformat()
            }
            self.history.append(result)
            
            return result
            
        except Exception as e:
            print(f"❌ Error during research: {e}")
            return {
                "topic": topic,
                "report": f"Error: {e}",
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
    
    def save_report(self, result: dict, filename: str = None):
        """Save report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_topic = "".join(c for c in result['topic'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_topic = safe_topic.replace(' ', '_')[:30]
            filename = f"reports/{safe_topic}_{timestamp}.txt"
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Save text report
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Topic: {result['topic']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(result["report"])
            f.write("\n\n" + "=" * 50 + "\n")
            f.write("SOURCES:\n")
            for src in result["sources"]:
                f.write(f"- {src.get('url', 'No URL')}\n")
        
        print(f"✅ Report saved: {filename}")
        
        # Save metadata
        meta_file = filename.replace(".txt", "_meta.json")
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "topic": result["topic"],
                "timestamp": result["timestamp"],
                "sources": result["sources"],
                "report_file": filename
            }, f, indent=2)
        
        return filename