"""
Prospect Profile Data Model

Defines the structure for storing prospect profiles discovered through the intelligent discovery system
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

class ProspectType(Enum):
    """Types of prospects"""
    COMPANY = "company"
    INDIVIDUAL = "individual"
    ENTREPRENEUR = "entrepreneur"
    INVESTOR = "investor"
    PARTNER = "partner"
    CLIENT = "client"
    OTHER = "other"

class RelevanceScore(Enum):
    """Relevance scoring for prospect-goal alignment"""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    UNSCORED = "Unscored"

class ProspectStatus(Enum):
    """Prospect engagement status"""
    DISCOVERED = "discovered"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    CONVERTED = "converted"
    REJECTED = "rejected"
    ARCHIVED = "archived"

@dataclass
class ContactInfo:
    """Contact information structure"""
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    website: Optional[str] = None
    twitter: Optional[str] = None
    other: Dict[str, str] = field(default_factory=dict)

@dataclass
class GoalAlignment:
    """Goal alignment assessment"""
    relevance_score: RelevanceScore = RelevanceScore.UNSCORED
    fit_reasons: List[str] = field(default_factory=list)
    potential_value: str = "To be determined"
    approach_priority: str = "Medium"
    alignment_notes: str = ""

@dataclass
class DiscoveryMetadata:
    """Discovery session metadata"""
    discovery_date: datetime = field(default_factory=datetime.now)
    source_query: str = ""
    search_context: str = ""
    company_goal: str = ""
    discovering_company: str = ""
    discovery_session_id: str = ""

@dataclass
class ProspectProfile:
    """Complete prospect profile"""
    
    # Core Identity
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    prospect_type: ProspectType = ProspectType.OTHER
    
    # Business Information
    business_description: str = ""
    industry: str = ""
    location: str = ""
    company_size: str = ""
    company_stage: str = ""
    
    # Contact Information
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    
    # Goal Alignment
    goal_alignment: GoalAlignment = field(default_factory=GoalAlignment)
    
    # Discovery Context
    discovery_metadata: DiscoveryMetadata = field(default_factory=DiscoveryMetadata)
    
    # Intelligence & Insights
    recent_activities: List[str] = field(default_factory=list)
    pain_points: List[str] = field(default_factory=list)
    buying_signals: List[str] = field(default_factory=list)
    budget_indicators: List[str] = field(default_factory=list)
    decision_makers: List[str] = field(default_factory=list)
    
    # Engagement Tracking
    status: ProspectStatus = ProspectStatus.DISCOVERED
    interactions: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Opportunity Assessment
    opportunity_description: str = ""
    estimated_value: str = ""
    timeline_indicators: str = ""
    competitor_analysis: str = ""
    
    # System Fields
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for JSON serialization"""
        return {
            'profile_id': self.profile_id,
            'name': self.name,
            'prospect_type': self.prospect_type.value,
            'business_description': self.business_description,
            'industry': self.industry,
            'location': self.location,
            'company_size': self.company_size,
            'company_stage': self.company_stage,
            'contact_info': {
                'email': self.contact_info.email,
                'phone': self.contact_info.phone,
                'linkedin': self.contact_info.linkedin,
                'website': self.contact_info.website,
                'twitter': self.contact_info.twitter,
                'other': self.contact_info.other
            },
            'goal_alignment': {
                'relevance_score': self.goal_alignment.relevance_score.value,
                'fit_reasons': self.goal_alignment.fit_reasons,
                'potential_value': self.goal_alignment.potential_value,
                'approach_priority': self.goal_alignment.approach_priority,
                'alignment_notes': self.goal_alignment.alignment_notes
            },
            'discovery_metadata': {
                'discovery_date': self.discovery_metadata.discovery_date.isoformat(),
                'source_query': self.discovery_metadata.source_query,
                'search_context': self.discovery_metadata.search_context,
                'company_goal': self.discovery_metadata.company_goal,
                'discovering_company': self.discovery_metadata.discovering_company,
                'discovery_session_id': self.discovery_metadata.discovery_session_id
            },
            'recent_activities': self.recent_activities,
            'pain_points': self.pain_points,
            'buying_signals': self.buying_signals,
            'budget_indicators': self.budget_indicators,
            'decision_makers': self.decision_makers,
            'status': self.status.value,
            'interactions': self.interactions,
            'notes': self.notes,
            'tags': self.tags,
            'opportunity_description': self.opportunity_description,
            'estimated_value': self.estimated_value,
            'timeline_indicators': self.timeline_indicators,
            'competitor_analysis': self.competitor_analysis,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProspectProfile':
        """Create profile from dictionary"""
        profile = cls()
        
        # Core fields
        profile.profile_id = data.get('profile_id', str(uuid.uuid4()))
        profile.name = data.get('name', '')
        profile.prospect_type = ProspectType(data.get('prospect_type', 'other'))
        profile.business_description = data.get('business_description', '')
        profile.industry = data.get('industry', '')
        profile.location = data.get('location', '')
        profile.company_size = data.get('company_size', '')
        profile.company_stage = data.get('company_stage', '')
        
        # Contact info
        contact_data = data.get('contact_info', {})
        profile.contact_info = ContactInfo(
            email=contact_data.get('email'),
            phone=contact_data.get('phone'),
            linkedin=contact_data.get('linkedin'),
            website=contact_data.get('website'),
            twitter=contact_data.get('twitter'),
            other=contact_data.get('other', {})
        )
        
        # Goal alignment
        goal_data = data.get('goal_alignment', {})
        profile.goal_alignment = GoalAlignment(
            relevance_score=RelevanceScore(goal_data.get('relevance_score', 'Unscored')),
            fit_reasons=goal_data.get('fit_reasons', []),
            potential_value=goal_data.get('potential_value', 'To be determined'),
            approach_priority=goal_data.get('approach_priority', 'Medium'),
            alignment_notes=goal_data.get('alignment_notes', '')
        )
        
        # Discovery metadata
        discovery_data = data.get('discovery_metadata', {})
        profile.discovery_metadata = DiscoveryMetadata(
            discovery_date=datetime.fromisoformat(discovery_data.get('discovery_date', datetime.now().isoformat())),
            source_query=discovery_data.get('source_query', ''),
            search_context=discovery_data.get('search_context', ''),
            company_goal=discovery_data.get('company_goal', ''),
            discovering_company=discovery_data.get('discovering_company', ''),
            discovery_session_id=discovery_data.get('discovery_session_id', '')
        )
        
        # Lists
        profile.recent_activities = data.get('recent_activities', [])
        profile.pain_points = data.get('pain_points', [])
        profile.buying_signals = data.get('buying_signals', [])
        profile.budget_indicators = data.get('budget_indicators', [])
        profile.decision_makers = data.get('decision_makers', [])
        profile.interactions = data.get('interactions', [])
        profile.notes = data.get('notes', [])
        profile.tags = data.get('tags', [])
        
        # Status and assessment
        profile.status = ProspectStatus(data.get('status', 'discovered'))
        profile.opportunity_description = data.get('opportunity_description', '')
        profile.estimated_value = data.get('estimated_value', '')
        profile.timeline_indicators = data.get('timeline_indicators', '')
        profile.competitor_analysis = data.get('competitor_analysis', '')
        
        # System fields
        profile.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        profile.updated_at = datetime.fromisoformat(data.get('updated_at', datetime.now().isoformat()))
        profile.version = data.get('version', 1)
        
        return profile
    
    def add_interaction(self, interaction_type: str, content: str, outcome: str = ""):
        """Add interaction record"""
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'content': content,
            'outcome': outcome,
            'user': 'system'
        }
        self.interactions.append(interaction)
        self.updated_at = datetime.now()
        self.version += 1
    
    def add_note(self, note: str, category: str = "general"):
        """Add note to prospect"""
        note_entry = {
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'content': note,
            'user': 'system'
        }
        self.notes.append(note_entry)
        self.updated_at = datetime.now()
        self.version += 1
    
    def update_status(self, new_status: ProspectStatus):
        """Update prospect status"""
        self.status = new_status
        self.updated_at = datetime.now()
        self.version += 1
    
    def add_tag(self, tag: str):
        """Add tag to prospect"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
            self.version += 1
    
    def get_summary(self) -> str:
        """Get brief summary of prospect"""
        return f"{self.name} ({self.prospect_type.value}) - {self.goal_alignment.relevance_score.value} relevance - {self.status.value}" 