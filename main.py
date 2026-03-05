from agent import ResearchAgent
import sys

def clear_screen():
    """Clear terminal screen."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main entry point."""
    clear_screen()
    print("""
    ╔══════════════════════════════════════╗
    ║   🤖 GROQ RESEARCH AGENT             ║
    ║   LangGraph + LangChain              ║
    ╚══════════════════════════════════════╝
    """)
    
    print("Initializing agent...")
    
    # Initialize agent
    try:
        agent = ResearchAgent()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing agent: {e}")
        print("\nPlease check:")
        print("1. Your GROQ_API_KEY in .env file")
        print("2. Internet connection")
        print("3. All dependencies are installed")
        sys.exit(1)
    
    while True:
        print("\n" + "-" * 40)
        print("1. 🔍 Research a topic")
        print("2. 📚 View history")
        print("3. ❌ Exit")
        print("-" * 40)
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            topic = input("\n📝 Enter research topic: ").strip()
            if topic:
                print("\n" + "🔄 Researching... (this may take 2-3 minutes)")
                
                # Do research
                result = agent.research(topic)
                
                # Show preview
                print("\n" + "=" * 50)
                print("📊 REPORT PREVIEW")
                print("=" * 50)
                
                if result["report"]:
                    preview = result["report"][:500] + "..." if len(result["report"]) > 500 else result["report"]
                    print(preview)
                else:
                    print("No report generated")
                
                # Save?
                save = input("\n💾 Save full report? (y/n): ").lower().strip()
                if save == "y":
                    filename = agent.save_report(result)
                    print(f"📁 Report saved as: {filename}")
        
        elif choice == "2":
            if agent.history:
                print("\n📚 Research History:")
                for i, item in enumerate(agent.history, 1):
                    date = item['timestamp'][:10] if 'timestamp' in item else 'Unknown'
                    print(f"{i}. {item['topic']} - {date}")
            else:
                print("\n📭 No research history yet")
        
        elif choice == "3":
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()