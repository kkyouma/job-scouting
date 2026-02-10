import requests

from src.config import settings
from src.models import JobListing
from src.util.logger_config import get_logger

logger = get_logger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        if self.token:
            self.base_url = f"https://api.telegram.org/bot{self.token.get_secret_value()}/sendMessage"
        else:
            self.base_url = None

    def notify(self, jobs: list[JobListing]):
        if not self.base_url or not self.chat_id:
            logger.warning("Telegram configuration missing. Skipping notification.")
            return

        if not jobs:
            self._send_message("No new jobs found matching your criteria.")
            return

        # Group messages to avoid hitting limits or spamming too much
        # Simple implementation: one message per job or a summary

        header = f"🚀 Found {len(jobs)} new jobs!\n\n"
        self._send_message(header)

        for job in jobs[:10]:  # Limit to 10 notifications to avoid spam
            msg = (
                f"**{job.title}**\n"
                f"🏢 {job.company_name}\n"
                f"📍 {job.location or 'Unknown'}\n"
                f"🔗 [Apply Here]({job.url})\n"
                f"🏷️ {', '.join(job.tags)}\n"
            )
            self._send_message(msg)

    def _send_message(self, text: str):
        if not self.base_url or not self.chat_id:
            logger.warning("Cannot send message: Missing Telegram config.")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(self.base_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
