import os
import json
import logging
from aiohttp import web
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
from botbuilder.schema import Activity, ActivityTypes, ConversationReference
from dotenv import load_dotenv

# Load environment variables (local testing kosam; Render lo direct env vars use chestam)
load_dotenv()

# Microsoft Bot Credentials from Azure
APP_ID = os.getenv("MICROSOFT_APP_ID")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD")

# Debug print to verify credentials
print(f"APP_ID: {APP_ID}")
print(f"APP_PASSWORD: {APP_PASSWORD}")

# Validate credentials
if not APP_ID or not APP_PASSWORD:
    raise ValueError("MICROSOFT_APP_ID or MICROSOFT_APP_PASSWORD not set in environment variables")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot Adapter Settings
SETTINGS = BotFrameworkAdapterSettings(app_id=APP_ID, app_password=APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Store ConversationReferences in memory (production lo DB use cheyali)
conversation_references = {}

class TeamsBot:
    async def on_turn(self, turn_context: TurnContext):
        """Handle incoming messages from Teams"""
        if turn_context.activity.type == ActivityTypes.message:
            # Echo back the message
            reply = Activity(
                type=ActivityTypes.message,
                text=f"You said: {turn_context.activity.text}",
            )
            await turn_context.send_activity(reply)

            # Store the conversation reference
            ref = TurnContext.get_conversation_reference(turn_context.activity)
            conversation_references[ref.conversation.id] = ref
            logger.info(f"Stored conversation reference for conversation ID: {ref.conversation.id}")
        
        elif turn_context.activity.type == ActivityTypes.conversation_update:
            # Handle conversation updates (e.g., bot added to Teams)
            logger.info("Conversation update received")

    async def send_proactive_message(self, message: str, conversation_id: str = None):
        """Send a proactive message to Teams"""
        if not conversation_references:
            logger.error("No conversation references available")
            raise ValueError("No conversation references available. Interact with the bot in Teams first.")
        
        # Use specific conversation ID or first available one
        ref = conversation_references.get(conversation_id) if conversation_id else list(conversation_references.values())[0]
        
        async def send_message(turn_context: TurnContext):
            await turn_context.send_activity(message)
        
        await ADAPTER.continue_conversation(ref, send_message, APP_ID)
        logger.info(f"Proactive message sent to conversation ID: {ref.conversation.id}")

# Bot instance
BOT = TeamsBot()

# API Endpoint for Teams and Proactive Messages
async def messages(req: web.Request):
    """Handle POST requests from Teams and external triggers (e.g., Postman)"""
    if "application/json" not in req.headers["Content-Type"]:
        return web.Response(status=415, text="Unsupported Media Type")

    body = await req.json()
    logger.info(f"Received request: {json.dumps(body)}")

    # Handle incoming Teams messages
    if "type" in body and body["type"] in ["message", "conversationUpdate"]:
        activity = Activity().deserialize(body)
        await ADAPTER.process_activity(activity, "", BOT.on_turn)
        return web.Response(status=200)

    # Handle proactive message request
    message_text = body.get("text", "Hello from external trigger!")
    conversation_id = body.get("conversation_id")  # Optional: specify conversation
    try:
        await BOT.send_proactive_message(message_text, conversation_id)
        return web.json_response({"status": "Message sent to Teams"}, status=200)
    except Exception as e:
        logger.error(f"Error sending proactive message: {str(e)}")
        return web.json_response({"error": str(e)}, status=500)

# Create web app
app = web.Application()
app.router.add_post("/api/messages", messages)

# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", 3978))  # Render lo PORT env var use avtundi
    logger.info(f"Starting server on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)