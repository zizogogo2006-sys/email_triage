import imaplib
import email
import openai
import os
import json
import logging

# Configuration
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD") # App Password
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

def fetch_unread_emails():
    """Connects to IMAP server and fetches unread emails."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select('inbox')

        # Search for unread emails
        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        emails = []
        for e_id in email_ids:
            status, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    body = get_email_body(msg)
                    emails.append({"id": e_id, "subject": subject, "sender": sender, "body": body})
        return mail, emails
    except Exception as e:
        logging.error(f"Failed to fetch emails: {e}")
        return None, []

def get_email_body(msg):
    """Extracts text content from an email message."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()
    return ""

def analyze_and_draft_response(email_data: dict) -> dict:
    """Uses OpenAI to categorize the email and draft a response."""
    prompt = f"""
    Analyze this customer support email.
    Sender: {email_data['sender']}
    Subject: {email_data['subject']}
    Body: {email_data['body']}
    
    Tasks:
    1. Categorize it: "Refund Request", "Technical Issue", "Feature Request", "Spam", "Other"
    2. Determine urgency: "High", "Medium", "Low"
    3. Draft a polite, professional response. If it's a refund, state it will be processed in 3-5 days. If technical, ask for OS and browser details.
    
    Output strictly as JSON:
    {{
        "category": "...",
        "urgency": "...",
        "draft_response": "..."
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a senior customer support AI."},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(response.choices[0].message.content)

def process_support_inbox():
    logging.info("Checking inbox for new support tickets...")
    mail_conn, emails = fetch_unread_emails()
    
    if not emails:
        logging.info("No new emails.")
        return
        
    for e in emails:
        logging.info(f"Processing email from {e['sender']}: {e['subject']}")
        analysis = analyze_and_draft_response(e)
        
        logging.info(f"Category: {analysis['category']} | Urgency: {analysis['urgency']}")
        logging.info(f"Drafted Response:\n{analysis['draft_response']}\n")
        
        # In a full system, we would:
        # 1. Forward High urgency to Slack via webhook
        # 2. Save the draft in a CRM (Zendesk/Freshdesk) or send it directly
        
        # Mark as read (optional during testing)
        # mail_conn.store(e['id'], '+FLAGS', '\SEEN')

if __name__ == "__main__":
    process_support_inbox()
