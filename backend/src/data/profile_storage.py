"""
Profile Storage System

JSON-based storage for prospect profiles with full CRUD operations
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .prospect_profile import ProspectProfile, ProspectType, RelevanceScore, ProspectStatus

class ProfileStorage:
    """JSON-based storage system for prospect profiles"""
    
    def __init__(self, storage_dir: str = "profiles"):
        """
        Initialize profile storage
        
        Args:
            storage_dir: Directory to store profile files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        self.profiles_dir = self.storage_dir / "profiles"
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.index_file = self.storage_dir / "index.json"
        self.metadata_file = self.storage_dir / "metadata.json"
        
        # Initialize index and metadata
        self._init_index()
        self._init_metadata()
    
    def _init_index(self):
        """Initialize or load profile index"""
        if not self.index_file.exists():
            self.index = {
                "profiles": {},
                "by_company": {},
                "by_goal": {},
                "by_status": {},
                "by_relevance": {},
                "by_tags": {},
                "last_updated": datetime.now().isoformat()
            }
            self._save_index()
        else:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
    
    def _init_metadata(self):
        """Initialize storage metadata"""
        if not self.metadata_file.exists():
            self.metadata = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "total_profiles": 0,
                "last_backup": None,
                "storage_stats": {
                    "total_size": 0,
                    "avg_profile_size": 0
                }
            }
            self._save_metadata()
        else:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
    
    def _save_index(self):
        """Save profile index"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _save_metadata(self):
        """Save storage metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def _get_profile_file(self, profile_id: str) -> Path:
        """Get profile file path"""
        return self.profiles_dir / f"{profile_id}.json"
    
    def _update_index(self, profile: ProspectProfile):
        """Update index with profile information"""
        profile_id = profile.profile_id
        
        # Main profile entry
        self.index["profiles"][profile_id] = {
            "name": profile.name,
            "prospect_type": profile.prospect_type.value,
            "status": profile.status.value,
            "relevance_score": profile.goal_alignment.relevance_score.value,
            "company_goal": profile.discovery_metadata.company_goal,
            "discovering_company": profile.discovery_metadata.discovering_company,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "tags": profile.tags
        }
        
        # Index by company
        company = profile.discovery_metadata.discovering_company
        if company not in self.index["by_company"]:
            self.index["by_company"][company] = []
        if profile_id not in self.index["by_company"][company]:
            self.index["by_company"][company].append(profile_id)
        
        # Index by goal
        goal = profile.discovery_metadata.company_goal
        if goal not in self.index["by_goal"]:
            self.index["by_goal"][goal] = []
        if profile_id not in self.index["by_goal"][goal]:
            self.index["by_goal"][goal].append(profile_id)
        
        # Index by status
        status = profile.status.value
        if status not in self.index["by_status"]:
            self.index["by_status"][status] = []
        if profile_id not in self.index["by_status"][status]:
            self.index["by_status"][status].append(profile_id)
        
        # Index by relevance
        relevance = profile.goal_alignment.relevance_score.value
        if relevance not in self.index["by_relevance"]:
            self.index["by_relevance"][relevance] = []
        if profile_id not in self.index["by_relevance"][relevance]:
            self.index["by_relevance"][relevance].append(profile_id)
        
        # Index by tags
        for tag in profile.tags:
            if tag not in self.index["by_tags"]:
                self.index["by_tags"][tag] = []
            if profile_id not in self.index["by_tags"][tag]:
                self.index["by_tags"][tag].append(profile_id)
    
    def _remove_from_index(self, profile_id: str):
        """Remove profile from index"""
        if profile_id not in self.index["profiles"]:
            return
        
        profile_data = self.index["profiles"][profile_id]
        
        # Remove from main index
        del self.index["profiles"][profile_id]
        
        # Remove from secondary indexes
        company = profile_data.get("discovering_company", "")
        if company in self.index["by_company"]:
            if profile_id in self.index["by_company"][company]:
                self.index["by_company"][company].remove(profile_id)
            if not self.index["by_company"][company]:
                del self.index["by_company"][company]
        
        goal = profile_data.get("company_goal", "")
        if goal in self.index["by_goal"]:
            if profile_id in self.index["by_goal"][goal]:
                self.index["by_goal"][goal].remove(profile_id)
            if not self.index["by_goal"][goal]:
                del self.index["by_goal"][goal]
        
        status = profile_data.get("status", "")
        if status in self.index["by_status"]:
            if profile_id in self.index["by_status"][status]:
                self.index["by_status"][status].remove(profile_id)
            if not self.index["by_status"][status]:
                del self.index["by_status"][status]
        
        relevance = profile_data.get("relevance_score", "")
        if relevance in self.index["by_relevance"]:
            if profile_id in self.index["by_relevance"][relevance]:
                self.index["by_relevance"][relevance].remove(profile_id)
            if not self.index["by_relevance"][relevance]:
                del self.index["by_relevance"][relevance]
        
        # Remove from tags
        for tag in profile_data.get("tags", []):
            if tag in self.index["by_tags"]:
                if profile_id in self.index["by_tags"][tag]:
                    self.index["by_tags"][tag].remove(profile_id)
                if not self.index["by_tags"][tag]:
                    del self.index["by_tags"][tag]
    
    def save_profile(self, profile: ProspectProfile) -> bool:
        """
        Save profile to storage
        
        Args:
            profile: ProspectProfile to save
            
        Returns:
            bool: True if successful
        """
        try:
            # Save profile file
            profile_file = self._get_profile_file(profile.profile_id)
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Update index
            self._update_index(profile)
            self._save_index()
            
            # Update metadata
            self.metadata["total_profiles"] = len(self.index["profiles"])
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error saving profile {profile.profile_id}: {e}")
            return False
    
    def load_profile(self, profile_id: str) -> Optional[ProspectProfile]:
        """
        Load profile from storage
        
        Args:
            profile_id: ID of profile to load
            
        Returns:
            Optional[ProspectProfile]: Profile if found, None otherwise
        """
        try:
            profile_file = self._get_profile_file(profile_id)
            if not profile_file.exists():
                return None
            
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            return ProspectProfile.from_dict(profile_data)
            
        except Exception as e:
            print(f"Error loading profile {profile_id}: {e}")
            return None
    
    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete profile from storage
        
        Args:
            profile_id: ID of profile to delete
            
        Returns:
            bool: True if successful
        """
        try:
            # Remove file
            profile_file = self._get_profile_file(profile_id)
            if profile_file.exists():
                profile_file.unlink()
            
            # Remove from index
            self._remove_from_index(profile_id)
            self._save_index()
            
            # Update metadata
            self.metadata["total_profiles"] = len(self.index["profiles"])
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting profile {profile_id}: {e}")
            return False
    
    def list_profiles(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all profiles with pagination
        
        Args:
            limit: Maximum number of profiles to return
            offset: Number of profiles to skip
            
        Returns:
            List[Dict[str, Any]]: List of profile summaries
        """
        profiles = list(self.index["profiles"].items())
        profiles.sort(key=lambda x: x[1]["updated_at"], reverse=True)
        
        return [
            {
                "profile_id": profile_id,
                **profile_data
            }
            for profile_id, profile_data in profiles[offset:offset + limit]
        ]
    
    def search_profiles(self, **filters) -> List[str]:
        """
        Search profiles by various criteria
        
        Args:
            **filters: Search criteria
            
        Returns:
            List[str]: List of matching profile IDs
        """
        results = set()
        
        # Search by company
        if "company" in filters:
            company = filters["company"]
            if company in self.index["by_company"]:
                results.update(self.index["by_company"][company])
        
        # Search by goal
        if "goal" in filters:
            goal = filters["goal"]
            if goal in self.index["by_goal"]:
                if results:
                    results.intersection_update(self.index["by_goal"][goal])
                else:
                    results.update(self.index["by_goal"][goal])
        
        # Search by status
        if "status" in filters:
            status = filters["status"]
            if status in self.index["by_status"]:
                if results:
                    results.intersection_update(self.index["by_status"][status])
                else:
                    results.update(self.index["by_status"][status])
        
        # Search by relevance
        if "relevance" in filters:
            relevance = filters["relevance"]
            if relevance in self.index["by_relevance"]:
                if results:
                    results.intersection_update(self.index["by_relevance"][relevance])
                else:
                    results.update(self.index["by_relevance"][relevance])
        
        # Search by tags
        if "tags" in filters:
            tags = filters["tags"] if isinstance(filters["tags"], list) else [filters["tags"]]
            tag_results = set()
            for tag in tags:
                if tag in self.index["by_tags"]:
                    tag_results.update(self.index["by_tags"][tag])
            if results:
                results.intersection_update(tag_results)
            else:
                results.update(tag_results)
        
        # Search by name (partial match)
        if "name" in filters:
            name_filter = filters["name"].lower()
            name_results = []
            for profile_id, profile_data in self.index["profiles"].items():
                if name_filter in profile_data.get("name", "").lower():
                    name_results.append(profile_id)
            if results:
                results.intersection_update(name_results)
            else:
                results.update(name_results)
        
        # If no specific filters, return all profiles
        if not results and not filters:
            results = set(self.index["profiles"].keys())
        
        return list(results)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dict[str, Any]: Storage statistics
        """
        total_profiles = len(self.index["profiles"])
        
        # Count by status
        status_counts = {}
        for status, profiles in self.index["by_status"].items():
            status_counts[status] = len(profiles)
        
        # Count by relevance
        relevance_counts = {}
        for relevance, profiles in self.index["by_relevance"].items():
            relevance_counts[relevance] = len(profiles)
        
        # Count by company
        company_counts = {}
        for company, profiles in self.index["by_company"].items():
            company_counts[company] = len(profiles)
        
        return {
            "total_profiles": total_profiles,
            "status_breakdown": status_counts,
            "relevance_breakdown": relevance_counts,
            "company_breakdown": company_counts,
            "total_tags": len(self.index["by_tags"]),
            "storage_location": str(self.storage_dir),
            "last_updated": self.index["last_updated"]
        }
    
    def backup_profiles(self, backup_dir: str = "backups") -> bool:
        """
        Create backup of all profiles
        
        Args:
            backup_dir: Directory to store backup
            
        Returns:
            bool: True if successful
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"profiles_backup_{timestamp}.json"
            
            # Create backup data
            backup_data = {
                "metadata": self.metadata,
                "index": self.index,
                "profiles": {}
            }
            
            # Add all profiles
            for profile_id in self.index["profiles"].keys():
                profile = self.load_profile(profile_id)
                if profile:
                    backup_data["profiles"][profile_id] = profile.to_dict()
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            # Update metadata
            self.metadata["last_backup"] = datetime.now().isoformat()
            self._save_metadata()
            
            print(f"✅ Backup created: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False 