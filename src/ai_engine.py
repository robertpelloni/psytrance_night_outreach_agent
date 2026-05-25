import os
from openai import OpenAI
import json

class AIEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def vibe_check(self, venue_name, raw_text):
        if not self.client:
            print("No OpenAI client configured. Returning default vibe score.")
            return {"vibe_score": 5, "justification": "AI not configured."}

        prompt = f"""
        Analyze this venue description and determine if it is suitable for a psytrance night.
        Venue Name: {venue_name}
        Description: {raw_text}

        Output JSON format:
        {{
            "vibe_score": (1-10),
            "justification": "short explanation"
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a music culture expert."},
                          {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"AI Error: {e}")
            return {"vibe_score": 0, "justification": f"Error: {e}"}

    def generate_pitch(self, venue_name, justification):
        if not self.client:
            return "Hey, we would love to play at your venue!"

        prompt = f"""
        Write a professional cold email to the booking manager of {venue_name}.
        The reason we like them is: {justification}
        We are a collective of psytrance selectors looking to start a recurring night.
        The tone should be professional and value-driven.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a professional booking agent."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI Error: {e}")
            return "Error generating pitch."
