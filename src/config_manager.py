import json
import os

class ConfigManager:
    def __init__(self, config_path='database/config.json'):
        self.config_path = config_path
        self.default_config = {
            "cities": ["Detroit", "Berlin", "London", "Tokyo", "Lisbon"],
            "target_genres": ["psytrance", "underground techno", "progressive psy"],
            "epk_link": "https://your-epk-link.com",
            "mix_link": "https://soundcloud.com/your-mix-link",
            "vibe_threshold": 7
        }
        self._ensure_config()

    def _ensure_config(self):
        if not os.path.exists(self.config_path):
            self.save_config(self.default_config)

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config

    def save_config(self, config_data):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get(self, key):
        config = self.load_config()
        return config.get(key, self.default_config.get(key))
