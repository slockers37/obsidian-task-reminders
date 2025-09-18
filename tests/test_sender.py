import requests
from dotenv import load_dotenv

# Load config from .env and config.yml
load_dotenv()
from config import load_config

def send_test_message():
    """Sends a single test message to the configured Gotify server."""
    print("Attempting to send a test message to Gotify...")
    try:
        config = load_config()
        url = f"{config.gotify.url}/message"
        headers = {"X-Gotify-Key": config.gotify.token}
        payload = {
            "title": "Test Message from Reminder App",
            "message": "Hello! If you received this, your Gotify configuration is working correctly.",
            "priority": 5
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            print("\nSuccess! Test message sent to Gotify.")
            print("Please check your Gotify client.")
        else:
            print(f"\nError: Failed to send message. Gotify server responded with status code {response.status_code}.")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    send_test_message()
