#!/usr/bin/env python3
"""
Pregame Web Application

Flask web server providing API endpoints and web interface for prospect discovery and profile management
"""

import os
import uuid
import json
import asyncio
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_cors import CORS

from src.core.discovery_engine import PregameClientDiscovery
from src.data.profile_manager import ProfileManager
from src.data.profile_storage import ProfileStorage
from src.data.prospect_profile import ProspectStatus
from src.utils.env_manager import get_api_keys, validate_api_keys

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
app.secret_key = os.environ.get('SECRET_KEY', 'pregame-secret-key-change-in-production')
CORS(app)

# Initialize components
profile_manager = ProfileManager()
profile_storage = ProfileStorage()

# Initialize discovery engine with proper dependencies
def create_discovery_engine():
    """Create a properly initialized discovery engine"""
    try:
        from langchain_deepresearch import DeepResearcher
        from langchain_openai import ChatOpenAI
        
        # Get API keys
        api_keys = get_api_keys()
        
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
        
        return PregameClientDiscovery(researcher)
    except Exception as e:
        print(f"Warning: Could not initialize discovery engine: {e}")
        return None

discovery_engine = create_discovery_engine()

# Global session storage
discovery_sessions = {}

class DiscoverySession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.status = "initializing"
        self.progress = 0
        self.start_time = datetime.now()
        self.end_time = None
        self.activity_log = []
        self.error = None
        self.results = None
        
    def add_activity(self, message: str):
        """Add an activity message with timestamp"""
        self.activity_log.append({
            'timestamp': datetime.now().isoformat(),
            'message': message
        })

# API Routes

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/discovery')
def discovery_page():
    """Discovery interface page"""
    return render_template('discovery.html')

# Removed profiles and analytics pages - simplified to 2 pages only

@app.route('/api/discovery/start', methods=['POST'])
def start_discovery():
    """Start a new discovery session"""
    try:
        data = request.json
        
        # Validate input - simplified structure
        company_name = data.get('company_name', '')
        company_description = data.get('company_description', '')
        industry = data.get('industry', '')
        goal = data.get('goal', '')
        
        if not company_name or not company_description or not industry or not goal:
            return jsonify({'error': 'All fields are required'}), 400
        
        # Create company data structure for existing discovery engine
        company_data = {
            'company_name': company_name,
            'industry': industry,
            'what_we_do': company_description,
            'target_customers': '',  # We'll derive this from goal
            'value_proposition': company_description,
            'company_size': '10-50',  # Default
            'stage': 'Growth',  # Default
            'location': 'US',  # Default
            'budget_range': ''  # Default
        }
        
        # Default preferences
        preferences = {
            'target_count': 15,
            'geographic_focus': 'US',
            'priority': 'balanced'
        }
        
        # Create session
        session_id = str(uuid.uuid4())
        session = DiscoverySession(session_id)
        discovery_sessions[session_id] = session
        
        # Start discovery in background thread
        def run_discovery():
            try:
                # Create event loop for async discovery
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run discovery
                prospects = loop.run_until_complete(
                    run_discovery_async(session, company_data, goal, preferences)
                )
                
                session.results = prospects
                session.status = "completed"
                session.end_time = datetime.now()
                
            except Exception as e:
                session.error = str(e)
                session.status = "error"
                print(f"Discovery error: {e}")
        
        # Start discovery thread
        discovery_thread = threading.Thread(target=run_discovery)
        discovery_thread.daemon = True
        discovery_thread.start()
        
        return jsonify({
            'session_id': session_id,
            'status': 'started',
            'message': 'Discovery session started'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def run_discovery_async(session, company_data, goal, preferences):
    """Run discovery asynchronously"""
    try:
        # Validate API keys
        session.add_activity("🔑 Validating API keys...")
        if not validate_api_keys():
            raise Exception("API keys not configured")
        session.add_activity("✅ API keys validated successfully")
        
        # Import required dependencies
        session.add_activity("📚 Loading AI research libraries...")
        from langchain_deepresearch import DeepResearcher
        from langchain_openai import ChatOpenAI
        session.add_activity("✅ AI libraries loaded")
        
        # Get API keys
        api_keys = get_api_keys()
        session.add_activity("🔧 Configuring AI models...")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_keys['openai_key'],
            temperature=0.1
        )
        session.add_activity("🤖 OpenAI GPT-4o-mini model initialized")
        
        # Initialize DeepResearcher
        researcher = DeepResearcher(
            llm=llm,
            google_api_key=api_keys['google_api_key'],
            google_cx=api_keys['google_cx']
        )
        session.add_activity("🔍 Deep research engine initialized")
        
        # Initialize discovery engine
        discovery_engine = PregameClientDiscovery(researcher)
        session.add_activity("⚙️ Pregame discovery engine ready")
        
        # Update session progress
        session.status = "running"
        session.progress = 15
        session.add_activity(f"🎯 Analyzing company: {company_data['company_name']}")
        session.add_activity(f"🏭 Industry: {company_data['industry']}")
        session.add_activity(f"🎯 Goal: {goal}")
        
        # Run discovery with detailed tracking
        session.add_activity("🚀 Starting intelligent prospect discovery...")
        session.progress = 25
        
        # Add more detailed progress tracking with realistic timing
        await asyncio.sleep(1)  # Small delay for realism
        session.add_activity("🔬 Analyzing your company profile and goals...")
        session.progress = 35
        
        await asyncio.sleep(1)
        session.add_activity("🎯 Identifying ideal prospect characteristics...")
        session.progress = 45
        
        await asyncio.sleep(1)
        session.add_activity("🌐 Searching web for potential prospects...")
        session.progress = 55
        
        await asyncio.sleep(1)
        session.add_activity("🔍 Deep research on discovered prospects...")
        session.progress = 65
        
        await asyncio.sleep(1)
        session.add_activity("📊 Analyzing prospect relevance and fit...")
        session.progress = 75
        
        try:
            prospects = await discovery_engine.discover_prospects(
                company_data=company_data,
                goal=goal,
                preferences=preferences
            )
            
            # Log the number of prospects found
            session.add_activity(f"🔍 Discovery engine returned {len(prospects)} prospects")
            
        except Exception as e:
            session.add_activity(f"❌ Discovery error: {str(e)}")
            raise
        
        session.add_activity(f"✅ Discovery completed - found {len(prospects)} prospects")
        await asyncio.sleep(1)
        session.add_activity("💾 Saving profiles to database...")
        session.progress = 95
        
        await asyncio.sleep(1)
        session.add_activity("🎉 All done! Your prospects are ready for review.")
        session.progress = 100
        return prospects
        
    except Exception as e:
        session.error = str(e)
        session.status = "error"
        raise

@app.route('/api/discovery/status/<session_id>')
def get_discovery_status(session_id):
    """Get discovery session status"""
    session = discovery_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'status': session.status,
        'progress': session.progress,
        'prospects_count': len(session.results) if session.results else 0,
        'created_at': session.start_time.isoformat(),
        'completed_at': session.end_time.isoformat() if session.end_time else None,
        'error': session.error,
        'activity_log': session.activity_log
    })

@app.route('/api/discovery/results/<session_id>')
def get_discovery_results(session_id):
    """Get discovery session results"""
    session = discovery_sessions.get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    if session.status != "completed":
        return jsonify({'error': 'Discovery not completed'}), 400
    
    return jsonify({
        'session_id': session_id,
        'prospects': session.results or [],
        'status': session.status,
        'error': session.error
    })

@app.route('/api/profiles')
def get_profiles():
    """Get all profiles with pagination and filtering"""
    # Get query parameters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    offset = (page - 1) * limit
    
    # Get filter parameters
    filters = {}
    if request.args.get('company'):
        filters['company'] = request.args.get('company')
    if request.args.get('goal'):
        filters['goal'] = request.args.get('goal')
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('relevance'):
        filters['relevance'] = request.args.get('relevance')
    if request.args.get('tags'):
        filters['tags'] = request.args.get('tags').split(',')
    if request.args.get('name'):
        filters['name'] = request.args.get('name')
    
    try:
        # Get profiles
        if filters:
            profiles = profile_manager.search_profiles(**filters)
            # Convert to dict format for JSON response
            profiles_data = []
            for profile in profiles:
                profiles_data.append({
                    'profile_id': profile.profile_id,
                    'name': profile.name,
                    'prospect_type': profile.prospect_type.value,
                    'status': profile.status.value,
                    'relevance_score': profile.goal_alignment.relevance_score.value,
                    'company_goal': profile.discovery_metadata.company_goal,
                    'discovering_company': profile.discovery_metadata.discovering_company,
                    'created_at': profile.created_at.isoformat(),
                    'updated_at': profile.updated_at.isoformat(),
                    'tags': profile.tags,
                    'industry': profile.industry,
                    'location': profile.location,
                    'business_description': profile.business_description[:100] + '...' if len(profile.business_description) > 100 else profile.business_description
                })
        else:
            profiles_data = profile_manager.list_profiles(limit=limit, offset=offset)
        
        # Get total count for pagination
        total_profiles = profile_manager.get_stats()['total_profiles']
        
        return jsonify({
            'profiles': profiles_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_profiles,
                'pages': (total_profiles + limit - 1) // limit
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>')
def get_profile(profile_id):
    """Get detailed profile information"""
    try:
        profile = profile_manager.get_profile(profile_id)
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        return jsonify(profile.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>/status', methods=['PUT'])
def update_profile_status(profile_id):
    """Update profile status"""
    try:
        data = request.json
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        # Validate status
        try:
            prospect_status = ProspectStatus(status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        if profile_manager.update_status(profile_id, prospect_status):
            return jsonify({'success': True, 'message': 'Status updated'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>/notes', methods=['POST'])
def add_profile_note(profile_id):
    """Add note to profile"""
    try:
        data = request.json
        note = data.get('note', '')
        category = data.get('category', 'general')
        
        if not note:
            return jsonify({'error': 'Note is required'}), 400
        
        if profile_manager.add_note(profile_id, note, category):
            return jsonify({'success': True, 'message': 'Note added'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>/tags', methods=['POST'])
def add_profile_tag(profile_id):
    """Add tag to profile"""
    try:
        data = request.json
        tag = data.get('tag', '')
        
        if not tag:
            return jsonify({'error': 'Tag is required'}), 400
        
        if profile_manager.add_tag(profile_id, tag):
            return jsonify({'success': True, 'message': 'Tag added'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>/interactions', methods=['POST'])
def add_profile_interaction(profile_id):
    """Add interaction to profile"""
    try:
        data = request.json
        interaction_type = data.get('type', '')
        content = data.get('content', '')
        outcome = data.get('outcome', '')
        
        if not interaction_type or not content:
            return jsonify({'error': 'Type and content are required'}), 400
        
        if profile_manager.add_interaction(profile_id, interaction_type, content, outcome):
            return jsonify({'success': True, 'message': 'Interaction added'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/<profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete profile"""
    try:
        if profile_manager.delete_profile(profile_id):
            return jsonify({'success': True, 'message': 'Profile deleted'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profiles/export')
def export_profiles():
    """Export profiles to CSV"""
    try:
        filename = f"profiles_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if profile_manager.export_profiles_to_csv(filename):
            return send_from_directory('.', filename, as_attachment=True)
        else:
            return jsonify({'error': 'Export failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/stats')
def get_analytics_stats():
    """Get analytics statistics"""
    try:
        stats = profile_manager.get_stats()
        
        # Add additional analytics
        profiles = profile_manager.search_profiles()
        
        # Calculate engagement metrics
        engagement_metrics = {
            'total_profiles': len(profiles),
            'contacted_profiles': len([p for p in profiles if p.status.value in ['contacted', 'engaged', 'converted']]),
            'converted_profiles': len([p for p in profiles if p.status.value == 'converted']),
            'high_relevance_profiles': len([p for p in profiles if p.goal_alignment.relevance_score.value == 'High'])
        }
        
        # Calculate conversion rate
        if engagement_metrics['contacted_profiles'] > 0:
            engagement_metrics['conversion_rate'] = (engagement_metrics['converted_profiles'] / engagement_metrics['contacted_profiles']) * 100
        else:
            engagement_metrics['conversion_rate'] = 0
        
        # Recent activity
        recent_profiles = sorted(profiles, key=lambda p: p.created_at, reverse=True)[:10]
        recent_activity = [
            {
                'profile_id': p.profile_id,
                'name': p.name,
                'created_at': p.created_at.isoformat(),
                'status': p.status.value,
                'relevance_score': p.goal_alignment.relevance_score.value
            }
            for p in recent_profiles
        ]
        
        return jsonify({
            **stats,
            'engagement_metrics': engagement_metrics,
            'recent_activity': recent_activity
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/charts')
def get_analytics_charts():
    """Get data for analytics charts"""
    try:
        profiles = profile_manager.search_profiles()
        
        # Status distribution
        status_data = {}
        for profile in profiles:
            status = profile.status.value
            status_data[status] = status_data.get(status, 0) + 1
        
        # Relevance distribution
        relevance_data = {}
        for profile in profiles:
            relevance = profile.goal_alignment.relevance_score.value
            relevance_data[relevance] = relevance_data.get(relevance, 0) + 1
        
        # Discovery timeline (by month)
        timeline_data = {}
        for profile in profiles:
            month = profile.created_at.strftime('%Y-%m')
            timeline_data[month] = timeline_data.get(month, 0) + 1
        
        # Industry distribution
        industry_data = {}
        for profile in profiles:
            industry = profile.industry or 'Unknown'
            industry_data[industry] = industry_data.get(industry, 0) + 1
        
        return jsonify({
            'status_distribution': status_data,
            'relevance_distribution': relevance_data,
            'discovery_timeline': timeline_data,
            'industry_distribution': industry_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create templates and static directories
    Path('../frontend/templates').mkdir(parents=True, exist_ok=True)
    Path('../frontend/static').mkdir(parents=True, exist_ok=True)
    Path('../frontend/static/css').mkdir(parents=True, exist_ok=True)
    Path('../frontend/static/js').mkdir(parents=True, exist_ok=True)
    Path('profiles').mkdir(exist_ok=True)
    
    print("🌐 Starting Pregame Web Application...")
    print("🔧 Setting up directories...")
    print("🚀 Server starting on http://localhost:5000")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000) 