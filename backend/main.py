"""
Main entry point for Pregame Intelligent Discovery Engine

This is the goal-based, intelligent version of the Pregame prospect discovery system.
"""

import asyncio
from pathlib import Path

# Import our modular components
from src.utils.env_manager import get_api_keys, validate_api_keys
from src.utils.input_handler import get_complete_discovery_input, display_summary, confirm_proceed
from src.core.discovery_engine import PregameClientDiscovery


async def main():
    """Main entry point for Pregame Intelligent Discovery"""
    
    print("🎯 Pregame Intelligent Discovery Engine - Goal-Based Version")
    print("=" * 60)
    
    try:
        # Import required dependencies
        from langchain_deepresearch import DeepResearcher
        from langchain_openai import ChatOpenAI
        
        # Get comprehensive user input
        company_data, goal, preferences = get_complete_discovery_input()
        
        # Confirm before proceeding
        if not confirm_proceed():
            print("👋 Discovery cancelled. Run again when you're ready!")
            return
        
        print("\n🔧 Setting up AI systems...")
        
        # Get and validate API keys
        api_keys = get_api_keys()
        
        if not validate_api_keys():
            print("❌ OpenAI API key not found in .env.local file")
            print("Please add your OpenAI API key to .env.local file")
            return
        
        print("✅ AI systems configured!")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_keys['openai_key'],
            temperature=0.1
        )
        
        # Initialize DeepResearcher
        researcher = DeepResearcher(
            llm=llm,
            google_api_key=api_keys['google_api_key'],
            google_cx=api_keys['google_cx']
        )
        
        # Initialize Pregame Intelligent Discovery Engine
        discovery_engine = PregameClientDiscovery(researcher)
        
        print(f"\n🚀 Starting intelligent discovery...")
        print(f"   Company: {company_data.get('company_name', 'Your Company')}")
        print(f"   Goal: {goal}")
        print(f"   This may take several minutes...")
        print("")
        
        # Run intelligent discovery pipeline
        prospects = await discovery_engine.discover_prospects(
            company_data=company_data,
            goal=goal,
            preferences=preferences
        )
        
        # Get AI analysis for reporting
        analysis = await discovery_engine.analyze_company_and_goal(company_data, goal)
        
        # Generate intelligent report with saved profiles info
        final_report = discovery_engine.format_intelligent_report(prospects, company_data, goal, analysis, [])
        
        # Display results
        display_summary(prospects, goal, company_data.get('company_name', 'Your Company'))
        print(final_report)
        
        # Save results to file
        company_name = company_data.get('company_name', 'company').replace(' ', '_')
        goal_short = goal.replace(' ', '_')[:20]
        output_file = f"pregame_discovery_{company_name}_{goal_short}.md"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_report)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Show live update file tip
        live_file = f"pregame_{company_name}_{goal_short}_live.json"
        if Path(live_file).exists():
            print(f"💡 Live progress was tracked in: {live_file}")
        
        # Show intelligent insights
        print(f"\n🧠 Intelligent Insights:")
        print(f"   - AI determined you need: {analysis.get('prospect_type', 'prospects')}")
        print(f"   - Target industry: {analysis.get('target_industry', 'various')}")
        print(f"   - Search strategy: {analysis.get('search_strategy', 'comprehensive')}")
        print(f"   - {len(prospects)} prospects found with goal alignment analysis")
        
        # Profile management info
        saved_profiles = []  # CLI version doesn't save profiles to database
        if saved_profiles:
            print(f"\n💾 Profile Management:")
            print(f"   - {len(saved_profiles)} prospect profiles saved to local database")
            print(f"   - Run 'python profiles_manager.py' to manage saved profiles")
            print(f"   - Search, update, export, and track engagement with prospects")
        
        # Success tips
        print(f"\n🎯 Success Tips:")
        print(f"   - Focus on 'High' relevance prospects first")
        print(f"   - Use the goal alignment data for personalized outreach")
        print(f"   - Leverage the AI analysis insights in your conversations")
        print(f"   - Track which approaches work best for future discoveries")
        print(f"   - Use profile management to track prospect engagement over time")
        
        # Ask if user wants to manage profiles now
        if saved_profiles:
            manage_now = input("\nWould you like to manage profiles now? (y/n): ").strip().lower()
            if manage_now == 'y':
                from src.utils.profile_cli import ProfileCLI
                print("\n" + "="*50)
                print("SWITCHING TO PROFILE MANAGEMENT MODE")
                print("="*50)
                cli = ProfileCLI()
                cli.run()
        
        return prospects
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure langchain-deepresearch and langchain-openai are installed")
        print("Run: pip install langchain-deepresearch langchain-openai")
        return None
    except KeyboardInterrupt:
        print("\n❌ Intelligent discovery interrupted by user")
        return None
    except Exception as e:
        print(f"❌ Error during intelligent discovery: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("🎯 Pregame Intelligent Discovery Engine")
    print("AI-powered, goal-based prospect discovery for any business objective...")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Happy prospecting with AI intelligence!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc() 