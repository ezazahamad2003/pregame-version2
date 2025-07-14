import asyncio
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any

# Add the parent directory to the path to access the .env.local file
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

def get_client_discovery_input():
    """Get client discovery criteria from user"""
    print("🎯 Pregame Client Discovery Engine")
    print("="*50)
    
    # Get discovery criteria
    solution = input("Your solution/service (default: AI solutions): ").strip() or "AI solutions"
    location = input("Target location (default: Bay Area): ").strip() or "Bay Area"
    client_type = input("Client type - companies/individuals/both (default: both): ").strip() or "both"
    
    try:
        count = int(input("Number of clients needed (default: 10): ") or "10")
        count = max(5, min(30, count))  # Clamp between 5-30
    except ValueError:
        count = 10
    
    print(f"\n🎯 Discovery Setup:")
    print(f"   Solution: {solution}")
    print(f"   Location: {location}")
    print(f"   Client Type: {client_type}")
    print(f"   Target Count: {count}")
    print("="*50)
    
    return solution, location, client_type, count

def read_env_file():
    """Read API keys from .env.local file"""
    # Check current directory first
    env_file = Path(".env.local")
    if not env_file.exists():
        # Check parent directory as fallback
        env_file = parent_dir / ".env.local"
    
    env_vars = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"')
    
    return env_vars

class PregameClientDiscovery:
    def __init__(self, researcher):
        self.researcher = researcher
        
    def get_discovery_prompts(self, solution: str, location: str, client_type: str):
        """Custom prompts for client discovery"""
        return {
            "query_generation": f"""You are a B2B client discovery specialist finding potential clients for {solution}.

            Target: {client_type} in {location} who might need {solution}.

            Generate specific search queries to find ACTUAL CLIENTS (companies or individuals), not general information.

            Focus on finding:
            - Company directories and business listings
            - Individual professionals and entrepreneurs
            - Recent business news and funding announcements
            - Job postings that reveal business needs
            - Industry-specific client lists and directories

            Generate targeted queries like:
            - "site:crunchbase.com {location} companies need {solution}"
            - "site:linkedin.com/in {location} CEO founder entrepreneur"
            - "{location} businesses {solution} implementation"
            - "site:angellist.com {location} startup founder"
            - "{location} {solution} client case studies"
            - "{solution} services {location} directory"

            Avoid generic queries like "{solution} trends" or "market analysis".""",

            "report_generation": f"""You are creating a CLIENT DISCOVERY REPORT for {solution} services.

            Extract information about potential CLIENTS (companies or individuals), not products or market trends.

            For each potential client found, extract:
            - Client name (company or individual)
            - Type (company/individual/entrepreneur)
            - Industry or business focus
            - Why they might need {solution}
            - Recent business activity (funding, growth, launches)
            - Location details
            - Contact information if available
            - Business size/stage

            Format as a client list:

            ## POTENTIAL CLIENTS: {solution.upper()}

            **1. [Client Name]**
            - Type: Company/Individual/Entrepreneur
            - Industry: Brief industry description
            - Business: What they do
            - {solution} Opportunity: Specific need or use case
            - Recent Activity: Funding/growth/news
            - Location: City, State
            - Size: Company size or individual status
            - Contact: Any contact info found

            **2. [Next Client]**
            ...

            Focus on extracting CLIENT DATA, not writing explanatory text.
            If you can't find specific clients, say "No specific clients found in this search" and suggest better search terms."""
        }

    async def discover_clients(self, solution: str, location: str, client_type: str, target_count: int = 10):
        """Main client discovery pipeline with live updates"""
        
        print(f"🔍 Stage 1: Discovering {solution} clients in {location}...")
        
        # Generate client-focused search queries based on type
        if client_type == "companies":
            discovery_queries = [
                f"site:crunchbase.com {location} companies technology",
                f"{location} business directory technology companies",
                f"site:linkedin.com/company {location} hiring",
                f"{location} startups funding 2024",
                f"site:angellist.com {location} companies",
            ]
        elif client_type == "individuals":
            discovery_queries = [
                f"site:linkedin.com/in {location} CEO founder entrepreneur",
                f"{location} business owner entrepreneur directory",
                f"site:twitter.com {location} startup founder",
                f"{location} individual consultant professional",
                f"site:crunchbase.com {location} founder CEO",
            ]
        else:  # both
            discovery_queries = [
                f"site:crunchbase.com {location} companies startups",
                f"site:linkedin.com/in {location} CEO founder",
                f"{location} business directory companies",
                f"site:angellist.com {location} startup",
                f"{location} entrepreneurs professionals directory",
            ]
        
        all_clients = []
        
        # Get custom prompts for client discovery
        custom_prompts = self.get_discovery_prompts(solution, location, client_type)
        
        # Create base filename for live updates
        base_filename = f"pregame_clients_{solution.replace(' ', '_')}_{location.replace(' ', '_')}"
        live_update_file = f"{base_filename}_live.json"
        
        for i, query in enumerate(discovery_queries, 1):
            print(f"   🔎 Search {i}/{len(discovery_queries)}: {query}")
            
            try:
                result = await self.researcher.research(
                    query=query,
                    breadth=3,  # More parallel searches for discovery
                    depth=1,    # Shallow depth for discovery
                    system_prompts=custom_prompts
                )
                
                # Extract clients from this search
                clients = self.extract_clients_from_result(result)
                all_clients.extend(clients)
                
                print(f"   ✅ Found {len(clients)} potential clients")
                
                # Save live update after each search
                await self.save_live_update(live_update_file, {
                    "stage": "discovery",
                    "completed_searches": i,
                    "total_searches": len(discovery_queries),
                    "clients_found_so_far": len(all_clients),
                    "current_query": query,
                    "latest_clients": clients,
                    "all_clients": all_clients,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
            except Exception as e:
                print(f"   ❌ Search failed: {e}")
                continue
        
        # Remove duplicates and filter
        unique_clients = self.deduplicate_clients(all_clients)
        
        print(f"\n🎯 Stage 2: Qualifying {len(unique_clients)} clients...")
        
        # Save update before qualification
        await self.save_live_update(live_update_file, {
            "stage": "qualification_start",
            "unique_clients_found": len(unique_clients),
            "clients_to_qualify": min(len(unique_clients), target_count),
            "unique_clients": unique_clients,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Qualify top clients with focused research
        qualified_clients = await self.qualify_clients_with_updates(
            unique_clients[:target_count*2], 
            solution, 
            target_count,
            live_update_file
        )
        
        return qualified_clients

    def extract_clients_from_result(self, result: Dict) -> List[Dict]:
        """Extract client data from research result with improved parsing"""
        clients = []
        
        if isinstance(result, dict) and 'report' in result:
            report = result['report']
            
            # Split by sections and parse more intelligently
            lines = report.split('\n')
            current_client = {}
            
            for line in lines:
                line = line.strip()
                
                # Look for client headers (various formats)
                if (line.startswith('**') and line.endswith('**')) or \
                   (line.startswith('###') or line.startswith('##')):
                    
                    # Save previous client if exists
                    if current_client and current_client.get('name'):
                        clients.append(current_client.copy())
                    
                    # Start new client
                    client_name = re.sub(r'[*#\d\.\s-]+', '', line).strip()
                    if client_name and len(client_name) > 2:
                        current_client = {'name': client_name}
                
                # Extract data fields with flexible parsing
                elif current_client and ':' in line:
                    if any(keyword in line.lower() for keyword in ['type:', 'client type:', 'category:']):
                        current_client['type'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['industry:', 'sector:', 'business:']):
                        current_client['industry'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['website:', 'url:', 'site:']):
                        current_client['website'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['opportunity:', 'need:', 'use case:']):
                        current_client['opportunity'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['activity:', 'signals:', 'recent:']):
                        current_client['activity'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['location:', 'address:', 'based:']):
                        current_client['location'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['size:', 'employees:', 'stage:']):
                        current_client['size'] = self.extract_value_after_colon(line)
                    elif any(keyword in line.lower() for keyword in ['contact:', 'email:', 'phone:']):
                        current_client['contact'] = self.extract_value_after_colon(line)
            
            # Don't forget the last client
            if current_client and current_client.get('name'):
                clients.append(current_client)
        
        return clients

    def extract_value_after_colon(self, line: str) -> str:
        """Helper to extract value after colon, cleaning markdown"""
        if ':' in line:
            value = line.split(':', 1)[1].strip()
            # Clean markdown formatting
            value = re.sub(r'[*_`-]+', '', value).strip()
            return value
        return ''

    def deduplicate_clients(self, clients: List[Dict]) -> List[Dict]:
        """Remove duplicate clients with better matching"""
        seen_names = set()
        unique_clients = []
        
        for client in clients:
            name = client.get('name', '').lower().strip()
            # Remove common business suffixes for better matching
            clean_name = re.sub(r'\b(inc|llc|corp|company|ltd|limited)\b', '', name).strip()
            
            if clean_name and clean_name not in seen_names and len(clean_name) > 2:
                seen_names.add(clean_name)
                unique_clients.append(client)
        
        return unique_clients

    async def save_live_update(self, filename: str, data: Dict):
        """Save live updates to file for real-time monitoring"""
        try:
            # Add metadata to the update
            update_data = {
                "live_update": True,
                "last_updated": asyncio.get_event_loop().time(),
                "status": data.get("stage", "processing"),
                **data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(update_data, f, indent=2, ensure_ascii=False)
                
            # Print live status update
            if data.get("stage") == "discovery":
                completed = data.get("completed_searches", 0)
                total = data.get("total_searches", 0)
                clients_found = data.get("clients_found_so_far", 0)
                print(f"   📊 Live Update: {completed}/{total} searches complete, {clients_found} clients found")
                
            elif data.get("stage") == "qualification":
                completed = data.get("completed_qualifications", 0)
                total = data.get("total_qualifications", 0)
                client_name = data.get("current_client", "")
                print(f"   📊 Live Update: Qualifying {completed}/{total} - {client_name}")
                
        except Exception as e:
            print(f"   ⚠️ Live update save failed: {e}")

    async def qualify_clients_with_updates(self, clients: List[Dict], solution: str, target_count: int, live_update_file: str) -> List[Dict]:
        """Focused qualification research on top clients with live updates"""
        qualified = []
        
        for i, client in enumerate(clients[:target_count], 1):
            if len(qualified) >= target_count:
                break
                
            client_name = client.get('name', '')
            print(f"   🔍 Qualifying {i}/{min(len(clients), target_count)}: {client_name}")
            
            # Save live update before qualification
            await self.save_live_update(live_update_file, {
                "stage": "qualification",
                "completed_qualifications": i-1,
                "total_qualifications": min(len(clients), target_count),
                "current_client": client_name,
                "qualified_so_far": len(qualified),
                "timestamp": asyncio.get_event_loop().time()
            })
            
            try:
                # Focused qualification query
                qualification_query = f"{client_name} business needs {solution} contact information recent news"
                
                result = await self.researcher.research(
                    query=qualification_query,
                    breadth=2,
                    depth=1,  # Keep shallow for speed
                    system_prompts=self.get_qualification_prompts(client_name, solution)
                )
                
                # Enhance client data with qualification results
                enhanced_client = client.copy()
                enhanced_client['qualification_research'] = result.get('report', '') if isinstance(result, dict) else str(result)
                enhanced_client['qualified'] = True
                enhanced_client['qualification_timestamp'] = asyncio.get_event_loop().time()
                
                qualified.append(enhanced_client)
                
                # Save live update after successful qualification
                await self.save_live_update(live_update_file, {
                    "stage": "qualification",
                    "completed_qualifications": i,
                    "total_qualifications": min(len(clients), target_count),
                    "current_client": f"{client_name} ✅ QUALIFIED",
                    "qualified_so_far": len(qualified),
                    "latest_qualified_client": enhanced_client,
                    "all_qualified_clients": qualified,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
            except Exception as e:
                print(f"   ❌ Qualification failed for {client_name}: {e}")
                # Add client anyway with basic info
                client['qualified'] = False
                client['qualification_error'] = str(e)
                qualified.append(client)
                continue
        
        # Final update
        await self.save_live_update(live_update_file, {
            "stage": "completed",
            "total_clients_qualified": len(qualified),
            "successful_qualifications": len([c for c in qualified if c.get('qualified')]),
            "final_qualified_clients": qualified,
            "completion_timestamp": asyncio.get_event_loop().time()
        })
        
        return qualified

    def get_qualification_prompts(self, client_name: str, solution: str):
        """Prompts for client qualification research"""
        return {
            "query_generation": f"""Research {client_name} for {solution} sales opportunity.

            Find specific information about:
            - Current business operations and challenges
            - Technology needs that {solution} could address
            - Recent business developments and growth
            - Decision maker contact information
            - Budget and purchasing signals

            Search for:
            - "{client_name} business challenges technology needs"
            - "{client_name} contact information leadership team"
            - "{client_name} recent news funding growth"
            - "{client_name} {solution} implementation use case"
            - "site:linkedin.com/in {client_name} founder CEO"
            """,

            "report_generation": f"""Create CLIENT QUALIFICATION for {client_name}.

            Structure your response as:

            ## CLIENT QUALIFICATION: {client_name}

            **Business Overview:**
            - Current operations and focus
            - Industry and market position
            - Business size and stage

            **{solution.title()} Opportunity:**
            - Specific use cases for {solution}
            - Current challenges and pain points
            - Technology gaps and needs
            - Potential ROI and value

            **Business Signals:**
            - Recent growth or funding
            - New initiatives or launches
            - Technology investments
            - Market expansion

            **Contact Intelligence:**
            - Key decision makers identified
            - Contact information found
            - Best outreach approach
            - Timing considerations

            **Qualification Score:** [High/Medium/Low] based on fit and readiness

            Focus on actionable sales intelligence for immediate outreach."""
        }

    def format_final_report(self, clients: List[Dict], solution: str, location: str) -> str:
        """Format final client discovery report"""
        report = f"""
# Pregame Client Discovery Report: {solution.upper()}

**Target Market:** {solution} for {location} clients
**Clients Found:** {len(clients)}
**Research Date:** {asyncio.get_event_loop().time()}

## Executive Summary

Discovered {len(clients)} potential clients for {solution} in {location}.

## Client Discovery Results

"""
        
        for i, client in enumerate(clients, 1):
            report += f"""
**{i}. {client.get('name', 'Unknown Client')}**
- **Type:** {client.get('type', 'Not specified')}
- **Industry:** {client.get('industry', 'Not specified')}
- **Website:** {client.get('website', 'Research needed')}
- **Opportunity:** {client.get('opportunity', 'To be determined')}
- **Activity:** {client.get('activity', 'None identified')}
- **Location:** {client.get('location', location)}
- **Contact:** {client.get('contact', 'Research needed')}
- **Status:** {'Qualified' if client.get('qualified') else 'Initial Discovery'}

"""
        
        report += f"""
## Next Steps

1. **Prioritize clients** based on qualification scores and fit
2. **Develop contact strategy** for high-priority clients
3. **Create personalized outreach** materials
4. **Track engagement** and update client intelligence

## Discovery Insights

- **Total searches performed:** 5+ targeted discovery queries
- **Sources covered:** Crunchbase, LinkedIn, AngelList, business directories
- **Client types found:** Companies, individuals, entrepreneurs
- **Contact intelligence:** Varies by client (see individual entries)

*Generated by Pregame Client Discovery Engine*
"""
        
        return report

async def main():
    try:
        from langchain_deepresearch import DeepResearcher
        from langchain_openai import ChatOpenAI
        
        # Get client discovery parameters
        solution, location, client_type, count = get_client_discovery_input()
        
        print("Setting up APIs...")
        
        # Read environment variables
        env_vars = read_env_file()
        
        # Check for required API keys
        openai_key = env_vars.get('OPENAI_KEY')
        google_api_key = env_vars.get('GOOGLE_API_KEY', "AIzaSyAT4tQKRNt1rwrqrTs2GzlXuWi-BAYJWPA")
        google_cx = env_vars.get('GOOGLE_CX', "010381b2504d141f5")
        
        if not openai_key:
            print("❌ OpenAI API key not found in .env.local file")
            return
        
        print("✅ APIs configured!")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=openai_key,
            temperature=0.1
        )
        
        # Initialize DeepResearcher (without Firecrawl to avoid connection issues)
        researcher = DeepResearcher(
            llm=llm,
            google_api_key=google_api_key,
            google_cx=google_cx
        )
        
        # Initialize Client Discovery Engine
        client_discovery = PregameClientDiscovery(researcher)
        
        print(f"🚀 Starting client discovery for {solution} in {location}...")
        print("   This may take several minutes...")
        print("")
        
        # Run client discovery pipeline
        clients = await client_discovery.discover_clients(
            solution=solution,
            location=location,
            client_type=client_type,
            target_count=count
        )
        
        # Generate final report
        final_report = client_discovery.format_final_report(clients, solution, location)
        
        print("\n" + "="*60)
        print("🎯 PREGAME CLIENT DISCOVERY RESULTS")
        print("="*60)
        print(final_report)
        print("="*60)
        
        # Save results in multiple formats
        base_filename = f"pregame_clients_{solution.replace(' ', '_')}_{location.replace(' ', '_')}"
        
        # 1. Save clean text report (Windows compatible)
        txt_file = f"{base_filename}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            # Remove emojis for compatibility
            clean_report = re.sub(r'[^\x00-\x7F]+', '', final_report)
            f.write(clean_report)
        
        # 2. Save detailed JSON data with all research
        json_file = f"{base_filename}_detailed.json"
        detailed_data = {
            "search_criteria": {
                "solution": solution,
                "location": location,
                "client_type": client_type,
                "target_count": count
            },
            "discovery_summary": {
                "total_clients_found": len(clients),
                "qualified_clients": len([c for c in clients if c.get('qualified')]),
                "research_timestamp": asyncio.get_event_loop().time()
            },
            "clients": clients,
            "report": clean_report,
            "completion_status": "COMPLETED"
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        
        # 3. Save CSV for easy spreadsheet import
        csv_file = f"{base_filename}_contacts.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("Name,Type,Industry,Website,Opportunity,Activity,Location,Contact,Status,Qualified\n")
            for client in clients:
                name = client.get('name', '').replace(',', ';')
                client_type_val = client.get('type', '').replace(',', ';')
                industry = client.get('industry', '').replace(',', ';')
                website = client.get('website', '').replace(',', ';')
                opportunity = client.get('opportunity', '').replace(',', ';')
                activity = client.get('activity', '').replace(',', ';')
                location_val = client.get('location', '').replace(',', ';')
                contact = client.get('contact', '').replace(',', ';')
                status = 'Qualified' if client.get('qualified') else 'Discovery'
                qualified_status = 'Yes' if client.get('qualified') else 'No'
                
                f.write(f'"{name}","{client_type_val}","{industry}","{website}","{opportunity}","{activity}","{location_val}","{contact}","{status}","{qualified_status}"\n')
        
        # 4. Save markdown version (with emojis intact)
        md_file = f"{base_filename}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(final_report)  # Keep original formatting
        
        # 5. Save final live update with completion status
        live_file = f"{base_filename}_live.json"
        final_live_data = {
            "live_update": True,
            "status": "COMPLETED",
            "completion_time": asyncio.get_event_loop().time(),
            "final_results": {
                "total_clients": len(clients),
                "qualified_clients": len([c for c in clients if c.get('qualified')]),
                "files_created": [txt_file, json_file, csv_file, md_file]
            },
            "search_criteria": {
                "solution": solution,
                "location": location,
                "client_type": client_type,
                "target_count": count
            },
            "final_client_list": clients
        }
        
        with open(live_file, 'w', encoding='utf-8') as f:
            json.dump(final_live_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Files saved:")
        print(f"   📄 Text Report: {txt_file}")
        print(f"   📊 Detailed Data: {json_file}")
        print(f"   📈 CSV Contacts: {csv_file}")
        print(f"   📝 Markdown: {md_file}")
        print(f"   🔴 Live Updates: {live_file}")
        print(f"\n💡 Pro Tip: Watch {live_file} for real-time progress!")
        
        return clients
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure langchain-deepresearch and langchain-openai are installed")
        return None
    except KeyboardInterrupt:
        print("\n❌ Client discovery interrupted by user")
        return None
    except Exception as e:
        print(f"❌ Error during client discovery: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🎯 Pregame - Client Discovery Engine")
    print("Discover high-value clients for any solution...")
    print("="*60)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Happy client hunting!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()