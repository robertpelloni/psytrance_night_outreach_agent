from src.ai_engine import AIEngine

class ReplyParser:
    def __init__(self, ai=None):
        self.ai = ai or AIEngine()

    def parse_reply(self, reply_content):
        """
        Ingests raw email/DM replies and outputs structured negotiation objects
        (date offers, capacity constraints, fee ranges, vibe concerns).
        """
        # We delegate the core extraction logic to the established AI method
        # but encapsulate it here for cleaner architecture.
        return self.ai.extract_negotiation_constraints(reply_content)
