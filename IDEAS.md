# IDEAS

## 🎯 Detroit Scene-Building
- **Psytrance Night Registry**: Once we have enough venues, publish a simple page listing "Detroit Psytrance Nights" — becomes a scene hub and SEO magnet.
- **Venue Warmth Map**: Color-code Detroit neighborhoods by how receptive they are to psytrance (based on vibe scores + reply sentiment). Shows where the scene is growing.
- **Circuit Cards**: Generate a printable "Detroit Psytrance Circuit" card for each season — venues, dates, lineup — to hand out at events.
- **Scene Buddy System**: If two artists are both using the agent, share venue intelligence (without sharing contacts) to avoid double-pitching the same venue.

## 🧠 AI & Intelligence
- **Dynamic Mix Tailoring**: Use AI to select a mix snippet that best fits the venue's recent vibe. (Partially implemented — `select_contextual_media` does this from the media library.)
- **Social Media Scraper**: Specifically target Instagram "Stories" to see current venue atmosphere in real-time.
- **Video Analysis**: Extend vision capabilities to analyze venue videos/stories for dynamic atmosphere assessment.
- **Collaborative Filtering**: If one venue rejects, have the AI suggest a "friendlier" venue based on similarity of traits.
- **Agentic Negotiation**: Allow the agent to handle basic follow-up questions (e.g., "What are your rates?"). (Basic drafting implemented v1.1.33.)
- **Scene Sentiment Pulse**: Periodically scan Detroit event forums/Reddit/Facebook groups for mentions of psytrance demand. Feed this into pitch generation ("the community is asking for this").
- **AI-Generated EPK**: If the user doesn't have an EPK, have AI generate a simple one-page EPK from the artist name, bio, and mix links.

## 🗺️ Geographic & Tour
- **Geographic Mapping**: Visualize all leads on a map with vibe-score heatmaps. (Implemented v1.1.22.)
- **Real-time Map Filtering**: Add time-based or status-based filters to the map view. (Implemented v1.1.23.)
- **Automated Tour Routing**: Use AI to optimize travel paths between highly-rated venues for multi-city tours. (Implemented v1.1.23.)
- **Tour Calendar View**: Instead of just the map, add a calendar view of potential tour dates across clustered venues.
- **Weather-Aware Tour Planning**: Factor in seasonal weather for outdoor vs. indoor venue preference.
- **Regional Scene Network**: Map connections between Detroit, Chicago, and Toronto psytrance communities for tour routing.

## 📣 Outreach & Pitching
- **Outreach A/B Testing**: Automate the testing of different pitch tones and media selections to maximize conversion. (Partially implemented — epsilon-greedy variant selection.)
- **Creative Visuals Pitch**: Include a gallery or link to projection mapping visuals in the pitch.
- **Multi-Genre Expansion**: Easily pivot the agent to techno, house, or ambient by changing the vibe prompts. (Implemented v1.1.35.)
- **Instagram DM Automation**: For venues with only IG handles, explore semi-automated DM sending (with extreme caution for ToS compliance).
- **Venue Warm Introduction**: If the agent finds that Venue A and Venue B are connected (same owner, same promoter network), use the relationship for a warm intro.
- **Pitch to Promoters, Not Just Venues**: Some Detroit promoters (e.g., for Movement afterparties) are more relevant than venue bookers for certain nights.

## 🔧 Tooling & Workflow
- **Mobile Dashboard**: Responsive or PWA version of the HITL dashboard for reviewing leads on your phone.
- **Voice Note Pitches**: For venues that prefer personal connection, generate a script for a short voice note or phone call.
- **Calendar Integration**: Sync booked dates with Google Calendar automatically.
- **Contract Generator**: Once a venue says yes, auto-generate a simple performance agreement.
- **Payment Tracker**: Track deposits, balances, and payment status for booked events.

## 🌐 Community & Scale
- **Multi-Artist Support**: Allow a collective to manage outreach for multiple DJs with different styles and rate cards.
- **Template Marketplace**: Share and import pitch templates, scraper configs, and search strategies.
- **Scene Reports**: Generate quarterly "State of Detroit Psytrance" reports from aggregated pipeline data.
- **Open Source Venue Database**: Anonymized venue data (no contacts) shared back to the community for scene research.
