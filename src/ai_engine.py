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
        Analyze this venue description and social media context to determine if it is suitable for a psytrance night.
        Venue Name: {venue_name}
        Context/Description: {raw_text}

        Criteria for high score (7-10):
        - References to 'underground', 'forest', 'psy', 'techno', 'dark', 'industrial'.
        - Mentions of high-quality sound systems (Funktion-One, etc.).
        - Immersive visual elements mentioned in bio or reviews.
        - Open-minded music policy.

        Output JSON format:
        {{
            "vibe_score": (1-10),
            "justification": "Detailed explanation incorporating social context if available"
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

    def generate_follow_up(self, venue_name, original_pitch):
        if not self.client:
            return "Just following up on our previous email regarding a psytrance night!"

        prompt = f"""
        Write a short, polite follow-up email to a booking manager at {venue_name}.
        We previously sent them a pitch for a psytrance residency.

        Original Pitch context:
        {original_pitch[:500]}...

        The follow-up should be brief, friendly, and just checking if they had a chance to see our proposal.
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
            return "Just checking back on my previous email!"

    def extract_venue_traits(self, raw_text):
        """Parses venue description for technical and atmospheric traits."""
        if not self.client or not raw_text: return "{}"

        prompt = f"""
        Analyze the following text about a music venue and extract key traits in JSON format.
        Focus on:
        1. sound_system: Mentioned brands or quality (e.g., 'Funktion-One', 'Void').
        2. lighting: Notable features (e.g., 'projection mapping', 'lasers').
        3. atmosphere: Keywords (e.g., 'intimate', 'industrial', 'outdoor').
        4. music_policy: Primary genres mentioned.

        Text: "{raw_text[:2000]}"

        Return ONLY valid JSON.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error extracting traits: {e}")
            return "{}"

    def analyze_sentiment(self, reply_content):
        if not self.client:
            return "UNKNOWN"

        prompt = f"""
        Analyze the sentiment of this venue's response to our booking pitch.
        Categorize it into exactly one of these tags:
        - INTERESTED (wants more info, says yes, asks for dates)
        - REJECTED (says no, not interested, stop emailing)
        - INQUIRY (asks a specific question but haven't committed)
        - OOO (Out of Office)
        - UNKNOWN (Undetermined)

        Reply Content:
        {reply_content}

        Output ONLY the tag name.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a sentiment analysis specialist."},
                          {"role": "user", "content": prompt}]
            )
            tag = response.choices[0].message.content.strip().upper()
            valid_tags = ['INTERESTED', 'REJECTED', 'INQUIRY', 'OOO', 'UNKNOWN']
            return tag if tag in valid_tags else "UNKNOWN"
        except Exception as e:
            print(f"AI Sentiment Analysis Error: {e}")
            return "UNKNOWN"

    def generate_pitch(self, venue_name, justification, epk_link=None, mix_link=None, traits=None, media_library=None):
        if not self.client:
            return "Hey, we would love to play at your venue!"

        selected_media = mix_link
        if media_library and traits:
            # Use AI to select the best media from the library based on traits
            selected_media = self.select_contextual_media(traits, media_library) or mix_link

        links_context = ""
        if epk_link:
            links_context += f"- Link to our Electronic Press Kit (EPK): {epk_link}\n"
        if selected_media:
            links_context += f"- Our showcase mix/visuals: {selected_media}\n"

        traits_context = ""
        if traits:
            traits_context = f"Additional Context about the venue: {traits}\nUse this to reference their specific setup (e.g., their sound system or unique lighting) to show we've done our homework."

        prompt = f"""
        Write a professional cold email to the booking manager of {venue_name}.
        The reason we like them is: {justification}
        We are a collective of psytrance selectors looking to start a recurring night.
        The tone should be professional and value-driven.

        Please include these links in the pitch:
        {links_context}

        {traits_context}
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

    def select_contextual_media(self, venue_traits, media_library):
        """Uses AI to pick the most relevant media from the library for a given venue."""
        if not self.client or not media_library: return None

        prompt = f"""
        Given the following venue traits:
        {venue_traits}

        Select the most appropriate media item from this library:
        {json.dumps(media_library)}

        Return ONLY the 'url' of the best match.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error selecting contextual media: {e}")
            return None

    def generate_reply_draft(self, venue_name, lead_reply, original_pitch):
        """Generates a professional draft response to a venue's reply."""
        if not self.client:
            return "Thank you for your reply! Let's discuss further."

        prompt = f"""
        Draft a professional and persuasive response to a booking manager at {venue_name}.

        They replied to our initial pitch with:
        "{lead_reply}"

        Our original pitch was:
        "{original_pitch[:1000]}..."

        Goal:
        - If they are interested, suggest a next step (e.g., a short call or meeting).
        - If they have a question (INQUIRY), answer it politely and knowledgeably based on the psytrance collective context.
        - Maintain a friendly, professional, and underground-authentic vibe.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are an expert music booking agent and negotiator."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI Draft Generation Error: {e}")
            return "Thank you for your interest! We'll get back to you shortly."

    def resolve_merge_conflict(self, file_content_with_conflicts):
        if not self.client:
            return None

        prompt = f"""
        Resolve the following git merge conflict.
        The content includes standard git conflict markers (<<<<<<<, =======, >>>>>>>).
        Intelligently merge the changes from both sides to create a functional and correct version of the file.

        Conflict content:
        {file_content_with_conflicts}

        Output ONLY the resolved file content. Do not include any explanation or markdown code blocks.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": "You are a expert software engineer specialized in git and conflict resolution."},
                          {"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"AI Conflict Resolution Error: {e}")
            return None
