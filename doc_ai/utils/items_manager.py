import json
from typing import List


class ItemsManager:
    def __init__(self, file_path: str):
        """
        Initialize the class with the file path where the master list of items is stored.
        If the file does not exist, it will create a new one with an empty list of items.
        """
        self.file_path = file_path
        self._load_items()

    def _load_items(self):
        """
        Load items from the file. If the file does not exist, create it with an empty list.
        """
        try:
            with open(self.file_path, "r") as file:
                self.items = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize an empty list if the file doesn't exist or is corrupted
            self.items = []
            self._save_items()

    def _save_items(self):
        """
        Save the current list of items back to the file.
        """
        with open(self.file_path, "w") as file:
            json.dump(self.items, file, indent=2)

    def get_all_items_str(self) -> str:
        """
        Return all available items as a list.
        """
        return ", ".join(self.items)

    def get_all_items(self) -> List[str]:
        """
        Return all available items as a list.
        """
        return self.items

    def add_items(self, new_items: List[str]):
        """
        Add any missing items from the input list to the master list of items.
        Arguments:
        - new_items: List of items to add to the master list.
        """
        # Add only items that are not already in the master list
        missing_items = [tag for tag in new_items if tag not in self.items]
        if missing_items:
            self.items.extend(missing_items)
            self._save_items()
            print(f"Added new items: {missing_items}")
        else:
            print("No new items to add.")
