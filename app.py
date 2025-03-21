from flask import Flask, request, jsonify
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity
from bot.bot import TeamsBot
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

app = Flask(__name__)
adapter = BotFrameworkAdapter(BotFrameworkAdapterSettings(app_id=None, app_password=None))
bot = TeamsBot()

@app.route("/api/messages", methods=["POST"])
async def messages():
    body = request.json
    activity = Activity().deserialize(body)
    auth_header = request.headers.get("Authorization", "")

    async def aux_func(turn_context):
        await bot.on_message_activity(turn_context)

    await adapter.process_activity(activity, auth_header, aux_func)
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
