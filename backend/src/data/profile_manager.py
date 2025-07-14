"""
Profile Manager

High-level operations for managing prospect profiles and converting discovery results
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from .prospect_profile import ProspectProfile, ProspectType, RelevanceScore, ProspectStatus, ContactInfo, GoalAlignment, DiscoveryMetadata
from .profile_storage import ProfileStorage

class ProfileManager:
    """High-level profile management operations"""
    
    def __init__(self, storage_dir: str = "profiles"):
        """
        Initialize ProfileManager
        
        Args:
            storage_dir: Directory for profile storage
        """
        self.storage = ProfileStorage(storage_dir)
    
    def create_profile_from_discovery(self, prospect_data: Dict[str, Any], company_data: Dict[str, str], goal: str, discovery_session_id: str = None) -> ProspectProfile:
        """
        Create a ProspectProfile from discovery results
        
        Args:
            prospect_data: Raw prospect data from discovery
            company_data: User's company information
            goal: Discovery goal
            discovery_session_id: Optional session ID
            
        Returns:
            ProspectProfile: Created profile
        """
        # Create profile
        profile = ProspectProfile()
        
        # Core identity
        profile.name = prospect_data.get('name', 'Unknown Prospect')
        profile.prospect_type = self._determine_prospect_type(prospect_data, goal)
        
        # Business information
        profile.business_description = prospect_data.get('business', prospect_data.get('industry', ''))
        profile.industry = prospect_data.get('industry', '')
        profile.location = prospect_data.get('location', '')
        profile.company_size = prospect_data.get('size', '')
        profile.company_stage = prospect_data.get('stage', '')
        
        # Contact information
        profile.contact_info = self._extract_contact_info(prospect_data)
        
        # Goal alignment
        profile.goal_alignment = self._extract_goal_alignment(prospect_data)
        
        # Discovery metadata
        profile.discovery_metadata = DiscoveryMetadata(
            discovery_date=datetime.now(),
            source_query=prospect_data.get('source_query', ''),
            search_context=prospect_data.get('search_context', ''),
            company_goal=goal,
            discovering_company=company_data.get('company_name', ''),
            discovery_session_id=discovery_session_id or str(uuid.uuid4())
        )
        
        # Intelligence & insights
        profile.recent_activities = self._extract_activities(prospect_data)
        profile.pain_points = self._extract_pain_points(prospect_data)
        profile.buying_signals = self._extract_buying_signals(prospect_data)
        profile.budget_indicators = self._extract_budget_indicators(prospect_data)
        profile.decision_makers = self._extract_decision_makers(prospect_data)
        
        # Opportunity assessment
        profile.opportunity_description = prospect_data.get('opportunity', prospect_data.get('need', ''))
        profile.estimated_value = prospect_data.get('estimated_value', '')
        profile.timeline_indicators = prospect_data.get('timeline', '')
        
        # Initial tags
        profile.tags = self._generate_initial_tags(prospect_data, goal)
        
        return profile
    
    def _determine_prospect_type(self, prospect_data: Dict[str, Any], goal: str) -> ProspectType:
        """Determine prospect type based on data and goal"""
        # Check explicit type
        if 'type' in prospect_data:
            type_str = prospect_data['type'].lower()
            if 'company' in type_str:
                return ProspectType.COMPANY
            elif 'individual' in type_str:
                return ProspectType.INDIVIDUAL
            elif 'entrepreneur' in type_str:
                return ProspectType.ENTREPRENEUR
        
        # Infer from goal
        goal_lower = goal.lower()
        if 'investor' in goal_lower or 'funding' in goal_lower:
            return ProspectType.INVESTOR
        elif 'partner' in goal_lower or 'collaboration' in goal_lower:
            return ProspectType.PARTNER
        elif 'client' in goal_lower or 'customer' in goal_lower:
            return ProspectType.CLIENT
        
        # Default based on business description
        business = prospect_data.get('business', '').lower()
        if 'ceo' in business or 'founder' in business:
            return ProspectType.INDIVIDUAL
        elif 'company' in business or 'corporation' in business:
            return ProspectType.COMPANY
        
        return ProspectType.OTHER
    
    def _extract_contact_info(self, prospect_data: Dict[str, Any]) -> ContactInfo:
        """Extract contact information from prospect data"""
        contact = ContactInfo()
        
        # Extract from various fields
        contact_str = prospect_data.get('contact', prospect_data.get('contacts', ''))
        
        # Parse contact string for email, phone, etc.
        if '@' in contact_str:
            # Extract email
            import re
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_str)
            if email_match:
                contact.email = email_match.group()
        
        if 'linkedin.com' in contact_str:
            # Extract LinkedIn
            import re
            linkedin_match = re.search(r'linkedin\.com/[\w/]+', contact_str)
            if linkedin_match:
                contact.linkedin = f"https://{linkedin_match.group()}"
        
        if 'website' in prospect_data:
            contact.website = prospect_data['website']
        
        # Extract other contact info
        if 'phone' in prospect_data:
            contact.phone = prospect_data['phone']
        
        if 'twitter' in prospect_data:
            contact.twitter = prospect_data['twitter']
        
        return contact
    
    def _extract_goal_alignment(self, prospect_data: Dict[str, Any]) -> GoalAlignment:
        """Extract goal alignment from prospect data"""
        alignment = GoalAlignment()
        
        # Extract relevance score
        if 'goal_alignment' in prospect_data:
            goal_data = prospect_data['goal_alignment']
            if isinstance(goal_data, dict):
                relevance = goal_data.get('relevance_score', 'Medium')
                alignment.relevance_score = RelevanceScore(relevance)
                alignment.fit_reasons = goal_data.get('fit_reasons', [])
                alignment.potential_value = goal_data.get('potential_value', 'To be determined')
                alignment.approach_priority = goal_data.get('approach_priority', 'Medium')
        else:
            # Infer from need/opportunity
            need = prospect_data.get('need', prospect_data.get('opportunity', ''))
            if need:
                alignment.relevance_score = RelevanceScore.MEDIUM
                alignment.fit_reasons = [f"Need identified: {need}"]
        
        return alignment
    
    def _extract_activities(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extract recent activities"""
        activities = []
        
        # From various fields
        if 'activity' in prospect_data:
            activities.append(prospect_data['activity'])
        
        if 'signals' in prospect_data:
            activities.append(prospect_data['signals'])
        
        if 'recent_activity' in prospect_data:
            activities.append(prospect_data['recent_activity'])
        
        return [a for a in activities if a and a.strip()]
    
    def _extract_pain_points(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extract pain points"""
        pain_points = []
        
        # From various fields
        if 'pain_points' in prospect_data:
            if isinstance(prospect_data['pain_points'], list):
                pain_points.extend(prospect_data['pain_points'])
            else:
                pain_points.append(prospect_data['pain_points'])
        
        if 'need' in prospect_data:
            pain_points.append(prospect_data['need'])
        
        if 'challenge' in prospect_data:
            pain_points.append(prospect_data['challenge'])
        
        return [p for p in pain_points if p and p.strip()]
    
    def _extract_buying_signals(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extract buying signals"""
        signals = []
        
        # From various fields
        if 'buying_signals' in prospect_data:
            if isinstance(prospect_data['buying_signals'], list):
                signals.extend(prospect_data['buying_signals'])
            else:
                signals.append(prospect_data['buying_signals'])
        
        if 'signals' in prospect_data:
            signals.append(prospect_data['signals'])
        
        # Check for funding/growth signals
        activity = prospect_data.get('activity', '').lower()
        if 'funding' in activity or 'raised' in activity or 'investment' in activity:
            signals.append('Recent funding activity')
        
        if 'hiring' in activity or 'growth' in activity:
            signals.append('Growth indicators')
        
        return [s for s in signals if s and s.strip()]
    
    def _extract_budget_indicators(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extract budget indicators"""
        indicators = []
        
        # From various fields
        if 'budget' in prospect_data:
            indicators.append(prospect_data['budget'])
        
        if 'budget_indicators' in prospect_data:
            if isinstance(prospect_data['budget_indicators'], list):
                indicators.extend(prospect_data['budget_indicators'])
            else:
                indicators.append(prospect_data['budget_indicators'])
        
        # Check for funding/size indicators
        size = prospect_data.get('size', '').lower()
        if 'funded' in size or 'series' in size:
            indicators.append(f'Company size: {size}')
        
        return [i for i in indicators if i and i.strip()]
    
    def _extract_decision_makers(self, prospect_data: Dict[str, Any]) -> List[str]:
        """Extract decision makers"""
        decision_makers = []
        
        # From various fields
        if 'decision_makers' in prospect_data:
            if isinstance(prospect_data['decision_makers'], list):
                decision_makers.extend(prospect_data['decision_makers'])
            else:
                decision_makers.append(prospect_data['decision_makers'])
        
        # Check if prospect is a decision maker
        name = prospect_data.get('name', '').lower()
        if 'ceo' in name or 'founder' in name or 'president' in name or 'director' in name:
            decision_makers.append(prospect_data.get('name', ''))
        
        return [d for d in decision_makers if d and d.strip()]
    
    def _generate_initial_tags(self, prospect_data: Dict[str, Any], goal: str) -> List[str]:
        """Generate initial tags for prospect"""
        tags = []
        
        # Add goal-based tag
        tags.append(f"goal:{goal.lower().replace(' ', '_')}")
        
        # Add type-based tags
        if 'type' in prospect_data:
            tags.append(f"type:{prospect_data['type'].lower()}")
        
        # Add industry tag
        if 'industry' in prospect_data:
            tags.append(f"industry:{prospect_data['industry'].lower().replace(' ', '_')}")
        
        # Add location tag
        if 'location' in prospect_data:
            tags.append(f"location:{prospect_data['location'].lower().replace(' ', '_')}")
        
        # Add discovery date
        tags.append(f"discovered:{datetime.now().strftime('%Y-%m')}")
        
        return tags
    
    def save_prospects_from_discovery(self, prospects: List[Dict[str, Any]], company_data: Dict[str, str], goal: str, discovery_session_id: str = None) -> List[str]:
        """
        Save multiple prospects from discovery results
        
        Args:
            prospects: List of prospect dictionaries from discovery
            company_data: User's company information
            goal: Discovery goal
            discovery_session_id: Optional session ID
            
        Returns:
            List[str]: List of saved profile IDs
        """
        session_id = discovery_session_id or str(uuid.uuid4())
        saved_profiles = []
        
        for prospect_data in prospects:
            try:
                # Create profile from discovery data
                profile = self.create_profile_from_discovery(
                    prospect_data, 
                    company_data, 
                    goal, 
                    session_id
                )
                
                # Save profile
                if self.storage.save_profile(profile):
                    saved_profiles.append(profile.profile_id)
                    print(f"✅ Saved profile: {profile.name}")
                else:
                    print(f"❌ Failed to save profile: {profile.name}")
                    
            except Exception as e:
                print(f"❌ Error saving prospect {prospect_data.get('name', 'Unknown')}: {e}")
                continue
        
        return saved_profiles
    
    def get_profile(self, profile_id: str) -> Optional[ProspectProfile]:
        """Get profile by ID"""
        return self.storage.load_profile(profile_id)
    
    def search_profiles(self, **filters) -> List[ProspectProfile]:
        """Search profiles and return full profile objects"""
        profile_ids = self.storage.search_profiles(**filters)
        profiles = []
        
        for profile_id in profile_ids:
            profile = self.storage.load_profile(profile_id)
            if profile:
                profiles.append(profile)
        
        return profiles
    
    def update_profile(self, profile: ProspectProfile) -> bool:
        """Update existing profile"""
        profile.updated_at = datetime.now()
        profile.version += 1
        return self.storage.save_profile(profile)
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete profile"""
        return self.storage.delete_profile(profile_id)
    
    def get_profiles_for_company(self, company_name: str) -> List[ProspectProfile]:
        """Get all profiles for a specific company"""
        return self.search_profiles(company=company_name)
    
    def get_profiles_for_goal(self, goal: str) -> List[ProspectProfile]:
        """Get all profiles for a specific goal"""
        return self.search_profiles(goal=goal)
    
    def get_high_relevance_profiles(self) -> List[ProspectProfile]:
        """Get all high-relevance profiles"""
        return self.search_profiles(relevance="High")
    
    def add_interaction(self, profile_id: str, interaction_type: str, content: str, outcome: str = "") -> bool:
        """Add interaction to profile"""
        profile = self.storage.load_profile(profile_id)
        if not profile:
            return False
        
        profile.add_interaction(interaction_type, content, outcome)
        return self.storage.save_profile(profile)
    
    def add_note(self, profile_id: str, note: str, category: str = "general") -> bool:
        """Add note to profile"""
        profile = self.storage.load_profile(profile_id)
        if not profile:
            return False
        
        profile.add_note(note, category)
        return self.storage.save_profile(profile)
    
    def update_status(self, profile_id: str, new_status: ProspectStatus) -> bool:
        """Update profile status"""
        profile = self.storage.load_profile(profile_id)
        if not profile:
            return False
        
        profile.update_status(new_status)
        return self.storage.save_profile(profile)
    
    def add_tag(self, profile_id: str, tag: str) -> bool:
        """Add tag to profile"""
        profile = self.storage.load_profile(profile_id)
        if not profile:
            return False
        
        profile.add_tag(tag)
        return self.storage.save_profile(profile)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get profile statistics"""
        return self.storage.get_stats()
    
    def backup_profiles(self, backup_dir: str = "backups") -> bool:
        """Create backup of all profiles"""
        return self.storage.backup_profiles(backup_dir)
    
    def list_profiles(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """List profiles with pagination"""
        return self.storage.list_profiles(limit, offset)
    
    def get_profile_summary(self, profile_id: str) -> Optional[str]:
        """Get brief profile summary"""
        profile = self.storage.load_profile(profile_id)
        if profile:
            return profile.get_summary()
        return None
    
    def export_profiles_to_csv(self, filename: str = "profiles_export.csv") -> bool:
        """Export profiles to CSV"""
        try:
            import csv
            from pathlib import Path
            
            profiles = self.search_profiles()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'profile_id', 'name', 'prospect_type', 'business_description',
                    'industry', 'location', 'company_size', 'status', 'relevance_score',
                    'email', 'phone', 'linkedin', 'website', 'company_goal',
                    'discovering_company', 'created_at', 'updated_at'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for profile in profiles:
                    writer.writerow({
                        'profile_id': profile.profile_id,
                        'name': profile.name,
                        'prospect_type': profile.prospect_type.value,
                        'business_description': profile.business_description,
                        'industry': profile.industry,
                        'location': profile.location,
                        'company_size': profile.company_size,
                        'status': profile.status.value,
                        'relevance_score': profile.goal_alignment.relevance_score.value,
                        'email': profile.contact_info.email or '',
                        'phone': profile.contact_info.phone or '',
                        'linkedin': profile.contact_info.linkedin or '',
                        'website': profile.contact_info.website or '',
                        'company_goal': profile.discovery_metadata.company_goal,
                        'discovering_company': profile.discovery_metadata.discovering_company,
                        'created_at': profile.created_at.isoformat(),
                        'updated_at': profile.updated_at.isoformat()
                    })
            
            print(f"✅ Profiles exported to: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False 