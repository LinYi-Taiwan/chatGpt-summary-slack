from flask import Flask, request, render_template
from func.chatgpt import ChatGPT
from func.slack import Slack
from func.gitlab import Gitlab
import json
import pandas as pd


app = Flask(__name__)

summary = ChatGPT()
search_engine = ChatGPT()
slack = Slack()
gitlab = Gitlab()


@app.route("/", methods=['POST'])
def thread_summary():

    data = json.loads(request.data)

    channel_id = data['event']['channel']

    if 'thread_ts' not in data['event']:
        slack.post_message('Not in thread.', channel_id)
        return
    else:
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


@app.route("/search")
def search():
    query = request.args.to_dict()
    if 'text' in query:
        question = query['text']
    else:
        question = 'No question.'

    result = search_engine.get_simarity(question)

    return render_template('qa.html', result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
