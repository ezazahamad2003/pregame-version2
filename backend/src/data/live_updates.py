"""
Live updates manager for real-time progress tracking
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

class LiveUpdateManager:
    """Manages live updates during client discovery process"""
    
    def __init__(self, filename: str = None):
        self.filename = filename or "pregame_client_discovery_live.json"
        self.updates = {
            'start_time': datetime.now().isoformat(),
            'status': 'starting',
            'stage': 'initialization',
            'clients_found': [],
            'progress': {
                'discovery': {'current': 0, 'total': 0},
                'qualification': {'current': 0, 'total': 0}
            },
            'logs': []
        }
    
    async def save_live_update(self, data: Dict):
        """
        Save live update to JSON file
        
        Args:
            data: Update data to save
        """
        try:
            self.updates.update(data)
            self.updates['last_updated'] = datetime.now().isoformat()
            
            with open(self.filename, 'w') as f:
                json.dump(self.updates, f, indent=2)
                
        except Exception as e:
            print(f"   ❌ Failed to save live update: {e}")
    
    async def update_stage(self, stage: str, status: str = None):
        """
        Update current stage and status
        
        Args:
            stage: Current stage name
            status: Optional status message
        """
        update_data = {
            'stage': stage,
            'status': status or 'in_progress'
        }
        
        await self.save_live_update(update_data)
    
    async def update_progress(self, stage: str, current: int, total: int):
        """
        Update progress for a specific stage
        
        Args:
            stage: Stage name ('discovery' or 'qualification')
            current: Current progress
            total: Total items
        """
        self.updates['progress'][stage] = {
            'current': current,
            'total': total
        }
        
        await self.save_live_update({})
    
    async def add_client(self, client: Dict):
        """
        Add a discovered client to the live updates
        
        Args:
            client: Client data dictionary
        """
        self.updates['clients_found'].append({
            'name': client.get('name', 'Unknown'),
            'business': client.get('business', 'Not specified'),
            'signals': client.get('signals', 'None'),
            'discovered_at': datetime.now().isoformat()
        })
        
        await self.save_live_update({})
    
    async def log_message(self, message: str, level: str = 'info'):
        """
        Add a log message to the live updates
        
        Args:
            message: Log message
            level: Log level (info, warning, error)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        
        self.updates['logs'].append(log_entry)
        
        # Keep only last 50 log entries
        if len(self.updates['logs']) > 50:
            self.updates['logs'] = self.updates['logs'][-50:]
        
        await self.save_live_update({})
    
    async def complete_discovery(self, final_results: Dict):
        """
        Mark discovery as complete and save final results
        
        Args:
            final_results: Final discovery results
        """
        completion_data = {
            'status': 'completed',
            'stage': 'finished',
            'end_time': datetime.now().isoformat(),
            'final_results': final_results,
            'total_clients': len(final_results.get('clients', []))
        }
        
        await self.save_live_update(completion_data)
    
    async def handle_error(self, error: str, stage: str = None):
        """
        Handle and log errors during discovery
        
        Args:
            error: Error message
            stage: Current stage where error occurred
        """
        error_data = {
            'status': 'error',
            'stage': stage or self.updates.get('stage', 'unknown'),
            'error': error,
            'error_time': datetime.now().isoformat()
        }
        
        await self.save_live_update(error_data)
        await self.log_message(f"ERROR: {error}", 'error')
    
    def get_current_status(self) -> Dict:
        """
        Get current status of the discovery process
        
        Returns:
            Dict: Current status information
        """
        return {
            'status': self.updates.get('status', 'unknown'),
            'stage': self.updates.get('stage', 'unknown'),
            'clients_found': len(self.updates.get('clients_found', [])),
            'progress': self.updates.get('progress', {}),
            'duration': self._calculate_duration()
        }
    
    def _calculate_duration(self) -> str:
        """Calculate elapsed time since start"""
        start_time = self.updates.get('start_time')
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                duration = datetime.now() - start_dt
                return str(duration).split('.')[0]  # Remove microseconds
            except:
                return "unknown"
        return "unknown"
    
    def cleanup(self):
        """Clean up the live update file"""
        try:
            if Path(self.filename).exists():
                Path(self.filename).unlink()
        except Exception as e:
            print(f"   ❌ Failed to cleanup live update file: {e}") 