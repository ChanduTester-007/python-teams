from botbuilder.core import TurnContext
from botbuilder.schema import Activity
from .ticket_handler import TicketHandler

ticket_handler = TicketHandler()

class TeamsBot:
    async def on_message_activity(self, turn_context: TurnContext):
        text = turn_context.activity.text.lower()
        user = turn_context.activity.from_property.name

        if "create ticket" in text:
            issue = text.replace("create ticket", "").strip()
            ticket = ticket_handler.create_ticket(user, issue)
            await turn_context.send_activity(f"✅ Ticket created: ID {ticket['id']}, Issue: {issue}")

        elif "list tickets" in text:
            tickets = ticket_handler.get_tickets()
            if not tickets:
                await turn_context.send_activity("📂 No tickets found.")
            else:
                response = "\n".join([f"🆔 {t['id']} | {t['issue']} | Status: {t['status']}" for t in tickets])
                await turn_context.send_activity(f"📋 Your Tickets:\n{response}")

        elif "update ticket" in text:
            parts = text.split()
            if len(parts) >= 4:
                ticket_id = int(parts[2])
                status = parts[3]
                ticket = ticket_handler.update_ticket(ticket_id, status)
                if ticket:
                    await turn_context.send_activity(f"🔄 Ticket {ticket_id} updated to {status}")
                else:
                    await turn_context.send_activity("⚠️ Ticket not found.")
        else:
            await turn_context.send_activity("🤖 Available Commands:\n- `Create Ticket <issue>`\n- `List Tickets`\n- `Update Ticket <ID> <Status>`")
