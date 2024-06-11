import toml
import os
import logging


class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        """Loads the configuration file."""
        if self.config_path.startswith("C:"):
            self.config_path = self.config_path[2:]
        if "\\" in self.config_path:
            self.config_path.replace("\\", "/")
        self.config_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.config_path
        )
        return toml.load(self.config_path)

    def get(self, section, key, default=None):
        """Gets a value from the configuration."""
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Sets a value in the configuration."""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()

    def save_config(self):
        """Saves the current configuration state to disk."""
        config_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), self.config_path
        )
        with open(config_path, "w") as f:
            toml.dump(self.config, f)

    def get_log_level(self):
        HIVE_AGENT_LOG_LEVEL = os.getenv("HIVE_AGENT_LOG_LEVEL", "INFO").upper()
        return getattr(logging, HIVE_AGENT_LOG_LEVEL, logging.INFO)
