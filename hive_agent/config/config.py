import toml
import os
import logging


class Config:
    def __init__(self, config_path):
        self.config_path = self.resolve_path(config_path)
        self.config = self.load_config()

    def resolve_path(self, path):
        """Resolves the path relative to the current working directory."""
        if not os.path.isabs(path):
            return os.path.abspath(os.path.join(os.getcwd(), path))
        return path

    def load_config(self):
        """Loads the configuration file."""
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
        with open(self.config_path, "w") as f:
            toml.dump(self.config, f)
