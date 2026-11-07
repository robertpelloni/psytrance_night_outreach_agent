import os
from openai import OpenAI
import json


class AIEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.run_total_tokens = 0
        self._alerted_run_budget = False
        self._alerted_day_budget = False

    def _log_usage(self, response):
        """Logs OpenAI token usage to the database."""
        try:
            from src.db_manager import DatabaseManager
            from src.config_manager import ConfigManager

            db = DatabaseManager()
            cfg = ConfigManager()
            usage = response.usage

            self.run_total_tokens += usage.total_tokens

            db.log_ai_usage(
                response.model,
                usage.prompt_tokens,
                usage.completion_tokens,
                usage.total_tokens
            )

            run_budget = cfg.get("openai_token_budget_per_run")
            if run_budget and self.run_total_tokens > run_budget and not self._alerted_run_budget:
                msg = f"Per-run OpenAI token budget exceeded: {self.run_total_tokens} > {run_budget}"
                print(f"WARNING: {msg}")
                db.log_system_event("AI_ENGINE", "WARNING", msg)
                self._alerted_run_budget = True

            day_budget = cfg.get("openai_token_budget_per_day")
            if day_budget:
                today_total = db.get_today_token_usage()
                if today_total > day_budget and not self._alerted_day_budget:
                    msg = f"Per-day OpenAI token budget exceeded: {today_total} > {day_budget}"
                    print(f"WARNING: {msg}")
                    db.log_system_event("AI_ENGINE", "WARNING", msg)
                    self._alerted_day_budget = True

        except Exception as e:
            print(f"Error logging AI usage: {e}")

    def _get_identity_context(self, artist_id=None):
        """Loads artist identity from config or database for use in prompts."""
        try:
            from src.config_manager import ConfigManager
            from src.db_manager import DatabaseManager

            cfg = ConfigManager()
            db = DatabaseManager()

            # Default from config
            artist_name = cfg.get("artist_name") or ""
            collective = cfg.get("collective_name") or ""
            home = cfg.get("home_city") or "Detroit"
            bio = ""
            epk = cfg.get("epk_link") or ""
            mix = cfg.get("mix_link") or ""

            # Overwrite if specific artist_id provided
            if artist_id:
                artist_data = db.get_artist(artist_id)
                if artist_data:
                    artist_name = artist_data['name']
                    bio = artist_data.get('bio', '')
                    epk = artist_data.get('epk_link', '')
                    mix = artist_data.get('mix_link', '')

            parts = []
            if artist_name:
                parts.append(f"Artist/DJ Name: {artist_name}")
            if collective:
                parts.append(f"Collective: {collective}")
            parts.append(f"Home City: {home}")
            if bio:
                parts.append(f"Bio: {bio}")

            return {
                "context": " | ".join(parts) if parts else "",
                "artist_name": artist_name,
                "epk_link": epk,
                "mix_link": mix
            }
        except Exception:
            return {"context": "", "artist_name": "", "epk_link": "", "mix_link": ""}

    def vibe_check(self, venue_name, raw_text, genre="psytrance", rating=None, artist_id=None, notes=None):
        if not self.client:
            print("No OpenAI client configured. Returning default vibe score.")
            return {"vibe_score": 5, "justification": "AI not configured."}

        rating_context = f"Google Rating: {rating}/5" if rating else ""
        identity = self._get_identity_context(artist_id=artist_id)["context"]
        identity_note = f"\nOutreach Identity: {identity}" if identity else ""

        notes_context = ""
        if notes:
            if isinstance(notes, list):
                notes_items = [f"- {n.get('author', 'Curator')}: {n.get('note', '')}" if isinstance(n, dict) else f"- {n}" for n in notes]
                notes_context = "\nCurator Confidential Intelligence & Field Notes:\n" + "\n".join(notes_items) + "\n"
            else:
                notes_context = f"\nCurator Confidential Intelligence & Field Notes:\n{notes}\n"

        prompt = f"""
Analyze this venue description, acoustic specs, and cultural context to determine if it is suitable
for a {genre} night in the Detroit underground music ecosystem.

Venue Name: {venue_name}
{rating_context}
Context/Description: {raw_text}
{notes_context}{identity_note}

Detroit Underground Ecosystem Context:
Detroit is a cornerstone of electronic music culture. Beyond its techno roots, there is a vibrant, selective
psychedelic and experimental underground. Venues that foster authentic underground dance music culture,
support DIY initiatives, or maintain audiophile sound and psychedelic visual setups are prime candidates.
We operate under a strict 6.5 vibe threshold: only venues rated 6.5 or higher qualify for automated outreach.

Scoring Criteria:
- Exceptional Vibe (8.0 - 10.0):
  * Dedicated underground dance music venue, warehouse, or loft space in core corridors (Eastern Market, Milwaukee Junction, Corktown, Hamtramck, Southwest).
  * High-fidelity sound reinforcement (Funktion-One, Void Acoustics, Danley, d&b audiotechnik, L-Acoustics).
  * History of hosting underground techno, trance, psytrance, ambient, or modular synthesizer showcases.
  * Robust visual production (projection mapping, lasers, psychedelic tapestry/UV art, haze/lighting control).
  * Direct resonance with our artist/collective branding and sound aesthetic.
- Qualified & Receptive Vibe (6.5 - 7.9):
  * Eclectic arts space, industrial DIY room, or indie nightclub with an adventurous programming policy.
  * Quality audio setup, dark dance floor aesthetic, and openness to community-driven promotions.
  * May require providing supplemental visual production or sound reinforcement.
- Borderline / High Friction (4.0 - 6.4):
  * Multi-format bar or rock club occasionally doing electronic events, but lacking immersive audio/visual ethos.
  * Corporate promoter restrictions or restrictive sound limits.
- Incompatible (1.0 - 3.9):
  * Top-40/commercial EDM bottle-service clubs, sports lounges, acoustic coffeehouses, or banquets.

Output JSON format:
{{
  "vibe_score": (1.0 to 10.0, decimal allowed e.g. 6.5, 7.5, 8.5),
  "justification": "Detailed explanation incorporating acoustic traits, corridor location, and artist alignment"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a music culture expert specializing in the Detroit underground electronic scene.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return (
                json.loads(content)
                if content
                else {"vibe_score": 0, "justification": "Empty AI response"}
            )
        except Exception as e:
            print(f"AI Error: {e}")
            return {"vibe_score": 0, "justification": f"Error: {e}"}

    def generate_follow_up(self, venue_name, original_pitch, genre="psytrance", artist_id=None, vibe_score=None, threshold=None, is_dm=False):
        if not self.client:
            return f"Just following up on our previous email regarding a {genre} night!"
        identity = self._get_identity_context(artist_id=artist_id)["context"]
        identity_note = f"\nOur identity: {identity}" if identity else ""
        vibe_context = ""
        if vibe_score is not None and threshold is not None:
            if vibe_score >= threshold + 2:
                vibe_context = "This venue is a perfect fit for our vibe! Be enthusiastic and reference how perfectly our sound matches their aesthetic."
            elif vibe_score >= threshold:
                vibe_context = "This venue is a solid match. Be polite and professional."
            else:
                vibe_context = "This venue is a bit of a stretch, but we still want to try. Keep it casual and low-pressure."

        format_instruction = ""
        if is_dm:
            format_instruction = "FORMAT THIS AS A SHORT INSTAGRAM/FACEBOOK DM. Be casual, punchy, and drop formal email salutations."

        prompt = f"""
Write a short, polite follow-up message to a booking manager at {venue_name}.
We previously sent them a pitch for a {genre} residency in the Detroit area.
{identity_note}
Original Pitch context: {original_pitch[:500]}...

The follow-up should be brief, friendly, and just checking if they had a chance
to see our proposal. Reference the Detroit scene if it feels natural.
{vibe_context}
{format_instruction}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional booking agent in the Detroit electronic music scene.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return content if content else "Just checking back on my previous email!"
        except Exception as e:
            print(f"AI Error: {e}")
            return "Just checking back on my previous email!"

    def extract_venue_traits(self, raw_text):
        """Parses venue description for technical and atmospheric traits."""
        if not self.client or not raw_text:
            return "{}"
        prompt = f"""
Analyze the following text about a music venue and extract key traits in JSON format.
Focus on:
1. sound_system: Mentioned brands or quality (e.g., 'Funktion-One', 'Void', 'd&b audiotechnik').
2. lighting: Notable features (e.g., 'projection mapping', 'lasers', 'UV art').
3. atmosphere: Keywords (e.g., 'intimate', 'industrial', 'warehouse', 'outdoor', 'DIY').
4. music_policy: Primary genres mentioned.
5. detroit_relevance: Any Detroit-specific signals (e.g., 'techno heritage', 'Motor City', 'underground').
6. venue_type: Categorize as 'club', 'bar', 'warehouse', 'art_space', 'diy', or 'lounge'.
7. capacity: Estimated capacity as an integer if mentioned, otherwise null.
8. neighborhood: Detroit neighborhood name if mentioned (e.g., 'Corktown', 'Midtown').

Text: "{raw_text[:2000]}"

Return ONLY valid JSON.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return content if content else "{}"
        except Exception as e:
            print(f"Error extracting traits: {e}")
            return "{}"


    def extract_negotiation_constraints(self, reply_content):
        """
        Parses a venue's reply to extract negotiation vectors like dates, capacity, fees, and vibe concerns.
        Outputs a JSON object.
        """
        if not self.client:
            return {"date_offers": [], "capacity_constraints": "", "fee_ranges": "", "vibe_concerns": ""}

        prompt = f"""
Analyze the following reply from a venue booking manager:
"{reply_content}"

Extract any explicit or implied negotiation constraints and output them strictly as a JSON object with the following keys:
- "date_offers": A list of strings representing specific dates or timeframes they offered.
- "capacity_constraints": Any mention of room capacity, minimum draw expectations, or ticketing structure.
- "fee_ranges": Any mention of performance fees, door splits, or guarantees.
- "vibe_concerns": Any concerns they raised about our genre, demographic, or fit for their space.

If a constraint is not mentioned, return an empty string or empty list for that key.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a professional music booking agent parsing venue negotiations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            self._log_usage(response)
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error extracting constraints: {e}")
            return {"date_offers": [], "capacity_constraints": "", "fee_ranges": "", "vibe_concerns": ""}

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

Reply Content: {reply_content}

Output ONLY the tag name.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sentiment analysis specialist.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            tag = content.strip().upper() if content else "UNKNOWN"
            valid_tags = ["INTERESTED", "REJECTED", "INQUIRY", "OOO", "UNKNOWN"]
            return tag if tag in valid_tags else "UNKNOWN"
        except Exception as e:
            print(f"AI Sentiment Analysis Error: {e}")
            return "UNKNOWN"

    def analyze_visual_vibe(self, image_url, genre="psytrance"):
        """Uses GPT-4o vision to analyze a venue image for aesthetic compatibility."""
        if not self.client or not image_url:
            return {
                "visual_vibe_score": 5,
                "visual_description": "No image or AI not configured.",
            }
        prompt = f"""
Analyze this image of a music venue. Does it look like a good fit for a {genre} night
in the Detroit underground scene?

Consider:
- Lighting: lasers, UV, projection mapping, psychedelic visuals
- Décor: psychedelic, industrial, warehouse, DIY, raw concrete
- Space layout: intimate dancefloor, immersive setup, booth positioning
- Detroit signals: exposed brick, industrial aesthetic, raw/unfinished vibe

Output JSON format:
{{
  "visual_vibe_score": (1-10),
  "visual_description": "Concise summary of the aesthetic features found in the image, with Detroit scene context."
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}},
                        ],
                    }
                ],
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return (
                json.loads(content)
                if content
                else {"visual_vibe_score": 0, "visual_description": "Empty AI response"}
            )
        except Exception as e:
            print(f"AI Vision Error: {e}")
            return {
                "visual_vibe_score": 0,
                "visual_description": f"Error analyzing image: {e}",
            }

    def generate_pitch(
        self,
        venue_name,
        justification,
        epk_link=None,
        mix_link=None,
        traits=None,
        media_library=None,
        genre="psytrance",
        variant="Professional",
        artist_id=None,
        is_dm=False,
        notes=None,
    ):
        if not self.client:
            return "Hey, we would love to play at your venue!"

        id_data = self._get_identity_context(artist_id=artist_id)
        identity = id_data["context"]

        # Use artist-specific links if provided
        final_epk = epk_link or id_data["epk_link"]
        final_mix = mix_link or id_data["mix_link"]

        selected_media = final_mix
        if media_library and traits:
            selected_media = (
                self.select_contextual_media(traits, media_library) or final_mix
            )

        links_context = ""
        if final_epk:
            links_context += f"- Link to our Electronic Press Kit (EPK): {final_epk}\n"
        if selected_media:
            links_context += f"- Our showcase mix/visuals: {selected_media}\n"

        traits_context = ""
        if traits:
            traits_context = f"Deeply integrate these venue traits into the pitch to show authentic engagement:\n{traits}"

        notes_context = ""
        if notes:
            if isinstance(notes, list):
                notes_items = [f"- {n.get('author', 'Curator')}: {n.get('note', '')}" if isinstance(n, dict) else f"- {n}" for n in notes]
                notes_context = "\nCurator Confidential Intelligence & Field Notes (incorporate relevant nuances):\n" + "\n".join(notes_items) + "\n"
            else:
                notes_context = f"\nCurator Confidential Intelligence & Field Notes (incorporate relevant nuances):\n{notes}\n"

        if identity:
            identity_context = f"Our identity: {identity}\n"
        else:
            identity_context = f"We are a Detroit-based {genre} DJ/selector.\n"

        format_instruction = ""
        if is_dm:
            format_instruction = "- FORMAT THIS AS AN INSTAGRAM/FACEBOOK DM. IT MUST BE VERY SHORT, PUNCHY, AND CASUAL. No formal salutations like 'Dear Booking Manager'.\n"

        variant_prompts = {
            "Professional": (
                "The tone should be highly professional, business-oriented, and value-driven. "
                "Emphasize the value proposition: drawing the Detroit psychedelic community, "
                "bringing our audience, and offering something unique to their programming."
            ),
            "Underground": (
                "The tone should be authentic, underground-focused, and slightly more casual, "
                "emphasizing subculture and community. Reference the Detroit underground legacy. "
                "Speak as one member of the scene to another. Keep it real."
            ),
            "Technical": (
                "The tone should focus heavily on technical specs, sound quality, and production value. "
                "Speak 'gear-talk' to their production manager. Mention our commitment to "
                "high-fidelity sound and immersive visual setups."
            ),
        }
        tone_instruction = variant_prompts.get(variant, variant_prompts["Professional"])

        prompt = f"""
Write a bespoke cold email pitch to the booking manager of {venue_name}.

Justification for outreach: {justification}

{identity_context}
Our project: We're looking to start a recurring {genre} night/residency at venues that
align with the psychedelic underground. Detroit has a rich electronic music tradition, and
we believe the city is ready for a dedicated psytrance experience — from forest psy to
dark progressive to full-power nighttime sets.

{tone_instruction}

Please include these links:
{links_context}
{traits_context}
{notes_context}

Key pitch elements:
- Position this as filling a gap: Detroit has world-class techno but very few regular psytrance events.
- Emphasize we understand the venue's identity and are not just mass-emailing.
- Suggest a low-risk first step (one-off night, weeknight, or early slot on an existing event).
- Keep it concise — booking managers are busy.
{format_instruction}
- If the venue is in Hamtramck/Ferndale, mention the suburb's growing creative scene.
- If the venue is in Detroit proper, acknowledge the city's electronic music heritage.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert music booking agent specializing in electronic music subcultures and the Detroit scene.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return content if content else "Error generating pitch."
        except Exception as e:
            print(f"AI Error: {e}")
            return "Error generating pitch."

    def select_contextual_media(self, venue_traits, media_library):
        """Uses AI to pick the most relevant media from the library for a given venue."""
        if not self.client or not media_library:
            return None
        prompt = f"""
Given the following venue traits: {venue_traits}

Select the most appropriate media item from this library:
{json.dumps(media_library)}

Return ONLY the 'url' of the best match. If no URL is set, return empty string.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", messages=[{"role": "user", "content": prompt}]
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            result = content.strip() if content else ""
            return result if result and result.startswith("http") else None
        except Exception as e:
            print(f"Error selecting contextual media: {e}")
            return None

    def generate_reply_draft(
        self, venue_name, lead_reply, original_pitch, genre="psytrance", rate_card=None, availability=None, artist_id=None, constraints=None
    ):
        """Generates a professional draft response to a venue's reply."""
        if not self.client:
            return "Thank you for your reply! Let's discuss further."
        identity = self._get_identity_context(artist_id=artist_id)["context"]
        identity_note = f"\nOur identity: {identity}" if identity else ""

        negotiation_context = ""
        if rate_card:
            negotiation_context += f"\n- Our Rate/Fee Info: {rate_card}"
        if availability:
            negotiation_context += f"\n- Our Availability Info: {availability}"

        constraints_context = ""
        if constraints:
            import json
            constraints_context = f"\nThe venue explicitly mentioned the following parameters:\n{json.dumps(constraints, indent=2)}\nAddress these points intelligently in the counter-proposal."

        prompt = f"""
Draft a professional and persuasive response to a booking manager at {venue_name}.

They replied to our initial pitch with: "{lead_reply}"

Our original pitch was: "{original_pitch[:1000]}..."
{identity_note}
{negotiation_context}
{constraints_context}

Goal:
- If they are interested, suggest a next step (e.g., a short call, a test night, or meeting at the venue).
- If they have a question (INQUIRY), answer it politely and knowledgeably based on the {genre} context.
- If they ask about rates or availability, use the provided negotiation context to inform your answer.
- Maintain a friendly, professional, and underground-authentic vibe.
- If relevant, reference the Detroit scene and our commitment to building community.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert music booking agent and negotiator in the Detroit underground scene.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return (
                content
                if content
                else "Thank you for your interest! We'll get back to you shortly."
            )
        except Exception as e:
            print(f"AI Draft Generation Error: {e}")
            return "Thank you for your interest! We'll get back to you shortly."

    def resolve_merge_conflict(self, file_content_with_conflicts):
        if not self.client:
            return None
        prompt = f"""
Resolve the following git merge conflict. The content includes standard git conflict
markers (<<<<<<<, =======, >>>>>>>). Intelligently merge the changes from both sides to
create a functional and correct version of the file.

Conflict content: {file_content_with_conflicts}

Output ONLY the resolved file content. Do not include any explanation or markdown code blocks.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a expert software engineer specialized in git and conflict resolution.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            self._log_usage(response)
            content = response.choices[0].message.content
            return content.strip() if content else None
        except Exception as e:
            print(f"AI Conflict Resolution Error: {e}")
            return None
