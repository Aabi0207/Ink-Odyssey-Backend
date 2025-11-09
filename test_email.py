"""
Quick test script to verify email configuration
Run this to test email sending before deploying
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email():
    """Test email sending functionality"""
    print("Testing email configuration...")
    print(f"From: {settings.EMAIL_HOST_USER}")
    print(f"To: {settings.ADMIN_EMAIL}")
    
    try:
        result = send_mail(
            subject='InkOdyssey - Email Test',
            message='This is a test email. If you receive this, email configuration is working correctly!',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        if result == 1:
            print("✅ Email sent successfully!")
            print(f"Check {settings.ADMIN_EMAIL} for the test email.")
        else:
            print("❌ Email failed to send (no error raised)")
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in .env")
        print("2. Ensure you're using a Gmail App Password (not account password)")
        print("3. Verify 2-Step Verification is enabled on Gmail")
        print("4. Check internet connection")

if __name__ == '__main__':
    test_email()
