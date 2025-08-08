#!/usr/bin/env python3
"""
Notification Service Base Classes and Data Models

Provides a structured interface for different notification services
like GitHub, email, Slack, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class Notification:
    """
    Standardized notification data structure
    """
    id: str
    title: str
    source: str
    type: str
    timestamp: datetime
    repository: Optional[str] = None
    url: Optional[str] = None
    reason: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class NotificationService(ABC):
    """
    Abstract base class for notification services
    """
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the name of this service"""
        pass
    
    @abstractmethod
    def get_notifications(self) -> Optional[List[Notification]]:
        """
        Fetch notifications from the service
        
        Returns:
            List of Notification objects or None if error
        """
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if the service is properly configured
        
        Returns:
            True if service can be used, False otherwise
        """
        pass


class NotificationManager:
    """
    Manages multiple notification services and aggregates their results
    """
    
    def __init__(self):
        self.services: List[NotificationService] = []
        self.seen_notifications: Dict[str, set] = {}
    
    def add_service(self, service: NotificationService):
        """Add a notification service to the manager"""
        if service.is_configured():
            self.services.append(service)
            self.seen_notifications[service.service_name] = set()
            print(f"Added {service.service_name} service")
        else:
            print(f"Warning: {service.service_name} service not properly configured")
    
    def get_all_notifications(self) -> List[Notification]:
        """
        Get notifications from all configured services
        
        Returns:
            List of all notifications from all services
        """
        all_notifications = []
        
        for service in self.services:
            try:
                notifications = service.get_notifications()
                if notifications:
                    all_notifications.extend(notifications)
            except Exception as e:
                print(f"Error fetching from {service.service_name}: {e}")
        
        return all_notifications
    
    def get_new_notifications(self) -> List[Notification]:
        """
        Get only new notifications (not seen before)
        
        Returns:
            List of new notifications from all services
        """
        new_notifications = []
        
        for service in self.services:
            try:
                notifications = service.get_notifications()
                if notifications:
                    service_seen = self.seen_notifications[service.service_name]
                    
                    for notification in notifications:
                        if notification.id not in service_seen:
                            new_notifications.append(notification)
                            service_seen.add(notification.id)
                            
            except Exception as e:
                print(f"Error fetching from {service.service_name}: {e}")
        
        return new_notifications
    
    def mark_notifications_as_seen(self, notifications: List[Notification]):
        """Mark notifications as seen to avoid duplicates"""
        for notification in notifications:
            for service_name, seen_set in self.seen_notifications.items():
                if notification.source == service_name:
                    seen_set.add(notification.id)