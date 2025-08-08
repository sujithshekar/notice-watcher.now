from playwright.sync_api import sync_playwright
import time
import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

print("🔁 Running the correct main.py file ✅")

# Load environment variables from .env
load_dotenv()

# Debug environment variables
print("🚨 Debugging Environment Variables (from .env):")
print(f"EMAIL_SENDER: {os.getenv('EMAIL_SENDER')}")
print(f"EMAIL_PASSWORD exists: {'EMAIL_PASSWORD' in os.environ}")
print(f"EMAIL_RECEIVER: {os.getenv('EMAIL_RECEIVER')}")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"EMAIL_SUBJECT: {os.getenv('EMAIL_SUBJECT')}")

# Email function
def send_email(subject, body):
    sender = os.getenv("EMAIL_SENDER")
    receiver = os.getenv("EMAIL_RECEIVER")
    password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT"))

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Function to get latest notice text
def get_latest_notice_text(page):
    try:
        page.goto("https://natboard.edu.in/allnotice.php", timeout=60000)
        page.wait_for_selector("a.view-notice", timeout=10000)
        notice = page.locator("a.view-notice").first.inner_text()
        return notice.strip()
    except Exception as e:
        print(f"❌ Error fetching notice: {e}")
        return None

# Main loop
def main():
    last_notice = None
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        while True:
            print("🔍 Checking for updates...")
            current_notice = get_latest_notice_text(page)

            if current_notice:
                print(f"🔔 Latest Notice: {current_notice}")
                if current_notice != last_notice:
                    print("🆕 New notice! Sending email...")
                    send_email(
                        os.getenv("EMAIL_SUBJECT", "New Notice Alert"),
                        current_notice
                    )
                    last_notice = current_notice
                else:
                    print("ℹ️ No new notice.")
            else:
                print("⚠️ Failed to fetch notice.")

            time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()

