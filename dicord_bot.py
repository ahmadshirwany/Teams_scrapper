import requests
import json


class DiscordWebhook:
    def __init__(self):
        self.webhook_url = "https://discord.com/api/webhooks/1292820332331274381/VJiy4l5QeIHK4otMmywynuUJ1mELMXd6A9FXhkxPP8gC_c9eCfHvuxWE0fiZqaZSPxSf"

    def send_message(self, content, username="Webhook Bot"):
        data = {
            "content": content,
            "username": username
        }
        return self._post(data)

    def send_embed(self, content, embed_data, username="Webhook Bot"):
        data = {
            "content": content,
            "username": username,
            "embeds": [embed_data]
        }
        return self._post(data)

    def _post(self, data):
        response = requests.post(
            self.webhook_url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 204:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.status_code}, {response.text}")
        return response


if __name__ == "__main__":
    discord_webhook = DiscordWebhook()
    discord_webhook.send_message("Hello, this is a message from my Ahymad!")
