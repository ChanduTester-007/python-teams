import json
import os

class TicketHandler:
    def __init__(self):
        self.db_file = "tickets.json"
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w') as f:
                json.dump([], f)

    def create_ticket(self, user, issue):
        ticket = {"id": len(self.get_tickets()) + 1, "user": user, "issue": issue, "status": "Open"}
        tickets = self.get_tickets()
        tickets.append(ticket)
        with open(self.db_file, 'w') as f:
            json.dump(tickets, f)
        return ticket

    def get_tickets(self):
        with open(self.db_file, 'r') as f:
            return json.load(f)

    def update_ticket(self, ticket_id, status):
        tickets = self.get_tickets()
        for ticket in tickets:
            if ticket["id"] == ticket_id:
                ticket["status"] = status
                with open(self.db_file, 'w') as f:
                    json.dump(tickets, f)
                return ticket
        return None
