#!/usr/bin/env python3
"""
GitHub Notification Service

Implements the NotificationService interface for GitHub notifications
"""

import os
import requests
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from ..core.notification_service import NotificationService, Notification

load_dotenv("config/.env")


class GitHubNotificationService(NotificationService):
    """GitHub notifications service implementation"""
    
    def __init__(self):
        self.token = os.getenv('GITHUB_TOKEN')
    
    @property
    def service_name(self) -> str:
        return "GitHub"
    
    def is_configured(self) -> bool:
        """Check if GitHub token is available"""
        return self.token is not None and self.token.strip() != ""
    
    def get_notifications(self) -> Optional[List[Notification]]:
        """
        Fetch GitHub notifications and convert to standard format
        
        Returns:
            List of Notification objects or None if error
        """
        if not self.is_configured():
            print("GitHub service not configured - missing GITHUB_TOKEN")
            return None
        
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Notifications-Printer'
        }
        
        try:
            response = requests.get('https://api.github.com/notifications', headers=headers)
            response.raise_for_status()
            raw_notifications = response.json()
            
            notifications = []
            for raw in raw_notifications:
                notification = self._convert_github_notification(raw)
                if notification:
                    notifications.append(notification)
            
            return notifications
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub notifications: {e}")
            return None
    
    def _convert_github_notification(self, raw_notification: dict) -> Optional[Notification]:
        """
        Convert GitHub API notification to standard Notification format
        
        Args:
            raw_notification: Raw notification from GitHub API
            
        Returns:
            Notification object or None if conversion fails
        """
        try:
            # Extract basic info
            notification_id = raw_notification.get('id')
            title = raw_notification.get('subject', {}).get('title', 'No Title')
            repo_name = raw_notification.get('repository', {}).get('full_name', 'Unknown Repo')
            reason = raw_notification.get('reason', 'unknown')
            updated_at = raw_notification.get('updated_at', '')
            url = raw_notification.get('subject', {}).get('url')
            
            # Parse timestamp
            timestamp = None
            if updated_at:
                try:
                    timestamp = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            # Determine notification type from reason
            notification_type = self._get_notification_type(reason)
            
            return Notification(
                id=notification_id,
                title=title,
                source=self.service_name,
                type=notification_type,
                timestamp=timestamp,
                repository=repo_name,
                url=url,
                reason=reason,
                raw_data=raw_notification
            )
            
        except Exception as e:
            print(f"Error converting GitHub notification: {e}")
            return None
    
    def _get_notification_type(self, reason: str) -> str:
        """
        Convert GitHub reason to notification type
        
        Args:
            reason: GitHub notification reason
            
        Returns:
            Standardized notification type
        """
        type_mapping = {
            'assign': 'Assignment',
            'author': 'Author',
            'comment': 'Comment',
            'invitation': 'Invitation',
            'manual': 'Manual',
            'mention': 'Mention',
            'review_requested': 'Review Request',
            'security_alert': 'Security Alert',
            'state_change': 'State Change',
            'subscribed': 'Subscription',
            'team_mention': 'Team Mention'
        }
        
        return type_mapping.get(reason.lower(), reason.title())