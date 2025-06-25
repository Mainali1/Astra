"""
Astra AI Assistant - Email Manager Feature Module
COPYRIGHT © 2024 Astra Technologies. ALL RIGHTS RESERVED.
"""

import logging
import json
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import aiofiles
from src.config import Config

logger = logging.getLogger(__name__)

class EmailManager:
    """Handles email operations."""
    
    def __init__(self, config: Config):
        """Initialize email manager."""
        self.config = config
        self.email_dir = Path(config.DATA_DIR) / 'email'
        self.email_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.email_dir / 'email_cache.json'
        self.cache: Dict[str, Any] = {'sent': [], 'received': []}
        self._load_cache()
        
        # Email server settings
        self.smtp_settings: Dict[str, Any] = {}
        self.imap_settings: Dict[str, Any] = {}
    
    def _load_cache(self):
        """Load email cache from file."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache['sent'])} sent and {len(self.cache['received'])} received emails")
        except Exception as e:
            logger.error(f"Error loading email cache: {str(e)}")
    
    def _save_cache(self):
        """Save email cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving email cache: {str(e)}")
    
    def configure_smtp(self, settings: Dict[str, Any]) -> bool:
        """Configure SMTP settings."""
        required = {'server', 'port', 'username', 'password', 'use_tls'}
        if not all(field in settings for field in required):
            return False
        
        self.smtp_settings = settings.copy()
        return True
    
    def configure_imap(self, settings: Dict[str, Any]) -> bool:
        """Configure IMAP settings."""
        required = {'server', 'port', 'username', 'password', 'use_ssl'}
        if not all(field in settings for field in required):
            return False
        
        self.imap_settings = settings.copy()
        return True
    
    async def send_email(self, to: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email."""
        try:
            if not self.smtp_settings:
                raise ValueError("SMTP not configured")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.smtp_settings['username']
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add body
            content_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, content_type))
            
            # Connect to SMTP server
            smtp = smtplib.SMTP(self.smtp_settings['server'], self.smtp_settings['port'])
            if self.smtp_settings['use_tls']:
                smtp.starttls()
            smtp.login(self.smtp_settings['username'], self.smtp_settings['password'])
            
            # Send email
            smtp.send_message(msg)
            smtp.quit()
            
            # Cache sent email
            sent_email = {
                'to': to,
                'subject': subject,
                'timestamp': datetime.now().isoformat(),
                'success': True
            }
            self.cache['sent'].append(sent_email)
            self._save_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            
            # Cache failed attempt
            if self.smtp_settings:
                sent_email = {
                    'to': to,
                    'subject': subject,
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': str(e)
                }
                self.cache['sent'].append(sent_email)
                self._save_cache()
            
            return False
    
    async def check_email(self, folder: str = 'INBOX', limit: int = 10) -> List[Dict[str, Any]]:
        """Check emails in specified folder."""
        try:
            if not self.imap_settings:
                raise ValueError("IMAP not configured")
            
            # Connect to IMAP server
            if self.imap_settings['use_ssl']:
                imap = imaplib.IMAP4_SSL(self.imap_settings['server'], self.imap_settings['port'])
            else:
                imap = imaplib.IMAP4(self.imap_settings['server'], self.imap_settings['port'])
            
            imap.login(self.imap_settings['username'], self.imap_settings['password'])
            imap.select(folder)
            
            # Search for emails
            _, message_numbers = imap.search(None, 'ALL')
            email_list = []
            
            # Get the last 'limit' emails
            for num in message_numbers[0].split()[-limit:]:
                _, msg_data = imap.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                # Extract email data
                email_data = {
                    'id': num.decode(),
                    'from': message['from'],
                    'to': message['to'],
                    'subject': message['subject'],
                    'date': message['date'],
                    'body': '',
                    'html': False
                }
                
                # Get email body
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "text/plain":
                            email_data['body'] = part.get_payload(decode=True).decode()
                        elif part.get_content_type() == "text/html":
                            email_data['body'] = part.get_payload(decode=True).decode()
                            email_data['html'] = True
                else:
                    email_data['body'] = message.get_payload(decode=True).decode()
                
                email_list.append(email_data)
            
            imap.close()
            imap.logout()
            
            # Cache received emails
            self.cache['received'].extend(email_list)
            self._save_cache()
            
            return email_list
            
        except Exception as e:
            logger.error(f"Error checking email: {str(e)}")
            return []
    
    def get_email_history(self, sent: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """Get email history from cache."""
        try:
            history = self.cache['sent' if sent else 'received']
            return sorted(
                history,
                key=lambda x: x['timestamp'] if sent else x['date'],
                reverse=True
            )[:limit]
        except Exception as e:
            logger.error(f"Error getting email history: {str(e)}")
            return []

class EmailManagerFeature:
    """Email manager feature for Astra."""
    
    def __init__(self, config: Config):
        """Initialize the email manager feature."""
        self.config = config
        self.manager = EmailManager(config)
    
    def _format_email(self, email_data: Dict[str, Any], sent: bool = False) -> str:
        """Format email for display."""
        if sent:
            return (
                f"To: {email_data['to']}\n"
                f"Subject: {email_data['subject']}\n"
                f"Sent: {email_data['timestamp']}\n"
                f"Status: {'✓' if email_data['success'] else '✗'}"
            )
        else:
            return (
                f"From: {email_data['from']}\n"
                f"Subject: {email_data['subject']}\n"
                f"Date: {email_data['date']}\n"
                f"\n{email_data['body'][:500]}..."
                if len(email_data['body']) > 500
                else f"\n{email_data['body']}"
            )
    
    def _format_email_list(self, emails: List[Dict[str, Any]], sent: bool = False) -> str:
        """Format email list for display."""
        if not emails:
            return "No emails found."
        
        response = "Email history:\n\n"
        for email_data in emails:
            response += self._format_email(email_data, sent) + "\n\n"
        return response
    
    async def handle(self, intent: Dict[str, Any]) -> str:
        """Handle email-related intents."""
        try:
            action = intent.get('action', '')
            params = intent.get('parameters', {})
            
            if action == 'configure_email':
                # Configure email settings
                smtp = params.get('smtp', {})
                imap = params.get('imap', {})
                
                success = True
                if smtp:
                    success &= self.manager.configure_smtp(smtp)
                if imap:
                    success &= self.manager.configure_imap(imap)
                
                if success:
                    return "Email settings configured successfully."
                return "Failed to configure email settings."
                
            elif action == 'send_email':
                # Send email
                to = params.get('to', '')
                subject = params.get('subject', '')
                body = params.get('body', '')
                html = params.get('html', False)
                
                if not all([to, subject, body]):
                    return "Please provide recipient, subject, and body."
                
                if await self.manager.send_email(to, subject, body, html):
                    return f"Email sent to {to}"
                return "Failed to send email."
                
            elif action == 'check_email':
                # Check emails
                folder = params.get('folder', 'INBOX')
                limit = int(params.get('limit', 10))
                
                emails = await self.manager.check_email(folder, limit)
                return self._format_email_list(emails)
                
            elif action == 'get_sent_history':
                # Get sent email history
                limit = int(params.get('limit', 10))
                emails = self.manager.get_email_history(sent=True, limit=limit)
                return self._format_email_list(emails, sent=True)
                
            elif action == 'get_received_history':
                # Get received email history
                limit = int(params.get('limit', 10))
                emails = self.manager.get_email_history(sent=False, limit=limit)
                return self._format_email_list(emails)
            
            else:
                return "I'm not sure what email operation you want to perform."
            
        except Exception as e:
            logger.error(f"Error handling email request: {str(e)}")
            return "I'm sorry, but I encountered an error with the email operation."
    
    def is_available(self) -> bool:
        """Check if the feature is available."""
        return True  # Email manager is always available
    
    async def cleanup(self):
        """Clean up resources."""
        pass  # No cleanup needed 