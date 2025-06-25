"""
AI-driven email management feature for Astra
"""
from typing import Dict, List, Optional
import json
import os
import email
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.ai.deepseek_client import DeepSeekClient

class EmailManager:
    def __init__(self):
        self.client = DeepSeekClient()
        self.config_dir = os.path.join(os.path.dirname(__file__), '../../config')
        self.credentials = self._load_credentials()
        
    def _load_credentials(self) -> Dict:
        """Load email credentials from config"""
        config_path = os.path.join(self.config_dir, 'email_config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {}
            
    async def summarize_emails(self, emails: List[Dict]) -> List[Dict]:
        """Summarize a list of emails using AI"""
        summaries = []
        for email_data in emails:
            prompt = f"""Summarize the following email:

From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}
Content:
{email_data.get('body', '')}

Provide:
1. Key points
2. Action items (if any)
3. Priority level
4. Required response (if any)

Format as JSON with these sections."""

            response = await self.client.generate_response(prompt)
            try:
                summary = json.loads(response)
                summary.update({
                    'email_id': email_data.get('id'),
                    'from': email_data.get('from'),
                    'subject': email_data.get('subject')
                })
                summaries.append(summary)
            except:
                summaries.append({
                    "error": "Failed to summarize email",
                    "email_id": email_data.get('id')
                })
                
        return summaries

    async def generate_email_response(self, email_data: Dict) -> str:
        """Generate an AI-powered email response"""
        prompt = f"""Generate a professional email response to the following email:

From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}
Content:
{email_data.get('body', '')}

Requirements:
1. Maintain professional tone
2. Address all points in the original email
3. Be concise but thorough
4. Include appropriate greeting and closing

Generate the complete response."""

        response = await self.client.generate_response(prompt)
        return response.strip()

    async def prioritize_emails(self, emails: List[Dict]) -> List[Dict]:
        """Prioritize emails using AI analysis"""
        prompt = f"""Analyze and prioritize the following emails:

{json.dumps(emails, indent=2)}

For each email, determine:
1. Priority level (High/Medium/Low)
2. Response urgency
3. Category (e.g., Action Required, FYI, Follow-up)
4. Suggested handling

Format as JSON array with these attributes."""

        response = await self.client.generate_response(prompt)
        try:
            return json.loads(response)
        except:
            return [{"error": "Failed to prioritize emails"}]

    def connect_imap(self, email: str, password: str) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to IMAP server"""
        # This is a simplified example - would need proper server detection
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(email, password)
            return mail
        except Exception as e:
            print(f"Failed to connect to IMAP: {e}")
            return None

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email using SMTP"""
        if not self.credentials:
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.credentials.get('email')
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(self.credentials.get('email'), self.credentials.get('password'))
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

class EmailManagerFeature:
    def __init__(self):
        self.manager = EmailManager()
        
    async def process_command(self, command: str) -> str:
        """Process email management related commands"""
        if "summarize emails" in command.lower():
            # This is a simplified example - would need actual email fetching
            emails = [
                {
                    "id": "1",
                    "from": "example@example.com",
                    "subject": "Meeting Tomorrow",
                    "body": "Can we meet tomorrow at 2 PM to discuss the project?"
                }
            ]
            summaries = await self.manager.summarize_emails(emails)
            return self._format_email_summaries(summaries)
            
        elif "generate response" in command.lower():
            # Extract email details from command
            email_data = {
                "from": "example@example.com",
                "subject": "Project Update",
                "body": "Please provide an update on the project status."
            }
            response = await self.manager.generate_email_response(email_data)
            return response
            
        elif "prioritize emails" in command.lower():
            # This is a simplified example
            emails = [
                {
                    "id": "1",
                    "subject": "Urgent: Server Down",
                    "from": "admin@example.com"
                }
            ]
            priorities = await self.manager.prioritize_emails(emails)
            return self._format_email_priorities(priorities)
            
        return "I'm not sure how to help with that email task."

    def _format_email_summaries(self, summaries: List[Dict]) -> str:
        """Format email summaries for display"""
        if summaries and "error" in summaries[0]:
            return f"Failed to summarize emails: {summaries[0]['error']}"
            
        result = "Email Summaries:\n\n"
        for summary in summaries:
            result += f"From: {summary.get('from', 'Unknown')}\n"
            result += f"Subject: {summary.get('subject', 'No Subject')}\n"
            result += f"Key Points:\n"
            for point in summary.get('key_points', []):
                result += f"- {point}\n"
            if summary.get('action_items'):
                result += f"\nAction Items:\n"
                for item in summary['action_items']:
                    result += f"- {item}\n"
            result += f"\nPriority: {summary.get('priority', 'Unknown')}\n"
            result += f"Required Response: {summary.get('required_response', 'None')}\n\n"
        return result

    def _format_email_priorities(self, priorities: List[Dict]) -> str:
        """Format email priorities for display"""
        if priorities and "error" in priorities[0]:
            return f"Failed to prioritize emails: {priorities[0]['error']}"
            
        result = "Email Priorities:\n\n"
        for priority in priorities:
            result += f"Subject: {priority.get('subject', 'Unknown')}\n"
            result += f"Priority: {priority.get('priority_level', 'Unknown')}\n"
            result += f"Urgency: {priority.get('response_urgency', 'Unknown')}\n"
            result += f"Category: {priority.get('category', 'Unknown')}\n"
            result += f"Suggested Handling: {priority.get('suggested_handling', 'Unknown')}\n\n"
        return result

# Initialize the feature
email_manager_feature = EmailManagerFeature()

# Export the command handler
async def handle_email_command(command: str) -> str:
    """Handle email management related voice commands"""
    return await email_manager_feature.process_command(command) 