from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import pytz

db = SQLAlchemy()

# Get local timezone
def get_local_timezone():
    """Get local timezone (system timezone)"""
    import time
    import sys
    if sys.platform == 'win32':
        # For Windows, get local timezone offset
        offset_hours = -time.timezone / 3600
        return pytz.FixedOffset(int(offset_hours * 60))
    else:
        # For Unix-like systems
        return pytz.timezone(time.tzname[0])

class SharedItem(db.Model):
    """Model for shared files and text snippets"""
    __tablename__ = 'shared_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    item_type = db.Column(db.String(20), nullable=False)  # 'file' or 'text'
    
    # File specific fields
    filename = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # in bytes
    
    # Text specific fields
    title = db.Column(db.String(200), nullable=True)
    content = db.Column(db.Text, nullable=True)
    
    # Common fields
    created_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    download_count = db.Column(db.Integer, default=0)
    
    def __init__(self, item_type, expires_in_seconds, **kwargs):
        self.item_type = item_type
        # Use local timezone for display, but store as UTC for consistency
        current_time = datetime.now()
        self.created_at = current_time
        self.expires_at = current_time + timedelta(seconds=expires_in_seconds)
        super().__init__(**kwargs)
    
    def is_expired(self):
        """Check if the item has expired using local time"""
        return datetime.now() > self.expires_at
    
    def get_time_remaining(self):
        """Get remaining time as a dictionary"""
        now = datetime.now()
        
        if self.is_expired():
            return {
                'days': 0, 
                'hours': 0, 
                'minutes': 0, 
                'seconds': 0, 
                'total_seconds': 0, 
                'time_string': 'Expired',
                'status': 'expired'
            }
        
        remaining = self.expires_at - now
        total_seconds = int(remaining.total_seconds())
        
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        # Format readable time
        if days > 0:
            time_str = f"{days}d {hours}h"
        elif hours > 0:
            time_str = f"{hours}h {minutes}m"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'total_seconds': total_seconds,
            'time_string': time_str,
            'status': 'active'
        }
    
    def to_dict(self):
        """Convert model to dictionary for JSON responses"""
        time_data = self.get_time_remaining()
        return {
            'id': self.item_id,
            'type': self.item_type,
            'filename': self.filename,
            'title': self.title,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'time_remaining': time_data,
            'download_count': self.download_count,
            'is_expired': self.is_expired()
        }