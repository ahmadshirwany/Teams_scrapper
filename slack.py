import requests
import json



class SlackWebhook:

    def __init__(self):

        self.webhook_url  = "https://hooks.slack.com/services/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"

    def send_message(self, message):

        payload = {
            'text': message  # Simple text message payload
        }
        response = requests.post(self.webhook_url, data=json.dumps(payload),
                                 headers={'Content-Type': 'application/json'})

        # Check the response status
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")


# Example usage:
if __name__ == "__main__":
    slack_notifier = SlackWebhook()
    slack_notifier.send_message("Hello from Python class!")
