"""
Save and load system for CypherDetective game progress
"""

import os
import json
from typing import Dict, Any


SAVE_DIR = ".user_data"
SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")


def ensure_save_dir():
    """Ensure the save directory exists"""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def load_progress() -> Dict[str, Any]:
    """
    Load user progress from save file

    Returns:
        Dictionary containing progress data, or default if file doesn't exist
    """
    ensure_save_dir()

    default_progress = {
        "highest_level_unlocked": 1,  # Level 0 and 1 are unlocked by default
        "levels_completed": [],
        "total_queries_attempted": 0,
        "total_queries_correct": 0,
    }

    if not os.path.exists(SAVE_FILE):
        return default_progress

    try:
        with open(SAVE_FILE, "r") as f:
            progress = json.load(f)
            # Ensure all required keys exist
            for key in default_progress:
                if key not in progress:
                    progress[key] = default_progress[key]
            return progress
    except Exception as e:
        print(f"Error loading progress: {e}")
        return default_progress


def save_progress(progress: Dict[str, Any]):
    """
    Save user progress to file

    Args:
        progress: Dictionary containing progress data
    """
    ensure_save_dir()

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(progress, f, indent=2)
    except Exception as e:
        print(f"Error saving progress: {e}")


def complete_level(level_num: int):
    """Mark a level as completed and unlock the next one"""
    progress = load_progress()

    if level_num not in progress["levels_completed"]:
        progress["levels_completed"].append(level_num)

    # Unlock next level
    if level_num >= progress["highest_level_unlocked"]:
        next_level = level_num + 1
        progress["highest_level_unlocked"] = next_level

    save_progress(progress)


def is_level_unlocked(level_num: int) -> bool:
    """Check if a level is unlocked"""
    # Level 0 and 1 are always unlocked
    if level_num == 0 or level_num == 1:
        return True
    progress = load_progress()
    return level_num <= progress["highest_level_unlocked"]


def get_highest_unlocked_level() -> int:
    """Get the highest unlocked level number"""
    progress = load_progress()
    return progress["highest_level_unlocked"]
