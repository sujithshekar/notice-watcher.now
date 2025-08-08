print("🛠 Restarting...")

import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.sync_api import sync_playwright

# Log env variables for debugging
print("🚨 Debugging Environment Variables:")
print("EMAIL_SENDER:", os.getenv("EMAIL_SENDER"))
print("EMAIL_PASSWORD exists:", os.getenv("EMAIL_PASSWORD") is not None)
print("EMAIL_RECEIVER:", os.getenv("EMAIL_RECEIVER"))
print("SMTP_SERVER:", os.getenv("SMTP_SERVER"))
print("SMTP_PORT:", os.getenv("SMTP_PORT"))
print("EMAIL_SUBJECT:", os.getenv("EMAIL_SUBJECT"))

# Load credentials from .env
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT", "New NBEMS Notice Alert")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📧 Email sent.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def get_latest_notice():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Headless mode ON
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()
        print("🔍 Checking for updates...")
        try:
            page.goto("https://natboard.edu.in/allnotice.php", timeout=60000)
            page.wait_for_selector("a[href^='viewNotice.php']", timeout=20000)
            first_notice = page.locator("a[href^='viewNotice.php']").first
            text = first_notice.inner_text()
            print(f"🔔 Latest Notice: {text}")
            return text.strip()
        except Exception as e:
            print(f"⚠️ Error while checking notices: {e}")
            return None
        finally:
            browser.close()


def read_last_notice():
    if os.path.exists("last_notice.txt"):
        with open("last_notice.txt", "r") as f:
            return f.read().strip()
    return None


def save_latest_notice(notice):
    with open("last_notice.txt", "w") as f:
        f.write(notice)


def main():
    print("🔍 Starting notice watcher...")
    while True:
        latest_notice = get_latest_notice()
        if latest_notice is None:
            print("⚠️ Could not fetch latest notice.")
        else:
            last_notice = read_last_notice()
            if latest_notice != last_notice:
                print("🆕 New notice! Sending email...")
                send_email(EMAIL_SUBJECT, latest_notice)
                save_latest_notice(latest_notice)
            else:
                print("ℹ️ No new notice.")
        time.sleep(30)  # Check every 30 seconds


if __name__ == "__main__":
    main()

