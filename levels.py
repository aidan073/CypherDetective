"""
Level definitions for CypherDetective game
Each level contains a lead, expected query pattern, and validation logic
"""
from typing import List, Dict, Callable, Any


class Level:
    """Represents a single level in the game"""
    
    def __init__(self, level_num: int, title: str, lead: str, hint: str = None):
        self.level_num = level_num
        self.title = title
        self.lead = lead  # The clue/lead given to the player
        self.hint = hint  # Optional hint for the player
        self.validator = None  # Function to validate the query result
    
    def set_validator(self, validator_func: Callable[[List[Dict[str, Any]]], bool]):
        """Set the validation function for this level"""
        self.validator = validator_func


# Level definitions
LEVELS = []

# Level 1: Find people with green eyes
def validate_level_1(results):
    """Validate that results contain people with green eyes"""
    if not results:
        return False
    # Check if any result has eye color information
    for record in results:
        if 'eyeColor' in record or 'eyes' in record or 'eye_color' in record:
            eye_value = record.get('eyeColor') or record.get('eyes') or record.get('eye_color', '')
            if 'green' in str(eye_value).lower():
                return True
    return False

level_1 = Level(
    level_num=1,
    title="The Green-Eyed Clue",
    lead="The suspect has green eyes. Find all people with green eyes in the database.",
    hint="Look for nodes with a property related to eye color. Try: MATCH (p:Person) WHERE p.eyeColor = 'green' RETURN p"
)
level_1.set_validator(validate_level_1)
LEVELS.append(level_1)

# Level 2: Find people at a specific location
def validate_level_2(results):
    """Validate that results show people connected to locations"""
    if not results:
        return False
    # Check if results contain location relationships
    for record in results:
        if 'location' in record or 'place' in record or 'at' in record:
            return True
    return False

level_2 = Level(
    level_num=2,
    title="Location Tracking",
    lead="The suspect was seen at the crime scene. Find all people who were at the crime scene location.",
    hint="Look for relationships between Person and Location nodes. Try: MATCH (p:Person)-[r:AT]->(l:Location) WHERE l.name = 'Crime Scene' RETURN p, l"
)
level_2.set_validator(validate_level_2)
LEVELS.append(level_2)

# Level 3: Find people with specific time relationship
def validate_level_3(results):
    """Validate that results include time information"""
    if not results:
        return False
    for record in results:
        if 'time' in record or 'timestamp' in record or 'when' in record:
            return True
    return False

level_3 = Level(
    level_num=3,
    title="Time is of the Essence",
    lead="The suspect was at the location between 8 PM and 10 PM. Find people who were at the crime scene during that time.",
    hint="Check relationship properties for time attributes. Try: MATCH (p:Person)-[r:AT]->(l:Location) WHERE l.name = 'Crime Scene' AND r.time >= '20:00' AND r.time <= '22:00' RETURN p, r.time"
)
level_3.set_validator(validate_level_3)
LEVELS.append(level_3)

# Level 4: Find connections between people
def validate_level_4(results):
    """Validate that results show relationships between people"""
    if not results:
        return False
    for record in results:
        if any(key in record for key in ['knows', 'related', 'connected', 'friend']):
            return True
    return False

level_4 = Level(
    level_num=4,
    title="The Network",
    lead="The suspect knows someone who was at the crime scene. Find all people connected to those who were at the crime scene.",
    hint="Look for relationships between Person nodes. Try: MATCH (p1:Person)-[r:AT]->(l:Location), (p1)-[k:KNOWS]->(p2:Person) WHERE l.name = 'Crime Scene' RETURN p1, p2, k"
)
level_4.set_validator(validate_level_4)
LEVELS.append(level_4)

# Level 5: Complex query - multiple conditions
def validate_level_5(results):
    """Validate complex query results"""
    if not results:
        return False
    # Should have multiple conditions met
    return len(results) > 0

level_5 = Level(
    level_num=5,
    title="The Final Clue",
    lead="The suspect has green eyes, was at the crime scene between 8-10 PM, and knows someone who was there. Find this person.",
    hint="Combine previous queries: MATCH (p:Person) WHERE p.eyeColor = 'green' MATCH (p)-[r:AT]->(l:Location) WHERE l.name = 'Crime Scene' AND r.time >= '20:00' AND r.time <= '22:00' MATCH (p)-[:KNOWS]->(p2:Person)-[:AT]->(l) RETURN DISTINCT p"
)
level_5.set_validator(validate_level_5)
LEVELS.append(level_5)


def get_level(level_num: int) -> Level:
    """Get a level by its number"""
    if 1 <= level_num <= len(LEVELS):
        return LEVELS[level_num - 1]
    return None


def get_total_levels() -> int:
    """Get total number of levels"""
    return len(LEVELS)

