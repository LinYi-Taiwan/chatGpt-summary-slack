
from flask import Flask, request
from func.chatgpt import ChatGPT
from func.slack import Slack
import json
import pandas as pd


app = Flask(__name__)

summary = ChatGPT()
slack = Slack()


@app.route("/", methods=['POST'])
def hello():

    data = json.loads(request.data)

    channel_id = data['event']['channel']
    thread_id = data['event']['thread_ts']

    r = slack.get_thread_conversations(
        channel_id=channel_id,
        thread_id=thread_id
    )

    messages = r.get('messages')

    df = pd.DataFrame.from_dict(messages)
    text = '\n'.join(df['text'].values)

    result = summary.get_response(text)
    slack.post_message(result, channel_id, thread_id)

    return {}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
