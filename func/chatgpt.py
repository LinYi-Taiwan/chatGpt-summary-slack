import os
import openai
from dotenv import load_dotenv

env_path = '.env'
load_dotenv(dotenv_path=env_path)
openai.api_key = os.environ['OPENAI_KEY']
model = os.environ['OPENAI_MODEL']


class ChatGPT:
    def __init__(self):
        self.max_tokens = 500,
        self.temperature = 0.3,
        self.model = model
        self.messages = []

    def get_response(self, msg):

        response = openai.ChatCompletion.create(
            model=self.model,
            max_tokens=500,
            temperature=0.7,
            messages=[
                {"role": "system", "content": "你是一個摘要高手，請用中文摘要以下內容"},
                {"role": "user", "content": msg},
            ]
        )
        result = response.choices[0].message.content
        return result
