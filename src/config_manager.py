import json
import os


class ConfigManager:
    def __init__(self, config_path="database/config.json"):
        self.config_path = config_path
        self.default_config = {
            "cities": [
                "Detroit",
                "Hamtramck",
                "Ferndale",
                "Royal Oak",
                "Ann Arbor",
                "Grand Rapids",
                "Chicago",
                "Cleveland",
                "Columbus",
                "Toronto",
            ],
            "target_genres": [
                "psytrance",
                "psychedelic trance",
                "forest psy",
                "dark prog",
                "progressive psy",
                "hi-tech",
            ],
            "epk_link": "",
            "mix_link": "",
            "artist_name": "",
            "collective_name": "",
            "home_city": "Detroit",
            "vibe_threshold": 6,
            "auto_approve_threshold": 9,
            "follow_up_days": 7,
            "max_follow_ups": 2,
            "imap_server": "",
            "imap_user": "",
            "imap_password": "",
            "imap_port": 993,
            "detroit_search_queries": [
                "underground electronic music venue",
                "warehouse venue Detroit",
                "techno club Detroit",
                "psytrance event Detroit",
                "electronic music art space Detroit",
                "afterhours Detroit",
                "DIY venue Detroit",
                "loft party Detroit",
                "industrial venue Detroit",
            ],
            "detroit_neighborhoods": [
                "Midtown Detroit",
                "Downtown Detroit",
                "Corktown Detroit",
                "Southwest Detroit",
                "Eastside Detroit",
                "New Center Detroit",
                "Hamtramck",
                "Ferndale",
            ],
            "media_library": [
                {
                    "name": "Forest Psy DJ Set",
                    "url": "",
                    "tags": ["forest", "underground", "dark", "nighttime"],
                },
                {
                    "name": "Progressive Psy Morning Set",
                    "url": "",
                    "tags": ["outdoor", "progressive", "morning", "chill"],
                },
                {
                    "name": "Dark Prog/Techno Crossover",
                    "url": "",
                    "tags": ["techno", "dark prog", "crossover", "industrial"],
                },
                {
                    "name": "Visual Projection Reel",
                    "url": "",
                    "tags": ["visuals", "lasers", "projections", "psychedelic"],
                },
            ],
        }
        self._ensure_config()

    def _ensure_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self.default_config)

    def load_config(self):
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config

    def save_config(self, config_data):
        try:
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key):
        config = self.load_config()
        return config.get(key, self.default_config.get(key))
