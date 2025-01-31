import json
import logging
from typing import List


class ItemsManager:
    def __init__(self, key: str):
        """
        Initialize the class with the file path where the configuration is stored.
        Validate that the specified key exists and contains a list.
        """
        self.file_path = "configs/config.json"
        self.key = key
        self._load_items()

    def _load_items(self):
        """
        Load items from the file. If the file does not exist or is invalid, create it with an empty list under the key.
        """
        try:
            with open(self.file_path, "r") as file:
                self.config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with an empty dictionary if the file is missing or corrupted
            self.config = {}

        # Ensure the key exists and contains a list
        if self.key not in self.config or not isinstance(self.config[self.key], list):
            self.config[self.key] = []
            self._save_items()

    def _save_items(self):
        """
        Save the updated configuration back to the file.
        """
        with open(self.file_path, "w") as file:
            json.dump(self.config, file, indent=2)

    def get_all_items_str(self) -> str:
        """
        Return all available items as a comma-separated string.
        """
        return ", ".join(self.config[self.key])

    def get_all_items(self) -> List[str]:
        """
        Return all available items as a list.
        """
        return self.config[self.key]

    def add_items(self, new_items: List[str]):
        """
        Add any missing items from the input list to the specified list in the config.
        Arguments:
        - new_items: List of items to add.
        """
        missing_items = [item for item in new_items if item not in self.config[self.key]]
        if missing_items:
            self.config[self.key].extend(missing_items)
            self._save_items()
            return True
        else:
            return False
