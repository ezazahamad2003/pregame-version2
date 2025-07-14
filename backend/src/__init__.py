"""
Pregame Intelligent Discovery Engine - Source Package

This package contains the modular components for the intelligent, goal-based prospect discovery system.
"""

__version__ = "2.0.0"
__author__ = "Pregame Development Team"
__description__ = "AI-powered intelligent prospect discovery for any business goal"

# Core modules
from .core.discovery_engine import PregameClientDiscovery
from .core.prompt_manager import PromptManager

# Data processing
from .data.client_extractor import ClientExtractor
from .data.live_updates import LiveUpdateManager
from .data.profile_manager import ProfileManager
from .data.profile_storage import ProfileStorage

# Utilities
from .utils.env_manager import get_api_keys, validate_api_keys
from .utils.input_handler import get_complete_discovery_input, display_progress, display_summary, display_analysis_summary, confirm_proceed

__all__ = [
    'PregameClientDiscovery',
    'PromptManager',
    'ClientExtractor', 
    'LiveUpdateManager',
    'ProfileManager',
    'ProfileStorage',
    'get_api_keys',
    'validate_api_keys',
    'get_complete_discovery_input',
    'display_progress',
    'display_summary',
    'display_analysis_summary',
    'confirm_proceed'
] 