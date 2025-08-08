# Multi-Service Notification Printer

A modular Python application that fetches notifications from multiple services (GitHub, Slack, Email, etc.) and prints them to thermal printers. Built with a clean, extensible architecture that makes it easy to add new notification services and printer types.

## 🌟 Features

- ✅ **Multi-Service Support** - GitHub notifications (more services coming)
- ✅ **Extensible Architecture** - Easy to add new notification services
- ✅ **Smart Polling** - Only prints new notifications, no duplicates
- ✅ **Thermal Printer Support** - Netum Bluetooth printers (NT-1809D compatible)
- ✅ **Structured Output** - Clean, formatted notifications
- ✅ **Auto-Discovery** - Automatically finds your thermal printer
- ✅ **Real-time Monitoring** - Polls every 60 seconds for new notifications

## 📁 Project Structure

```
Print-GitHub-Notifications/
├── 📁 config/
│   └── .env                    # Environment variables
├── 📁 src/
│   ├── 📁 core/
│   │   └── notification_service.py    # Base classes & data models
│   ├── 📁 services/
│   │   └── github_service.py          # GitHub API implementation
│   └── 📁 printers/
│       └── netum_printer.py           # Thermal printer interface
├── 📁 tests/                  # Test files
├── main.py                    # Main application
├── requirements.txt           # Dependencies
└── setup.py                  # Package installation
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd Print-Notifications

# Install dependencies
pip install -r requirements.txt

# Or install as package (recommended)
pip install -e .
```

### 2. Setup Your Thermal Printer

1. Turn on your Netum printer
2. Pair it with your computer via Bluetooth settings
3. Make sure it's connected (not just paired)

### 3. Configure GitHub Notifications

1. Get a GitHub Personal Access Token:

   - Go to https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select the `notifications` scope
   - Copy the generated token

2. Create configuration:

   ```bash
   # Create config/.env file with your token
   echo "GITHUB_TOKEN=your_github_token_here" > config/.env
   ```

### 4. Run the Application

```bash
# Start monitoring (polls every 60 seconds)
python main.py

# Or if installed as package
print-notifications
```

## 📋 Usage Examples

### Basic Usage

The application automatically starts polling all configured services every 60 seconds and prints only new notifications.

### One-time Print All Notifications

```python
from src.core.notification_service import NotificationManager
from src.services.github_service import GitHubNotificationService

manager = NotificationManager()
manager.add_service(GitHubNotificationService())

notifications = manager.get_all_notifications()
print(f"Found {len(notifications)} notifications")
```

### Custom Service Integration

```python
from src.core.notification_service import NotificationManager
from src.services.github_service import GitHubNotificationService
# from src.services.slack_service import SlackNotificationService  # Future

def setup_notification_manager():
    manager = NotificationManager()

    # Add GitHub service
    manager.add_service(GitHubNotificationService())

    # Add more services as needed
    # manager.add_service(SlackNotificationService())

    return manager
```

## 🔧 Creating Custom Notification Services

### Step 1: Implement the NotificationService Interface

Create a new file in `src/services/your_service.py`:

```python
#!/usr/bin/env python3
"""
Your Custom Notification Service
"""

import os
from datetime import datetime
from typing import List, Optional
from ..core.notification_service import NotificationService, Notification

class YourNotificationService(NotificationService):
    """Your custom notification service implementation"""

    def __init__(self):
        # Initialize your service (API keys, config, etc.)
        self.api_key = os.getenv('YOUR_SERVICE_API_KEY')

    @property
    def service_name(self) -> str:
        return "YourService"

    def is_configured(self) -> bool:
        """Check if service is properly configured"""
        return self.api_key is not None and self.api_key.strip() != ""

    def get_notifications(self) -> Optional[List[Notification]]:
        """
        Fetch notifications from your service

        Returns:
            List of Notification objects or None if error
        """
        if not self.is_configured():
            print("YourService not configured - missing API key")
            return None

        try:
            # Your API call logic here
            raw_notifications = self._fetch_from_api()

            notifications = []
            for raw in raw_notifications:
                notification = self._convert_notification(raw)
                if notification:
                    notifications.append(notification)

            return notifications

        except Exception as e:
            print(f"Error fetching notifications from YourService: {e}")
            return None

    def _fetch_from_api(self):
        """Implement your API fetching logic"""
        # Example: return requests.get(your_api_endpoint).json()
        pass

    def _convert_notification(self, raw_data) -> Optional[Notification]:
        """Convert your API response to standard Notification format"""
        try:
            return Notification(
                id=raw_data.get('id'),
                title=raw_data.get('title', 'No Title'),
                source=self.service_name,
                type=raw_data.get('type', 'Unknown'),
                timestamp=datetime.now(),  # Parse from your API
                repository=raw_data.get('repo'),  # If applicable
                url=raw_data.get('url'),
                reason=raw_data.get('reason'),
                raw_data=raw_data
            )
        except Exception as e:
            print(f"Error converting notification: {e}")
            return None
```

### Step 2: Add to Main Application

Update `main.py` to include your service:

```python
def setup_notification_manager() -> NotificationManager:
    manager = NotificationManager()

    # Add existing services
    manager.add_service(GitHubNotificationService())

    # Add your new service
    from src.services.your_service import YourNotificationService
    manager.add_service(YourNotificationService())

    return manager
```

### Step 3: Add Configuration

Add any required environment variables to `config/.env`:

```bash
YOUR_SERVICE_API_KEY=your_api_key_here
```

## 🎨 Notification Data Structure

All notifications are converted to a standardized format:

```python
@dataclass
class Notification:
    id: str                    # Unique identifier
    title: str                 # Notification title
    source: str               # Service name (e.g., "GitHub")
    type: str                 # Notification type (e.g., "Comment")
    timestamp: datetime       # When notification occurred
    repository: Optional[str] # Repository name (if applicable)
    url: Optional[str]       # Link to notification
    reason: Optional[str]    # Why you received this notification
    raw_data: Optional[Dict] # Original API response
```

## 🖨️ Adding Custom Printers

### Step 1: Create Printer Implementation

Create `src/printers/your_printer.py`:

```python
from typing import List
from ..core.notification_service import Notification

class YourPrinter:
    """Your custom printer implementation"""

    def __init__(self):
        # Initialize your printer connection
        pass

    def is_connected(self) -> bool:
        """Check if printer is connected"""
        pass

    def print_notifications(self, notifications: List[Notification]) -> bool:
        """Print notifications to your printer"""
        pass
```

### Step 2: Update Main Application

Modify `main.py` to use your printer instead of NetumPrinter.

## 📊 Available Services

### ✅ GitHub Notifications

- **Status**: Implemented
- **Requirements**: GitHub Personal Access Token with `notifications` scope
- **Features**: Issues, PRs, mentions, reviews, assignments

### 🔄 Planned Services

- **Slack**: Direct messages, mentions, channel notifications
- **Email**: IMAP/Gmail API integration
- **Discord**: Server notifications, DMs
- **Jira**: Assigned issues, comments
- **Azure DevOps**: Work items, builds, PRs

## 🛠️ Development

### Running Tests

```bash
# Future: when tests are added
python -m pytest tests/
```

### Code Structure Guidelines

- **Services**: Implement `NotificationService` interface
- **Data Models**: Use the standardized `Notification` dataclass
- **Error Handling**: Always return `None` on errors, log issues
- **Configuration**: Use environment variables in `config/.env`

## 📝 API Reference

### NotificationService (Abstract Base Class)

#### Required Methods

```python
@property
def service_name(self) -> str:
    """Return service name (e.g., 'GitHub')"""

def is_configured(self) -> bool:
    """Return True if service is properly configured"""

def get_notifications(self) -> Optional[List[Notification]]:
    """Fetch and return list of notifications"""
```

### NotificationManager

#### Key Methods

```python
def add_service(self, service: NotificationService):
    """Add a notification service"""

def get_all_notifications(self) -> List[Notification]:
    """Get notifications from all services"""

def get_new_notifications(self) -> List[Notification]:
    """Get only new notifications (not seen before)"""
```

## 🔧 Configuration

All configuration is done via environment variables in `config/.env`:

```bash
# GitHub
GITHUB_TOKEN=your_github_token_here

# Future services
SLACK_TOKEN=your_slack_token_here
EMAIL_PASSWORD=your_email_password_here
```

## 🐛 Troubleshooting

### No Notifications Printed

1. Check if services are configured (API tokens in `config/.env`)
2. Verify printer connection (should auto-discover Netum printers)
3. Ensure you have actual new notifications to print

### Import Errors

1. Make sure you're in the project root directory
2. Install requirements: `pip install -r requirements.txt`
3. Check Python path includes the project directory

### Printer Issues

1. Ensure Netum printer is paired AND connected via Bluetooth
2. Close other applications that might be using the printer
3. Try restarting the printer

## 📄 License

This project is open source. Feel free to use, modify, and distribute.
