#!/usr/bin/env python3
"""
Multi-Service Notifications Printer

Fetches notifications from multiple services and prints them to a thermal printer.
"""

import time
from datetime import datetime
from src.printers.netum_printer import NetumPrinter
from src.core.notification_service import NotificationManager, Notification
from src.services.github_service import GitHubNotificationService


def format_notification_for_print(notification: Notification) -> str:
    """
    Format a single notification for printing
    
    Args:
        notification: Notification object
        
    Returns:
        String formatted for thermal printer
    """
    # Format timestamp
    formatted_time = notification.timestamp.strftime('%Y-%m-%d %H:%M')
    
    # Format for thermal printer (typically 32-48 chars wide)
    output = []
    output.append("=" * 32)
    output.append(f"SERVICE: {notification.source}"[:32])
    if notification.repository:
        output.append(f"REPO: {notification.repository}"[:32])
    output.append(f"TYPE: {notification.type}"[:32])
    if notification.reason:
        output.append(f"REASON: {notification.reason.upper()}"[:32])
    output.append(f"TIME: {formatted_time}"[:32])
    output.append("-" * 32)
    
    # Wrap title text to fit printer width
    title_lines = []
    words = notification.title.split()
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= 32:
            current_line += (" " + word if current_line else word)
        else:
            if current_line:
                title_lines.append(current_line)
            current_line = word
    
    if current_line:
        title_lines.append(current_line)
    
    output.extend(title_lines)
    output.append("=" * 32)
    output.append("")  # Blank line between notifications
    
    return "\n".join(output)


def setup_notification_manager() -> NotificationManager:
    """
    Set up and configure all notification services
    
    Returns:
        Configured NotificationManager instance
    """
    manager = NotificationManager()
    
    # Add GitHub service
    github_service = GitHubNotificationService()
    manager.add_service(github_service)
    
    # Future services can be added here:
    # manager.add_service(SlackNotificationService())
    # manager.add_service(EmailNotificationService())
    
    return manager


def print_notifications_to_printer(notifications):
    """
    Print notifications to the thermal printer
    
    Args:
        notifications: List of Notification objects to print
    """
    if not notifications:
        return True
        
    with NetumPrinter() as printer:
        if not printer.is_connected:
            print("Failed to connect to printer")
            return False
        
        # Group notifications by service
        services = {}
        for notification in notifications:
            if notification.source not in services:
                services[notification.source] = []
            services[notification.source].append(notification)
        
        # Print header
        printer.print_line("=" * 32)
        printer.print_line("NOTIFICATIONS")
        printer.print_line("=" * 32)
        printer.print_line(f"Total: {len(notifications)}")
        printer.print_line(f"Services: {', '.join(services.keys())}")
        printer.print_line(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        printer.print_line("")
        
        # Print notifications grouped by service
        for service_name, service_notifications in services.items():
            printer.print_line(f"--- {service_name.upper()} ---")
            printer.print_line(f"Count: {len(service_notifications)}")
            printer.print_line("")
            
            for i, notification in enumerate(service_notifications, 1):
                print(f"Printing {service_name} notification {i}/{len(service_notifications)}")
                formatted_text = format_notification_for_print(notification)
                printer.print_text(formatted_text)
        
        # Final separator
        printer.print_line("=" * 32)
        printer.print_line("END OF NOTIFICATIONS")
        printer.print_line("=" * 32)
        printer.feed_lines(3)
    
    return True


def poll_notifications():
    """
    Continuously poll all notification services every 60 seconds
    Print only new notifications to the thermal printer
    """
    manager = setup_notification_manager()
    
    if not manager.services:
        print("No notification services configured!")
        return
    
    print(f"Starting notifications polling (every 60 seconds)")
    print(f"Configured services: {', '.join([s.service_name for s in manager.services])}")
    print("Press Ctrl+C to stop")
    
    # Initial check to populate seen notifications
    print("Performing initial check...")
    initial_notifications = manager.get_all_notifications()
    if initial_notifications:
        manager.mark_notifications_as_seen(initial_notifications)
        print(f"Tracking {len(initial_notifications)} existing notifications")
    
    try:
        while True:
            print(f"\nChecking for new notifications... {datetime.now().strftime('%H:%M:%S')}")
            
            new_notifications = manager.get_new_notifications()
            
            if new_notifications:
                print(f"Found {len(new_notifications)} new notifications - printing...")
                success = print_notifications_to_printer(new_notifications)
                if success:
                    print("New notifications printed successfully!")
                else:
                    print("Failed to print notifications")
            else:
                print("No new notifications")
            
            # Wait 60 seconds before next check
            print("Waiting 60 seconds...")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nStopping notification polling...")


def print_all_notifications():
    """
    One-time check and print of all current notifications from all services
    """
    manager = setup_notification_manager()
    
    if not manager.services:
        print("No notification services configured!")
        return
    
    print("Fetching notifications from all services...")
    notifications = manager.get_all_notifications()
    
    if not notifications:
        print("No notifications found")
        return
    
    print(f"Found {len(notifications)} total notifications")
    success = print_notifications_to_printer(notifications)
    if success:
        print("All notifications printed successfully!")
    else:
        print("Failed to print notifications")


def main():
    """Main function - start polling for notifications"""
    poll_notifications()


if __name__ == "__main__":
    main()