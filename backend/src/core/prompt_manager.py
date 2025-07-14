"""
Intelligent prompt management for goal-based client discovery
"""

from typing import Dict, List

class PromptManager:
    """Manages prompts for intelligent, goal-based client discovery"""
    
    def __init__(self):
        pass
    
    def analyze_company_and_goal(self, company_data: Dict[str, str], goal: str) -> Dict[str, str]:
        """
        Generate analysis prompt to understand what prospects the user needs
        
        Args:
            company_data: User's company information
            goal: User's specific goal
            
        Returns:
            Dict[str, str]: Analysis prompts
        """
        return {
            "query_generation": f"""You are a business intelligence analyst. Analyze this company's profile and goal to determine the best prospect discovery strategy.

            COMPANY PROFILE:
            - Company: {company_data.get('company_name', 'Not provided')}
            - Industry: {company_data.get('industry', 'Not provided')}
            - Size: {company_data.get('company_size', 'Not provided')}
            - Stage: {company_data.get('stage', 'Not provided')}
            - What they do: {company_data.get('what_we_do', 'Not provided')}
            - Target customers: {company_data.get('target_customers', 'Not provided')}
            - Value proposition: {company_data.get('value_proposition', 'Not provided')}
            - Location: {company_data.get('location', 'Not provided')}
            - Budget range: {company_data.get('budget_range', 'Not provided')}

            GOAL: {goal}

            Based on this information, determine:
            1. What type of prospects they need (companies, individuals, investors, partners, etc.)
            2. What industry/sector to target
            3. What size/stage companies to focus on
            4. What specific pain points or needs to look for
            5. What search strategy would be most effective

            Generate search queries that would find these specific prospects.""",

            "report_generation": f"""You are analyzing a company's prospect needs. Based on the company profile and goal, provide a strategic analysis.

            COMPANY: {company_data.get('company_name', 'Not provided')}
            GOAL: {goal}

            Provide your analysis in this format:

            ## PROSPECT DISCOVERY ANALYSIS

            **Prospect Type:** [Type of prospects needed - companies, individuals, investors, etc.]
            **Target Industry:** [Which industries/sectors to focus on]
            **Company Size/Stage:** [What size/stage companies to target]
            **Geographic Focus:** [Where to search - local, national, global]
            **Key Criteria:** [What specific characteristics to look for]
            **Pain Points to Target:** [What problems/needs to focus on]
            **Search Strategy:** [How to approach the search]
            **Recommended Approach:** [Best way to reach these prospects]

            **Search Queries to Use:**
            1. [Specific search query 1]
            2. [Specific search query 2]
            3. [Specific search query 3]
            4. [Specific search query 4]
            5. [Specific search query 5]

            Focus on actionable insights that will help find the most relevant prospects for this specific goal."""
        }
    
    def get_intelligent_discovery_prompts(self, company_data: Dict[str, str], goal: str, analysis: Dict[str, str]) -> Dict[str, str]:
        """
        Generate intelligent discovery prompts based on analysis
        
        Args:
            company_data: User's company information
            goal: User's specific goal
            analysis: AI analysis results
            
        Returns:
            Dict[str, str]: Discovery prompts
        """
        prospect_type = analysis.get('prospect_type', 'companies')
        target_industry = analysis.get('target_industry', 'various')
        key_criteria = analysis.get('key_criteria', 'relevant businesses')
        
        return {
            "query_generation": f"""You are a prospect researcher for {company_data.get('company_name', 'this company')}. 
            Find SPECIFIC {prospect_type.upper()} that match their goal: {goal}

            COMPANY CONTEXT:
            - They do: {company_data.get('what_we_do', 'Not specified')}
            - Their target customers: {company_data.get('target_customers', 'Not specified')}
            - Their value proposition: {company_data.get('value_proposition', 'Not specified')}

            TARGET CRITERIA:
            - Prospect type: {prospect_type}
            - Target industry: {target_industry}
            - Key criteria: {key_criteria}

            Generate search queries that find ACTUAL {prospect_type}, not general information.

            Focus on finding:
            - Business directories and databases
            - Industry-specific listings
            - Recent news and announcements
            - Funding databases (if looking for funded companies)
            - Professional networks and associations
            - Job postings that reveal company needs
            - Social media and business profiles

            Example query patterns:
            - "site:crunchbase.com {target_industry} {company_data.get('location', 'US')}"
            - "site:linkedin.com/company {target_industry} hiring"
            - "{target_industry} companies {key_criteria}"
            - "recent funding {target_industry} {company_data.get('location', 'US')}"
            - "{prospect_type} {target_industry} news 2024"

            Avoid generic queries. Focus on finding specific, actionable prospects.""",

            "report_generation": f"""You are extracting PROSPECTS for: {goal}

            COMPANY CONTEXT: {company_data.get('company_name', 'User')} - {company_data.get('what_we_do', 'Not specified')}
            TARGET: {prospect_type} in {target_industry} that match: {key_criteria}

            For each prospect found, extract:
            - Name (person/company name)
            - Contact information (email, phone, LinkedIn, website)
            - Business description (what they do)
            - Why they're relevant to the goal: {goal}
            - Recent activities or signals
            - Location/headquarters
            - Size/stage (if applicable)
            - Specific pain points or needs mentioned
            - Budget/investment indicators (if relevant)

            Format as structured data:

            ## PROSPECTS FOUND: {goal.upper()}

            **1. [Prospect Name]**
            - Contact: [Email/Phone/LinkedIn/Website]
            - Business: [What they do in 1 sentence]
            - Relevance: [Why they match the goal]
            - Recent Signals: [Recent activities/news/posts]
            - Location: [City, State/Country]
            - Size/Stage: [If applicable]
            - Pain Points: [Specific challenges mentioned]
            - Budget Indicators: [If relevant]

            **2. [Next Prospect]**
            ...

            Focus on extracting ACTIONABLE PROSPECT DATA.
            Only include prospects that clearly match the goal: {goal}
            If no relevant prospects found, state "No matching prospects found" and suggest refined search terms."""
        }
    
    def get_intelligent_qualification_prompts(self, prospect_name: str, company_data: Dict[str, str], goal: str) -> Dict[str, str]:
        """
        Generate intelligent qualification prompts
        
        Args:
            prospect_name: Name of prospect to qualify
            company_data: User's company information
            goal: User's specific goal
            
        Returns:
            Dict[str, str]: Qualification prompts
        """
        return {
            "query_generation": f"""Research {prospect_name} for {company_data.get('company_name', 'this company')}'s goal: {goal}

            RESEARCH CONTEXT:
            - Company offering: {company_data.get('what_we_do', 'Not specified')}
            - Value proposition: {company_data.get('value_proposition', 'Not specified')}
            - Typical customers: {company_data.get('target_customers', 'Not specified')}
            - Goal: {goal}

            Find specific information about {prospect_name}:
            - Current business situation and challenges
            - Recent activities, announcements, or changes
            - Technology stack and current solutions (if relevant)
            - Team size, growth patterns, hiring
            - Budget indicators and investment patterns
            - Decision-making process and key contacts
            - Pain points that align with our value proposition
            - Timeline and urgency indicators
            - Competitive landscape and alternatives

            Search patterns:
            - "{prospect_name} challenges problems pain points"
            - "{prospect_name} recent news announcements funding"
            - "{prospect_name} team hiring growth expansion"
            - "site:linkedin.com/in {prospect_name} contact"
            - "{prospect_name} technology stack tools"
            - "{prospect_name} budget investment spending"
            - "{prospect_name} {company_data.get('industry', 'business')} opportunity"
            """,

            "report_generation": f"""Create INTELLIGENT QUALIFICATION for {prospect_name}.

            QUALIFICATION CONTEXT:
            - Our Company: {company_data.get('company_name', 'User')}
            - Our Offering: {company_data.get('what_we_do', 'Not specified')}
            - Our Goal: {goal}

            ## PROSPECT QUALIFICATION: {prospect_name}

            **Prospect Profile:**
            - Name and role/business type
            - Current business situation
            - Company size and growth stage
            - Industry and market position

            **Goal Alignment:**
            - How they relate to our goal: {goal}
            - Specific opportunities for our offering
            - Current pain points we could solve
            - Value proposition match score (1-10)

            **Qualification Signals:**
            - Recent activities and business changes
            - Budget and investment indicators
            - Growth signals and expansion plans
            - Technology adoption patterns
            - Decision-making timeline

            **Contact Intelligence:**
            - Best contact methods and information found
            - Decision-making authority and influence
            - Communication preferences and patterns
            - Mutual connections or warm intro opportunities

            **Approach Strategy:**
            - Recommended outreach method and timing
            - Key value propositions to emphasize
            - Conversation starters and talking points
            - Potential objections and how to address them

            **Opportunity Assessment:**
            - Likelihood of success (High/Medium/Low)
            - Potential deal size or value
            - Timeline to decision
            - Next steps and follow-up strategy

            **Risk Factors:**
            - Potential challenges or obstacles
            - Competitive threats
            - Budget or timing constraints

            Focus on actionable intelligence that enables immediate, relevant outreach aligned with the goal: {goal}"""
        }
    
    def generate_smart_search_queries(self, company_data: Dict[str, str], goal: str, analysis: Dict[str, str]) -> List[str]:
        """
        Generate smart search queries based on company data and goal analysis
        
        Args:
            company_data: User's company information
            goal: User's specific goal
            analysis: AI analysis results
            
        Returns:
            List[str]: List of optimized search queries
        """
        prospect_type = analysis.get('prospect_type', 'companies')
        target_industry = analysis.get('target_industry', 'business')
        location = company_data.get('location', 'US')
        
        # Base queries
        base_queries = [
            f"site:crunchbase.com {target_industry} {location}",
            f"site:linkedin.com/company {target_industry} {location}",
            f"{target_industry} {prospect_type} {location}",
            f"recent funding {target_industry} {location}",
            f"{target_industry} news 2024 {location}",
        ]
        
        # Goal-specific queries
        if "investor" in goal.lower():
            base_queries.extend([
                f"site:crunchbase.com investors {target_industry}",
                f"venture capital {target_industry}",
                f"angel investors {location}",
            ])
        elif "client" in goal.lower() or "customer" in goal.lower():
            base_queries.extend([
                f"{target_industry} companies need {company_data.get('value_proposition', 'services')}",
                f"site:linkedin.com/company {target_industry} hiring",
                f"{target_industry} challenges problems",
            ])
        elif "partner" in goal.lower():
            base_queries.extend([
                f"{target_industry} partnerships {location}",
                f"strategic partnerships {target_industry}",
                f"collaboration {target_industry}",
            ])
        
        return base_queries
    
    def get_goal_analysis_summary(self, analysis_result: str) -> Dict[str, str]:
        """
        Parse AI analysis result into structured data
        
        Args:
            analysis_result: Raw AI analysis response
            
        Returns:
            Dict[str, str]: Structured analysis data
        """
        # Simple parsing - in production, you'd use more sophisticated NLP
        lines = analysis_result.split('\n')
        analysis = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('**Prospect Type:**'):
                analysis['prospect_type'] = line.replace('**Prospect Type:**', '').strip()
            elif line.startswith('**Target Industry:**'):
                analysis['target_industry'] = line.replace('**Target Industry:**', '').strip()
            elif line.startswith('**Search Strategy:**'):
                analysis['search_strategy'] = line.replace('**Search Strategy:**', '').strip()
            elif line.startswith('**Key Criteria:**'):
                analysis['key_criteria'] = line.replace('**Key Criteria:**', '').strip()
        
        return analysis 