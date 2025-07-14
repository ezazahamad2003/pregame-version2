"""
Input handling utilities for Pregame Client Discovery
"""

from typing import Tuple, Dict

def get_user_company_data() -> Dict[str, str]:
    """
    Get user's company data for intelligent prospect matching
    
    Returns:
        Dict[str, str]: Company information dictionary
    """
    print("🏢 Tell us about your company:")
    print("-" * 30)
    
    company_data = {}
    
    # Company basics
    company_data['company_name'] = input("Company name: ").strip()
    company_data['industry'] = input("Industry (e.g., SaaS, Consulting, AI, etc.): ").strip()
    company_data['company_size'] = input("Company size (e.g., 1-10, 10-50, 50-200): ").strip() or "1-10"
    company_data['stage'] = input("Company stage (e.g., Startup, Growth, Enterprise): ").strip() or "Startup"
    
    # What they do
    company_data['what_we_do'] = input("What does your company do? (1-2 sentences): ").strip()
    company_data['target_customers'] = input("Who are your typical customers? (e.g., B2B SaaS companies, SMB retailers): ").strip()
    company_data['value_proposition'] = input("What's your main value proposition? (what problem do you solve?): ").strip()
    
    # Business context
    company_data['location'] = input("Primary location/market (default: US): ").strip() or "US"
    company_data['budget_range'] = input("Typical client budget range (optional): ").strip() or "Not specified"
    
    return company_data

def get_user_goal() -> str:
    """
    Get user's specific goal for prospect discovery
    
    Returns:
        str: User's goal
    """
    print("\n🎯 What's your goal?")
    print("-" * 20)
    
    goal = input("Describe your goal (e.g., 'Find 20 B2B SaaS companies that need AI automation', 'Get clients for our marketing agency', 'Find investors for our startup'): ").strip()
    
    return goal

def get_discovery_preferences() -> Dict[str, any]:
    """
    Get user preferences for the discovery process
    
    Returns:
        Dict[str, any]: Discovery preferences
    """
    print("\n⚙️ Discovery Preferences:")
    print("-" * 25)
    
    preferences = {}
    
    # Number of prospects
    try:
        count = int(input("How many prospects do you want to find? (default: 15): ") or "15")
        preferences['target_count'] = max(5, min(50, count))
    except ValueError:
        preferences['target_count'] = 15
    
    # Geographic focus
    geo_focus = input("Geographic focus (e.g., 'Bay Area', 'US', 'Global', 'Europe'): ").strip()
    preferences['geographic_focus'] = geo_focus if geo_focus else "US"
    
    # Priority level
    priority_options = ["speed", "quality", "balanced"]
    priority = input("Priority (speed/quality/balanced - default: balanced): ").strip().lower()
    preferences['priority'] = priority if priority in priority_options else "balanced"
    
    return preferences

def get_complete_discovery_input() -> Tuple[Dict[str, str], str, Dict[str, any]]:
    """
    Get complete input for intelligent client discovery
    
    Returns:
        Tuple[Dict[str, str], str, Dict[str, any]]: (company_data, goal, preferences)
    """
    print("🎯 Pregame Intelligent Client Discovery")
    print("=" * 50)
    print("Let's analyze your company and goals to find the perfect prospects!")
    print()
    
    # Get company data
    company_data = get_user_company_data()
    
    # Get goal
    goal = get_user_goal()
    
    # Get preferences
    preferences = get_discovery_preferences()
    
    # Display summary
    print(f"\n📊 Discovery Setup Summary:")
    print(f"   Company: {company_data.get('company_name', 'Not provided')}")
    print(f"   Industry: {company_data.get('industry', 'Not provided')}")
    print(f"   Goal: {goal}")
    print(f"   Target Count: {preferences['target_count']}")
    print(f"   Geographic Focus: {preferences['geographic_focus']}")
    print(f"   Priority: {preferences['priority']}")
    print("=" * 50)
    
    return company_data, goal, preferences

def display_progress(stage: str, message: str, progress: int = None, total: int = None):
    """
    Display progress information to the user
    
    Args:
        stage: Current stage name
        message: Progress message
        progress: Current progress (optional)
        total: Total items (optional)
    """
    if progress is not None and total is not None:
        print(f"   {stage} [{progress}/{total}]: {message}")
    else:
        print(f"   {stage}: {message}")

def display_analysis_summary(analysis: Dict[str, any]):
    """
    Display the AI's analysis of the user's company and goal
    
    Args:
        analysis: AI analysis results
    """
    print("\n🧠 AI Analysis Results:")
    print("-" * 30)
    print(f"Prospect Type: {analysis.get('prospect_type', 'Not determined')}")
    print(f"Target Industry: {analysis.get('target_industry', 'Not determined')}")
    print(f"Search Strategy: {analysis.get('search_strategy', 'Not determined')}")
    print(f"Key Criteria: {analysis.get('key_criteria', 'Not determined')}")
    print()

def display_summary(prospects: list, goal: str, company_name: str):
    """
    Display final summary of discovered prospects
    
    Args:
        prospects: List of discovered prospects
        goal: User's goal
        company_name: User's company name
    """
    print("\n" + "=" * 60)
    print("🎯 PREGAME INTELLIGENT DISCOVERY RESULTS")
    print("=" * 60)
    print(f"Company: {company_name}")
    print(f"Goal: {goal}")
    print(f"Prospects Found: {len(prospects)}")
    print("=" * 60)

def confirm_proceed() -> bool:
    """
    Ask user to confirm before proceeding with discovery
    
    Returns:
        bool: True if user wants to proceed
    """
    response = input("\n🚀 Ready to start intelligent prospect discovery? (y/n): ").strip().lower()
    return response in ['y', 'yes', ''] 