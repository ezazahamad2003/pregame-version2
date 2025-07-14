"""
Profile Management CLI Utilities

Command-line interface for managing prospect profiles
"""

from typing import List, Optional
import sys
from datetime import datetime

from ..data.profile_manager import ProfileManager
from ..data.prospect_profile import ProspectStatus, RelevanceScore

class ProfileCLI:
    """Command-line interface for profile management"""
    
    def __init__(self):
        self.profile_manager = ProfileManager()
    
    def show_main_menu(self):
        """Display main menu options"""
        print("\n🎯 PREGAME PROFILE MANAGEMENT")
        print("=" * 40)
        print("1. 📊 View Profile Statistics")
        print("2. 🔍 Search Profiles")
        print("3. 📋 List All Profiles")
        print("4. 👁️  View Profile Details")
        print("5. ✏️  Update Profile")
        print("6. 📝 Add Note to Profile")
        print("7. 🏷️  Add Tag to Profile")
        print("8. 📤 Export Profiles to CSV")
        print("9. 🗑️  Delete Profile")
        print("10. 💾 Backup Profiles")
        print("0. 🚪 Exit")
        print("=" * 40)
        
        choice = input("Enter your choice (0-10): ").strip()
        return choice
    
    def view_stats(self):
        """Display profile statistics"""
        print("\n📊 PROFILE STATISTICS")
        print("-" * 30)
        
        stats = self.profile_manager.get_stats()
        
        print(f"Total Profiles: {stats['total_profiles']}")
        print(f"Storage Location: {stats['storage_location']}")
        print(f"Last Updated: {stats['last_updated']}")
        print(f"Total Tags: {stats['total_tags']}")
        
        # Status breakdown
        print("\n📈 Status Breakdown:")
        for status, count in stats['status_breakdown'].items():
            print(f"  {status}: {count}")
        
        # Relevance breakdown
        print("\n🎯 Relevance Breakdown:")
        for relevance, count in stats['relevance_breakdown'].items():
            print(f"  {relevance}: {count}")
        
        # Company breakdown
        print("\n🏢 Company Breakdown:")
        for company, count in stats['company_breakdown'].items():
            print(f"  {company}: {count}")
        
        input("\nPress Enter to continue...")
    
    def search_profiles(self):
        """Search profiles with filters"""
        print("\n🔍 SEARCH PROFILES")
        print("-" * 25)
        
        filters = {}
        
        # Company filter
        company = input("Company name (or press Enter to skip): ").strip()
        if company:
            filters['company'] = company
        
        # Goal filter
        goal = input("Goal (or press Enter to skip): ").strip()
        if goal:
            filters['goal'] = goal
        
        # Status filter
        print("\nStatus options: discovered, qualified, contacted, engaged, converted, rejected, archived")
        status = input("Status (or press Enter to skip): ").strip()
        if status:
            filters['status'] = status
        
        # Relevance filter
        print("\nRelevance options: High, Medium, Low, Unscored")
        relevance = input("Relevance (or press Enter to skip): ").strip()
        if relevance:
            filters['relevance'] = relevance
        
        # Tags filter
        tags = input("Tags (comma-separated, or press Enter to skip): ").strip()
        if tags:
            filters['tags'] = [tag.strip() for tag in tags.split(',')]
        
        # Name filter
        name = input("Name (partial match, or press Enter to skip): ").strip()
        if name:
            filters['name'] = name
        
        # Execute search
        profiles = self.profile_manager.search_profiles(**filters)
        
        if not profiles:
            print("❌ No profiles found matching your criteria.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n✅ Found {len(profiles)} profiles:")
        print("-" * 50)
        
        for i, profile in enumerate(profiles, 1):
            print(f"{i}. {profile.get_summary()}")
        
        # Option to view details
        while True:
            choice = input(f"\nEnter profile number to view details (1-{len(profiles)}) or press Enter to return: ").strip()
            if not choice:
                break
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(profiles):
                    self.view_profile_details(profiles[index])
                else:
                    print("❌ Invalid profile number.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    def list_profiles(self):
        """List all profiles with pagination"""
        print("\n📋 ALL PROFILES")
        print("-" * 20)
        
        page = 0
        page_size = 10
        
        while True:
            profiles_data = self.profile_manager.list_profiles(limit=page_size, offset=page * page_size)
            
            if not profiles_data:
                if page == 0:
                    print("❌ No profiles found.")
                else:
                    print("❌ No more profiles.")
                break
            
            print(f"\nPage {page + 1} (showing {len(profiles_data)} profiles):")
            print("-" * 40)
            
            for i, profile_data in enumerate(profiles_data, 1):
                print(f"{i + page * page_size}. {profile_data['name']} ({profile_data['prospect_type']})")
                print(f"   Status: {profile_data['status']} | Relevance: {profile_data['relevance_score']}")
                print(f"   Company: {profile_data['discovering_company']} | Goal: {profile_data['company_goal']}")
                print("")
            
            print("Options: [n]ext page, [p]revious page, [v]iew profile, [r]eturn to menu")
            choice = input("Enter choice: ").strip().lower()
            
            if choice == 'n':
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice == 'v':
                try:
                    profile_num = int(input("Enter profile number to view: "))
                    if 1 <= profile_num <= len(profiles_data):
                        profile_data = profiles_data[profile_num - 1]
                        profile = self.profile_manager.get_profile(profile_data['profile_id'])
                        if profile:
                            self.view_profile_details(profile)
                    else:
                        print("❌ Invalid profile number.")
                except ValueError:
                    print("❌ Please enter a valid number.")
            elif choice == 'r':
                break
            else:
                print("❌ Invalid choice.")
    
    def view_profile_details(self, profile=None):
        """View detailed profile information"""
        if not profile:
            profile_id = input("Enter profile ID: ").strip()
            profile = self.profile_manager.get_profile(profile_id)
            
            if not profile:
                print("❌ Profile not found.")
                return
        
        print(f"\n👁️  PROFILE DETAILS: {profile.name}")
        print("=" * 50)
        
        # Basic info
        print(f"Profile ID: {profile.profile_id}")
        print(f"Name: {profile.name}")
        print(f"Type: {profile.prospect_type.value}")
        print(f"Status: {profile.status.value}")
        print(f"Industry: {profile.industry}")
        print(f"Location: {profile.location}")
        print(f"Company Size: {profile.company_size}")
        print(f"Business: {profile.business_description}")
        
        # Contact info
        print(f"\n📞 CONTACT INFORMATION:")
        print(f"Email: {profile.contact_info.email or 'Not provided'}")
        print(f"Phone: {profile.contact_info.phone or 'Not provided'}")
        print(f"LinkedIn: {profile.contact_info.linkedin or 'Not provided'}")
        print(f"Website: {profile.contact_info.website or 'Not provided'}")
        
        # Goal alignment
        print(f"\n🎯 GOAL ALIGNMENT:")
        print(f"Relevance Score: {profile.goal_alignment.relevance_score.value}")
        print(f"Fit Reasons: {', '.join(profile.goal_alignment.fit_reasons) if profile.goal_alignment.fit_reasons else 'None'}")
        print(f"Potential Value: {profile.goal_alignment.potential_value}")
        print(f"Approach Priority: {profile.goal_alignment.approach_priority}")
        
        # Discovery info
        print(f"\n🔍 DISCOVERY INFORMATION:")
        print(f"Discovered by: {profile.discovery_metadata.discovering_company}")
        print(f"Goal: {profile.discovery_metadata.company_goal}")
        print(f"Discovery Date: {profile.discovery_metadata.discovery_date.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Intelligence
        if profile.recent_activities:
            print(f"\n📊 RECENT ACTIVITIES:")
            for activity in profile.recent_activities:
                print(f"  • {activity}")
        
        if profile.pain_points:
            print(f"\n🔴 PAIN POINTS:")
            for pain_point in profile.pain_points:
                print(f"  • {pain_point}")
        
        if profile.buying_signals:
            print(f"\n🟢 BUYING SIGNALS:")
            for signal in profile.buying_signals:
                print(f"  • {signal}")
        
        # Interactions
        if profile.interactions:
            print(f"\n💬 INTERACTIONS:")
            for interaction in profile.interactions[-5:]:  # Show last 5
                print(f"  [{interaction['timestamp']}] {interaction['type']}: {interaction['content']}")
        
        # Notes
        if profile.notes:
            print(f"\n📝 NOTES:")
            for note in profile.notes[-3:]:  # Show last 3
                print(f"  [{note['timestamp']}] {note['category']}: {note['content']}")
        
        # Tags
        if profile.tags:
            print(f"\n🏷️  TAGS:")
            print(f"  {', '.join(profile.tags)}")
        
        # System info
        print(f"\n⚙️  SYSTEM INFO:")
        print(f"Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Updated: {profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Version: {profile.version}")
        
        input("\nPress Enter to continue...")
    
    def update_profile_status(self):
        """Update profile status"""
        profile_id = input("Enter profile ID: ").strip()
        
        print("\nStatus options:")
        print("1. discovered")
        print("2. qualified")
        print("3. contacted")
        print("4. engaged")
        print("5. converted")
        print("6. rejected")
        print("7. archived")
        
        choice = input("Enter new status (1-7): ").strip()
        
        status_map = {
            '1': ProspectStatus.DISCOVERED,
            '2': ProspectStatus.QUALIFIED,
            '3': ProspectStatus.CONTACTED,
            '4': ProspectStatus.ENGAGED,
            '5': ProspectStatus.CONVERTED,
            '6': ProspectStatus.REJECTED,
            '7': ProspectStatus.ARCHIVED
        }
        
        if choice in status_map:
            if self.profile_manager.update_status(profile_id, status_map[choice]):
                print("✅ Status updated successfully!")
            else:
                print("❌ Failed to update status. Profile not found.")
        else:
            print("❌ Invalid status choice.")
        
        input("\nPress Enter to continue...")
    
    def add_note(self):
        """Add note to profile"""
        profile_id = input("Enter profile ID: ").strip()
        note = input("Enter note: ").strip()
        category = input("Enter category (default: general): ").strip() or "general"
        
        if self.profile_manager.add_note(profile_id, note, category):
            print("✅ Note added successfully!")
        else:
            print("❌ Failed to add note. Profile not found.")
        
        input("\nPress Enter to continue...")
    
    def add_tag(self):
        """Add tag to profile"""
        profile_id = input("Enter profile ID: ").strip()
        tag = input("Enter tag: ").strip()
        
        if self.profile_manager.add_tag(profile_id, tag):
            print("✅ Tag added successfully!")
        else:
            print("❌ Failed to add tag. Profile not found.")
        
        input("\nPress Enter to continue...")
    
    def export_profiles(self):
        """Export profiles to CSV"""
        filename = input("Enter filename (default: profiles_export.csv): ").strip()
        if not filename:
            filename = "profiles_export.csv"
        
        if self.profile_manager.export_profiles_to_csv(filename):
            print("✅ Profiles exported successfully!")
        else:
            print("❌ Export failed.")
        
        input("\nPress Enter to continue...")
    
    def delete_profile(self):
        """Delete profile"""
        profile_id = input("Enter profile ID: ").strip()
        
        # Show profile details first
        profile = self.profile_manager.get_profile(profile_id)
        if not profile:
            print("❌ Profile not found.")
            input("\nPress Enter to continue...")
            return
        
        print(f"\n⚠️  You are about to delete profile: {profile.name}")
        print(f"   Type: {profile.prospect_type.value}")
        print(f"   Status: {profile.status.value}")
        print(f"   Created: {profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        confirm = input("\nAre you sure you want to delete this profile? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            if self.profile_manager.delete_profile(profile_id):
                print("✅ Profile deleted successfully!")
            else:
                print("❌ Failed to delete profile.")
        else:
            print("❌ Deletion cancelled.")
        
        input("\nPress Enter to continue...")
    
    def backup_profiles(self):
        """Backup profiles"""
        backup_dir = input("Enter backup directory (default: backups): ").strip() or "backups"
        
        if self.profile_manager.backup_profiles(backup_dir):
            print("✅ Backup created successfully!")
        else:
            print("❌ Backup failed.")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Run the profile management CLI"""
        print("🎯 Starting Pregame Profile Management CLI...")
        
        while True:
            try:
                choice = self.show_main_menu()
                
                if choice == '0':
                    print("\n👋 Goodbye!")
                    break
                elif choice == '1':
                    self.view_stats()
                elif choice == '2':
                    self.search_profiles()
                elif choice == '3':
                    self.list_profiles()
                elif choice == '4':
                    self.view_profile_details()
                elif choice == '5':
                    self.update_profile_status()
                elif choice == '6':
                    self.add_note()
                elif choice == '7':
                    self.add_tag()
                elif choice == '8':
                    self.export_profiles()
                elif choice == '9':
                    self.delete_profile()
                elif choice == '10':
                    self.backup_profiles()
                else:
                    print("❌ Invalid choice. Please try again.")
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ An error occurred: {e}")
                input("\nPress Enter to continue...")

def main():
    """Main entry point for profile CLI"""
    cli = ProfileCLI()
    cli.run()

if __name__ == "__main__":
    main() 