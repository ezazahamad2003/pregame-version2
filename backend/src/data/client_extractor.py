"""
Client data extraction and processing utilities
"""

import re
from typing import Dict, List, Any

class ClientExtractor:
    """Handles extraction and processing of client data from research results"""
    
    def __init__(self):
        self.client_patterns = {
            'name': [r'\*\*(.*?)\*\*', r'## (.*?)(?:\n|$)', r'# (.*?)(?:\n|$)'],
            'contact': [r'contact[:\s]+(.*?)(?:\n|$)', r'email[:\s]+(.*?)(?:\n|$)', r'phone[:\s]+(.*?)(?:\n|$)'],
            'website': [r'website[:\s]+(.*?)(?:\n|$)', r'site[:\s]+(.*?)(?:\n|$)', r'https?://[^\s]+'],
            'business': [r'business[:\s]+(.*?)(?:\n|$)', r'company[:\s]+(.*?)(?:\n|$)', r'does[:\s]+(.*?)(?:\n|$)'],
            'need': [r'need[:\s]+(.*?)(?:\n|$)', r'pain[:\s]+(.*?)(?:\n|$)', r'problem[:\s]+(.*?)(?:\n|$)'],
            'signals': [r'signals[:\s]+(.*?)(?:\n|$)', r'recent[:\s]+(.*?)(?:\n|$)', r'funding[:\s]+(.*?)(?:\n|$)'],
            'location': [r'location[:\s]+(.*?)(?:\n|$)', r'based[:\s]+(.*?)(?:\n|$)', r'headquarters[:\s]+(.*?)(?:\n|$)'],
            'founded': [r'founded[:\s]+(.*?)(?:\n|$)', r'established[:\s]+(.*?)(?:\n|$)', r'started[:\s]+(.*?)(?:\n|$)']
        }
    
    def extract_clients_from_result(self, result: Dict) -> List[Dict]:
        """
        Extract client data from research result
        
        Args:
            result: Research result dictionary
            
        Returns:
            List[Dict]: List of extracted client data
        """
        clients = []
        
        # Debug logging
        print(f"🔍 ClientExtractor: Processing result type: {type(result)}")
        
        if isinstance(result, dict) and 'report' in result:
            report = result['report']
            print(f"🔍 ClientExtractor: Report length: {len(str(report)) if report else 0}")
            print(f"🔍 ClientExtractor: Report preview: {str(report)[:300]}...")
            
            clients = self._parse_structured_report(report)
            print(f"🔍 ClientExtractor: Parsed {len(clients)} clients from report")
        else:
            print(f"🔍 ClientExtractor: No 'report' key in result or result is not dict")
            if isinstance(result, dict):
                print(f"🔍 ClientExtractor: Available keys: {list(result.keys())}")
        
        return clients
    
    def _parse_structured_report(self, report: str) -> List[Dict]:
        """Parse structured report format for client data"""
        clients = []
        lines = report.split('\n')
        current_client = {}
        
        print(f"🔍 Parsing report with {len(lines)} lines")
        
        # Count potential client headers
        header_lines = [line for line in lines if line.strip().startswith('**') and line.strip().endswith('**')]
        print(f"🔍 Found {len(header_lines)} potential client headers")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Look for client headers (markdown format)
            if line.startswith('**') and line.endswith('**'):
                # Save previous client if exists
                if current_client and current_client.get('name'):
                    clients.append(current_client.copy())
                    print(f"🔍 Added client: {current_client.get('name')}")
                
                # Start new client
                client_name = line.strip('*').strip()
                print(f"🔍 Processing potential client header: '{client_name}'")
                
                if client_name and not client_name.isupper():  # Skip headers
                    current_client = {'name': client_name}
                    print(f"🔍 Started new client: {client_name}")
                else:
                    print(f"🔍 Skipping header (uppercase or empty): {client_name}")
            
            # Extract data fields
            elif current_client and ':' in line:
                print(f"🔍 Processing data line for {current_client.get('name', 'unnamed')}: {line}")
                self._extract_field_from_line(line, current_client)
        
        # Don't forget the last client
        if current_client and current_client.get('name'):
            clients.append(current_client)
            print(f"🔍 Added final client: {current_client.get('name')}")
        
        print(f"🔍 Total clients parsed: {len(clients)}")
        return clients
    
    def _extract_field_from_line(self, line: str, client: Dict):
        """Extract field data from a line"""
        line_lower = line.lower()
        
        # Map common field patterns
        field_mappings = {
            'website': ['website', 'site', 'url'],
            'business': ['business', 'company', 'does', 'description'],
            'need': ['need', 'pain', 'problem', 'challenge'],
            'signals': ['signals', 'recent', 'news', 'funding'],
            'location': ['location', 'based', 'headquarters', 'hq'],
            'founded': ['founded', 'established', 'started'],
            'contacts': ['contacts', 'contact', 'email', 'phone']
        }
        
        for field, keywords in field_mappings.items():
            for keyword in keywords:
                if keyword in line_lower:
                    value = self._extract_value_after_colon(line)
                    if value:
                        client[field] = value
                    break
    
    def _extract_value_after_colon(self, line: str) -> str:
        """Extract value after colon in a line"""
        if ':' in line:
            parts = line.split(':', 1)
            if len(parts) > 1:
                return parts[1].strip().lstrip('- ').strip()
        return ""
    
    def deduplicate_clients(self, clients: List[Dict]) -> List[Dict]:
        """
        Remove duplicate clients based on name similarity
        
        Args:
            clients: List of client dictionaries
            
        Returns:
            List[Dict]: Deduplicated list of clients
        """
        seen_names = set()
        unique_clients = []
        
        for client in clients:
            name = client.get('name', '').lower().strip()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_clients.append(client)
        
        return unique_clients
    
    def enrich_client_data(self, client: Dict, qualification_result: Dict) -> Dict:
        """
        Enrich client data with qualification research results
        
        Args:
            client: Original client data
            qualification_result: Deep research results
            
        Returns:
            Dict: Enhanced client data
        """
        enhanced_client = client.copy()
        enhanced_client['qualification_research'] = qualification_result
        enhanced_client['qualified'] = True
        
        # Extract additional insights from qualification
        if isinstance(qualification_result, dict) and 'report' in qualification_result:
            report = qualification_result['report']
            enhanced_client['insights'] = self._extract_insights_from_report(report)
        
        return enhanced_client
    
    def _extract_insights_from_report(self, report: str) -> Dict:
        """Extract key insights from qualification report"""
        insights = {}
        
        # Extract key sections
        sections = {
            'company_overview': ['company overview', 'about', 'description'],
            'opportunity': ['opportunity', 'use case', 'potential'],
            'sales_signals': ['sales signals', 'signals', 'recent'],
            'contact_strategy': ['contact strategy', 'approach', 'outreach'],
            'next_steps': ['next steps', 'recommendations', 'action']
        }
        
        report_lower = report.lower()
        for section, keywords in sections.items():
            for keyword in keywords:
                if keyword in report_lower:
                    # Extract content after the keyword
                    start_idx = report_lower.find(keyword)
                    if start_idx != -1:
                        # Get the section content (approximate)
                        section_text = report[start_idx:start_idx + 500]
                        insights[section] = section_text[:200] + "..." if len(section_text) > 200 else section_text
                        break
        
        return insights 