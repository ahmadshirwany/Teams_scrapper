import requests
import json

# Your Discord webhook URL
webhook_url = 'https://discord.com/api/webhooks/1292820332331274381/VJiy4l5QeIHK4otMmywynuUJ1mELMXd6A9FXhkxPP8gC_c9eCfHvuxWE0fiZqaZSPxSf'

# Message data
data = {
    "content": "Hello, this is a message from my webhook!",
    "username": "My Webhook"
}

# Post the message to the Discord channel
response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})

# Check the response
if response.status_code == 204:
    print("Message sent successfully!")
else:
    print(f"Failed to send message: {response.status_code}")
