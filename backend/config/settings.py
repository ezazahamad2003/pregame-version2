"""
Configuration settings for Pregame Client Discovery Engine
"""

# Default search settings
DEFAULT_SEARCH_SETTINGS = {
    'breadth': 2,
    'depth': 1,
    'max_retries': 3,
    'timeout': 30
}

# Default qualification settings
DEFAULT_QUALIFICATION_SETTINGS = {
    'breadth': 3,
    'depth': 2,
    'max_retries': 2,
    'timeout': 45
}

# Client discovery limits
CLIENT_LIMITS = {
    'min_count': 5,
    'max_count': 30,
    'default_count': 10
}

# Supported client types
SUPPORTED_CLIENT_TYPES = [
    'companies',
    'individuals',
    'both'
]

# Default API settings
DEFAULT_API_SETTINGS = {
    'openai_model': 'gpt-4o-mini',
    'openai_temperature': 0.1,
    'google_api_key': 'AIzaSyAT4tQKRNt1rwrqrTs2GzlXuWi-BAYJWPA',
    'google_cx': '010381b2504d141f5'
}

# Live update settings
LIVE_UPDATE_SETTINGS = {
    'max_log_entries': 50,
    'update_interval': 1.0,
    'auto_cleanup': True
}

# Report formatting
REPORT_SETTINGS = {
    'encoding': 'utf-8',
    'include_timestamp': True,
    'include_insights': True
} 