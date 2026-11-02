import os
import re
import tempfile

from gtts import gTTS
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ["SLACK_BOT_TOKEN"])


@app.shortcut("read_aloud")
def read_aloud(ack, shortcut, client):
    ack()  # risponde subito a Slack (ha solo 3 secondi)

    user_id = shortcut["user"]["id"]
    text = shortcut["message"].get("text", "")
    text = re.sub(r"<[^>]+>", "", text).strip()  # toglie menzioni e link
    dm = client.conversations_open(users=user_id)["channel"]["id"]

    if not text:
        client.chat_postMessage(channel=dm, text="Questo messaggio non contiene testo da leggere.")
        return

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "messaggio.mp3")
        gTTS(text=text[:5000], lang="it").save(path)
        client.files_upload_v2(
            channel=dm,
            file=path,
            title="Messaggio letto ad alta voce",
            initial_comment="🎧 Ecco il tuo messaggio in audio",
        )


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
