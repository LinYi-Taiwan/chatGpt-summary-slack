import logging
from slack_sdk import WebClient
from dotenv import load_dotenv
import os

# logging.basicConfig(level=logging.DEBUG)
env_path = '.env'
load_dotenv(dotenv_path=env_path)

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
user_oauth_token = os.environ['USER_OAUTH_TOKEN']


# api_response = client.api_test()


class Slack:
    def __init__(self):
        self.client = WebClient(token=user_oauth_token)

    def post_message(self, msg,  channel_id, thread_id=''):
        try:
            self.client.chat_postMessage(
                channel=channel_id,
                thread_ts=thread_id,
                text=msg,
                token=user_oauth_token
            )
        except:
            print('Error')

    def get_thread_conversations(self, channel_id, thread_id):
        res = self.client.conversations_replies(
            channel=channel_id,
            ts=thread_id
        )

        return res
