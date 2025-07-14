"""
Core intelligent discovery engine for goal-based prospect discovery
"""

import asyncio
from typing import Dict, List, Any
from datetime import datetime

from ..utils.input_handler import display_progress, display_analysis_summary
from ..data.client_extractor import ClientExtractor
from ..data.live_updates import LiveUpdateManager
from ..data.profile_manager import ProfileManager
from .prompt_manager import PromptManager

class PregameClientDiscovery:
    """Intelligent discovery engine for goal-based prospect discovery"""
    
    def __init__(self, researcher):
        self.researcher = researcher
        self.prompt_manager = PromptManager()
        self.client_extractor = ClientExtractor()
        self.profile_manager = ProfileManager()
        self.live_update_manager = None
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for cross-platform compatibility
        
        Args:
            filename: Raw filename string
            
        Returns:
            str: Sanitized filename safe for file systems
        """
        import re
        
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        
        # Remove or replace invalid characters for Windows/Unix
        # Invalid chars: < > : " | ? * \ / and newlines/control chars
        filename = re.sub(r'[<>:"|?*\\/\n\r\t\f\v]', '', filename)
        
        # Replace multiple underscores with single underscore
        filename = re.sub(r'_+', '_', filename)
        
        # Remove leading/trailing underscores and dots
        filename = filename.strip('_.')
        
        # Ensure filename isn't empty
        if not filename:
            filename = 'untitled'
            
        # Limit length to avoid filesystem issues
        if len(filename) > 50:
            filename = filename[:50]
            
        return filename
        
    async def discover_prospects(self, company_data: Dict[str, str], goal: str, preferences: Dict[str, any]) -> List[Dict]:
        """
        Intelligent prospect discovery pipeline
        
        Args:
            company_data: User's company information
            goal: User's specific goal
            preferences: Discovery preferences
            
        Returns:
            List[Dict]: List of qualified prospects
        """
        target_count = preferences.get('target_count', 15)
        
        # Initialize live updates
        company_name = self._sanitize_filename(company_data.get('company_name', 'company'))
        goal_part = self._sanitize_filename(goal)[:20]  # Limit length
        live_update_file = f"pregame_{company_name}_{goal_part}_live.json"
        self.live_update_manager = LiveUpdateManager(live_update_file)
        
        await self.live_update_manager.update_stage("analysis", "starting")
        
        # Stage 1: AI Analysis of company and goal
        print(f"🧠 Stage 1: AI Analysis - Understanding your company and goal...")
        analysis = await self.analyze_company_and_goal(company_data, goal)
        
        # Display analysis to user
        display_analysis_summary(analysis)
        
        await self.live_update_manager.update_stage("discovery", "starting")
        
        # Stage 2: Intelligent Discovery
        print(f"🔍 Stage 2: Discovering prospects based on AI analysis...")
        
        # Generate smart search queries
        search_queries = self.prompt_manager.generate_smart_search_queries(company_data, goal, analysis)
        
        all_prospects = []
        discovery_prompts = self.prompt_manager.get_intelligent_discovery_prompts(company_data, goal, analysis)
        
        # Execute searches
        for i, query in enumerate(search_queries, 1):
            display_progress("Search", f"{query}", i, len(search_queries))
            
            try:
                result = await self.researcher.research(
                    query=query,
                    breadth=2,
                    depth=1,
                    system_prompts=discovery_prompts
                )
                
                # Debug: Log the research result structure
                await self.live_update_manager.log_message(f"Research result type: {type(result)}", 'info')
                if isinstance(result, dict):
                    await self.live_update_manager.log_message(f"Research result keys: {list(result.keys())}", 'info')
                    if 'report' in result:
                        report_preview = str(result['report'])[:200] + "..." if len(str(result['report'])) > 200 else str(result['report'])
                        await self.live_update_manager.log_message(f"Report preview: {report_preview}", 'info')
                
                # Extract prospects from results
                prospects = self.client_extractor.extract_clients_from_result(result)
                await self.live_update_manager.log_message(f"Extracted {len(prospects)} prospects from query {i}", 'info')
                
                # Debug: Log prospect details if any found
                if prospects:
                    for j, prospect in enumerate(prospects[:2]):  # Log first 2 prospects
                        await self.live_update_manager.log_message(f"Prospect {j+1}: {prospect.get('name', 'No name')} - {prospect.get('business', 'No business info')}", 'info')
                else:
                    await self.live_update_manager.log_message("No prospects extracted from this search", 'warning')
                
                all_prospects.extend(prospects)
                
                # Update live tracking
                for prospect in prospects:
                    await self.live_update_manager.add_client(prospect)
                
                await self.live_update_manager.update_progress("discovery", i, len(search_queries))
                
                print(f"   ✅ Found {len(prospects)} prospects")
                
            except Exception as e:
                error_msg = f"Search failed: {e}"
                print(f"   ❌ {error_msg}")
                await self.live_update_manager.log_message(error_msg, 'error')
                continue
        
        # Remove duplicates
        unique_prospects = self.client_extractor.deduplicate_clients(all_prospects)
        
        print(f"\n🎯 Stage 3: Intelligent qualification of {len(unique_prospects)} prospects...")
        
        # Stage 3: Intelligent Qualification
        qualified_prospects = await self.qualify_prospects_intelligently(
            unique_prospects[:target_count*2], 
            company_data,
            goal,
            target_count
        )
        
        # Stage 4: Save Prospect Profiles
        print(f"\n💾 Stage 4: Saving {len(qualified_prospects)} prospect profiles...")
        
        session_id = f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        saved_profile_ids = self.profile_manager.save_prospects_from_discovery(
            qualified_prospects, 
            company_data, 
            goal, 
            session_id
        )
        
        print(f"✅ Saved {len(saved_profile_ids)} prospect profiles")
        
        # Complete the discovery
        final_results = {
            'company_data': company_data,
            'goal': goal,
            'analysis': analysis,
            'prospects': qualified_prospects,
            'preferences': preferences,
            'saved_profiles': saved_profile_ids
        }
        
        await self.live_update_manager.complete_discovery(final_results)
        
        return qualified_prospects
    
    async def analyze_company_and_goal(self, company_data: Dict[str, str], goal: str) -> Dict[str, str]:
        """
        Use AI to analyze company data and goal to determine discovery strategy
        
        Args:
            company_data: User's company information
            goal: User's specific goal
            
        Returns:
            Dict[str, str]: Analysis results
        """
        try:
            analysis_prompts = self.prompt_manager.analyze_company_and_goal(company_data, goal)
            
            result = await self.researcher.research(
                query=f"Analyze {company_data.get('company_name', 'company')} goal: {goal}",
                breadth=1,
                depth=1,
                system_prompts=analysis_prompts
            )
            
            # Parse the analysis result
            if isinstance(result, dict) and 'report' in result:
                analysis = self.prompt_manager.get_goal_analysis_summary(result['report'])
                
                # Log the analysis
                await self.live_update_manager.log_message(f"AI Analysis completed: {analysis}", 'info')
                
                return analysis
            else:
                # Fallback analysis
                return {
                    'prospect_type': 'companies',
                    'target_industry': company_data.get('industry', 'business'),
                    'search_strategy': 'broad search',
                    'key_criteria': 'relevant businesses'
                }
                
        except Exception as e:
            await self.live_update_manager.log_message(f"Analysis failed: {e}", 'error')
            print(f"   ❌ Analysis failed: {e}")
            
            # Return fallback analysis
            return {
                'prospect_type': 'companies',
                'target_industry': company_data.get('industry', 'business'),
                'search_strategy': 'broad search',
                'key_criteria': 'relevant businesses'
            }
    
    async def qualify_prospects_intelligently(self, prospects: List[Dict], company_data: Dict[str, str], goal: str, target_count: int) -> List[Dict]:
        """
        Qualify prospects using intelligent, goal-aware prompts
        
        Args:
            prospects: List of prospects to qualify
            company_data: User's company information
            goal: User's specific goal
            target_count: Target number of qualified prospects
            
        Returns:
            List[Dict]: List of qualified prospects
        """
        qualified = []
        
        for i, prospect in enumerate(prospects[:target_count], 1):
            if len(qualified) >= target_count:
                break
                
            prospect_name = prospect.get('name', '')
            display_progress("Qualifying", f"{prospect_name}", i, min(len(prospects), target_count))
            
            try:
                # Intelligent qualification
                qualification_query = f"{prospect_name} {goal} qualification research"
                qualification_prompts = self.prompt_manager.get_intelligent_qualification_prompts(
                    prospect_name, company_data, goal
                )
                
                result = await self.researcher.research(
                    query=qualification_query,
                    breadth=3,
                    depth=2,
                    system_prompts=qualification_prompts
                )
                
                # Enrich prospect data
                enhanced_prospect = self.client_extractor.enrich_client_data(prospect, result)
                
                # Add goal-specific context
                enhanced_prospect['goal_alignment'] = self.assess_goal_alignment(prospect, goal, result)
                
                qualified.append(enhanced_prospect)
                
                # Update progress
                await self.live_update_manager.update_progress("qualification", i, target_count)
                
            except Exception as e:
                error_msg = f"Qualification failed for {prospect_name}: {e}"
                print(f"   ❌ {error_msg}")
                await self.live_update_manager.log_message(error_msg, 'error')
                continue
        
        return qualified
    
    def assess_goal_alignment(self, prospect: Dict, goal: str, qualification_result: Dict) -> Dict[str, any]:
        """
        Assess how well the prospect aligns with the user's goal
        
        Args:
            prospect: Prospect data
            goal: User's goal
            qualification_result: Deep research results
            
        Returns:
            Dict[str, any]: Goal alignment assessment
        """
        # Simple alignment assessment - in production, you'd use more sophisticated analysis
        alignment = {
            'relevance_score': 'Medium',  # High/Medium/Low
            'fit_reasons': [],
            'potential_value': 'To be determined',
            'approach_priority': 'Medium'
        }
        
        # Check for goal keywords in prospect data
        goal_lower = goal.lower()
        prospect_text = f"{prospect.get('business', '')} {prospect.get('need', '')} {prospect.get('signals', '')}".lower()
        
        if 'investor' in goal_lower:
            if 'fund' in prospect_text or 'invest' in prospect_text:
                alignment['relevance_score'] = 'High'
                alignment['fit_reasons'].append('Investment focus detected')
        elif 'client' in goal_lower:
            if 'need' in prospect_text or 'problem' in prospect_text:
                alignment['relevance_score'] = 'High'
                alignment['fit_reasons'].append('Clear need identified')
        elif 'partner' in goal_lower:
            if 'partner' in prospect_text or 'collaboration' in prospect_text:
                alignment['relevance_score'] = 'High'
                alignment['fit_reasons'].append('Partnership potential')
        
        return alignment
    
    def format_intelligent_report(self, prospects: List[Dict], company_data: Dict[str, str], goal: str, analysis: Dict[str, str], saved_profiles: List[str] = None) -> str:
        """
        Format intelligent discovery report
        
        Args:
            prospects: List of discovered prospects
            company_data: User's company information
            goal: User's goal
            analysis: AI analysis results
            
        Returns:
            str: Formatted report
        """
        company_name = company_data.get('company_name', 'Your Company')
        
        report = f"""
# 🎯 PREGAME INTELLIGENT DISCOVERY REPORT

**Company:** {company_name}
**Goal:** {goal}
**Prospects Found:** {len(prospects)}
**Research Date:** {asyncio.get_event_loop().time()}

## 🧠 AI ANALYSIS SUMMARY

**Prospect Type:** {analysis.get('prospect_type', 'Not determined')}
**Target Industry:** {analysis.get('target_industry', 'Not determined')}
**Search Strategy:** {analysis.get('search_strategy', 'Not determined')}
**Key Criteria:** {analysis.get('key_criteria', 'Not determined')}

## 📊 EXECUTIVE SUMMARY

Based on AI analysis of {company_name} and the goal "{goal}", we found {len(prospects)} qualified prospects that align with your objectives.

## 🎯 PROSPECT LIST

"""
        
        for i, prospect in enumerate(prospects, 1):
            goal_alignment = prospect.get('goal_alignment', {})
            relevance_score = goal_alignment.get('relevance_score', 'Medium')
            
            report += f"""
**{i}. {prospect.get('name', 'Unknown Prospect')}** (Relevance: {relevance_score})
- **Contact:** {prospect.get('contacts', 'Research needed')}
- **Business:** {prospect.get('business', 'Not specified')}
- **Goal Relevance:** {prospect.get('need', 'To be determined')}
- **Recent Signals:** {prospect.get('signals', 'None found')}
- **Location:** {prospect.get('location', 'Not specified')}
- **Fit Reasons:** {', '.join(goal_alignment.get('fit_reasons', ['Standard match']))}

"""
        
        report += f"""
## 🚀 NEXT STEPS

1. **Prioritize High-Relevance Prospects** - Focus on prospects with "High" relevance scores
2. **Personalize Outreach** - Use the goal alignment data to craft targeted messages
3. **Leverage Insights** - Use the AI analysis to refine your approach
4. **Track Engagement** - Monitor responses and update prospect intelligence

## 💾 PROSPECT PROFILES SAVED

{f"✅ **{len(saved_profiles)} prospect profiles** have been saved to your local database" if saved_profiles else "❌ No profiles were saved"}

- **Access Profiles:** Use the profile management CLI to view and manage saved profiles
- **Profile Search:** Search profiles by company, goal, relevance, status, or tags
- **Profile Updates:** Add notes, interactions, and track engagement status
- **Data Export:** Export profiles to CSV for external systems

## 📈 INTELLIGENT INSIGHTS

- **AI Analysis:** Successfully analyzed company profile and goal
- **Smart Search:** Used {analysis.get('prospect_type', 'targeted')} search strategy
- **Goal Alignment:** Each prospect assessed for fit with: {goal}
- **Recommendation:** Focus on prospects with specific pain points matching your value proposition

## 🔄 CONTINUOUS IMPROVEMENT

- **Success Metrics:** Track response rates by relevance score
- **Feedback Loop:** Update analysis based on prospect responses
- **Refinement:** Adjust search criteria based on results
- **Profile Intelligence:** Continuously update saved profiles with new interactions

*Generated by Pregame Intelligent Discovery Engine*
"""
        
        return report 