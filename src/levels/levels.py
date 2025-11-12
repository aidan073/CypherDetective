"""
Level definitions for CypherDetective game
Each level contains a lead, expected query pattern, and validation logic
"""

from src.enums.ground_truths import LevelGroundTruth


class Level:
    """Represents a single level in the game"""

    def __init__(
        self,
        level_num: int,
        title: str,
        lead: str,
        hint: str = None,
        answer: str = None,
    ):
        self.level_num = level_num
        self.title = title
        self.lead = lead  # The clue/lead given to the player
        self.hint = hint  # Optional hint for the player
        self.answer = answer  # Expected answer for the player
        self.ground_truth_query = None  # Query to get the ground truth for this level

    def set_ground_truth_query(self, ground_truth_query: str):
        """Set the ground truth for this level"""
        self.ground_truth_query = ground_truth_query


# Level definitions
LEVELS = []


# Level 1: Verified alibis
level_1 = Level(
    level_num=1,
    title="Verified Alibis",
    lead="Initial interrogations determined that some alibis were verifiable. Find all suspects without verified alibis.",
    hint="Look for suspects with the verified_alibi property set to false.",
    answer="MATCH (s:Suspect) WHERE s.verified_alibi = false RETURN s.name AS suspect",
)
level_1.set_ground_truth_query(LevelGroundTruth.LEVEL_1.value)
LEVELS.append(level_1)


# Level 2: Exclude suspects in victim's building
level_2 = Level(
    level_num=2,
    title="The Bullet's Path",
    lead="The bullet came through the window from somewhere outside. All suspects who were in the victim's building are innocent. Find all suspects who were not at the victim's apartment building.",
    hint="Look for suspects with a WAS_AT relationship to anything but the victim's building.",
    answer='MATCH (s:Suspect) WHERE NOT (s)-[:WAS_AT]->(:Location {name: "Victim\'s Apartment Building"}) RETURN s.name AS suspect',
)
level_2.set_ground_truth_query(LevelGroundTruth.LEVEL_2.value)
LEVELS.append(level_2)


# Level 3: Hotel employees
level_3 = Level(
    level_num=3,
    title="The Rooftop Access",
    lead="The bullet came from the rooftop of the Grandview Hotel. The rooftop door is always locked and can only be accessed by employees. Find all suspects who work at the Grandview Hotel.",
    hint="Look for suspects with a WORKS_AT relationship to the Grandview Hotel.",
    answer='MATCH (s:Suspect)-[:WORKS_AT]->(h:Location {name: "Grandview Hotel"}) RETURN s.name AS suspect',
)
level_3.set_ground_truth_query(LevelGroundTruth.LEVEL_3.value)
LEVELS.append(level_3)


# Level 4: Security level requirement
level_4 = Level(
    level_num=4,
    title="Keycard Access",
    lead="An employee can only get a keycard if they have security level 2 or higher access at the hotel. Find all suspects with access level 2 or higher.",
    hint="Filter hotel employees by access_level property.",
    answer="MATCH (s:Suspect) WHERE s.access_level >= 2 RETURN s.name AS suspect",
)
level_4.set_ground_truth_query(LevelGroundTruth.LEVEL_4.value)
LEVELS.append(level_4)


# Level 5: Physical description
level_5 = Level(
    level_num=5,
    title="The Witness Description",
    lead="A witness saw the suspect climbing the stairs towards the roof. They said the suspect had brown hair and was at least 6 feet tall. Find all suspects matching this description.",
    hint="Filter suspects by hair color and height.",
    answer='MATCH (s:Suspect) WHERE s.hair = "brown" AND s.height >= 6.0 RETURN s.name AS suspect',
)
level_5.set_ground_truth_query(LevelGroundTruth.LEVEL_5.value)
LEVELS.append(level_5)


# Level 6: Blood type evidence
level_6 = Level(
    level_num=6,
    title="Blood Evidence",
    lead="A shard from a broken bottle near the presumed suspect's location had some dried blood. ABO blood testing determined that the blood type was O positive. Find all suspects with O+ blood type.",
    hint="Filter suspects by blood_type property.",
    answer='MATCH (s:Suspect) WHERE s.blood_type = "O+" RETURN s.name AS suspect',
)
level_6.set_ground_truth_query(LevelGroundTruth.LEVEL_6.value)
LEVELS.append(level_6)


# Level 7: Close friend relationship
level_7 = Level(
    level_num=7,
    title="The Murder Weapon",
    lead="The murder weapon was discovered in a nearby river. The serial number showed the last owner as the victim, John Doe. A witness said John Doe mentioned selling the gun to a close friend. Find all suspects who are close friends of John Doe.",
    hint="Look for suspects with a CLOSE_FRIEND_OF relationship to John Doe.",
    answer='MATCH (v:Victim {name: "John Doe"})<-[:CLOSE_FRIEND_OF]-(s:Suspect) RETURN s.name AS suspect',
)
level_7.set_ground_truth_query(LevelGroundTruth.LEVEL_7.value)
LEVELS.append(level_7)


# Level 8: Financial deposits
level_8 = Level(
    level_num=8,
    title="The Money Trail",
    lead="An anonymous tip said the murderer has recent deposits into different banks summing up to exactly $475,500. Find the suspect whose total deposits across all banks equal this amount.",
    hint="Sum deposit amounts using aggregation.",
    answer="MATCH (s:Suspect)-[r:DEPOSITED_IN]->(:Bank) WITH s, SUM(r.amount) AS total WHERE total = 475500 RETURN s.name AS suspect",
)
level_8.set_ground_truth_query(LevelGroundTruth.LEVEL_8.value)
LEVELS.append(level_8)


def get_level(level_num: int) -> Level:
    """Get a level by its number"""
    if 1 <= level_num <= len(LEVELS):
        return LEVELS[level_num - 1]
    return None


def get_total_levels() -> int:
    """Get total number of levels"""
    return len(LEVELS)
