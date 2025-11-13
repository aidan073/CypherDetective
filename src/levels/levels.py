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


# Level 0: Tutorial
level_0 = Level(
    level_num=0,
    title="Tutorial",
    lead="Welcome to CypherDetective. This is a tutorial level to help you get started. Try querying the knowledge graph to find all suspect's names. Just like in all future levels, be sure to return the names of the suspects as 'suspect' (e.g. RETURN s.name AS suspect).",
    hint="Use MATCH to find all nodes with the Suspect label, then RETURN their names.",
    answer="MATCH (s:Suspect) RETURN s.name AS suspect",
)
level_0.set_ground_truth_query(LevelGroundTruth.LEVEL_0.value)
LEVELS.append(level_0)


# Level 1: Verified alibis
level_1 = Level(
    level_num=1,
    title="Alibis",
    lead="Early investigations into the homicide of John Doe have confirmed the alibis of some suspects. These suspects have been marked with 'verified_alibi = true'. Query the knowledge graph for only the names of the suspects who DON'T have a verified alibi.",
    hint="Match and return the names of the suspects where the verified_alibi property is set to false. Make sure to return the suspect's name as 'suspect' (e.g. RETURN s.name AS suspect).",
    answer="MATCH (s:Suspect) WHERE s.verified_alibi = false RETURN s.name AS suspect",
)
level_1.set_ground_truth_query(LevelGroundTruth.LEVEL_1.value)
LEVELS.append(level_1)


# Level 2: Include only suspects at Grandview Hotel
level_2 = Level(
    level_num=2,
    title="The Bullet's Path",
    lead="Investigations have placed the bullet's origin at the rooftop of the Grandview Hotel, so only individuals who were at Grandview Hotel are still suspects. Find the names of all suspects who were at the Grandview Hotel.",
    hint="Get the names of suspects who have a WAS_AT relationship to the Grandview Hotel.",
    answer='MATCH (s:Suspect)-[:WAS_AT]->(:Location {name: "Grandview Hotel"}) RETURN s.name AS suspect',
)
level_2.set_ground_truth_query(LevelGroundTruth.LEVEL_2.value)
LEVELS.append(level_2)


# Level 3: Hotel employees
level_3 = Level(
    level_num=3,
    title="Hotel Employees",
    lead="The Grandview Hotel rooftop door is always locked and can only be accessed by employees. Find the names of all suspects who work at the Grandview Hotel.",
    hint="Get the names of suspects with a WORKS_AT relationship to the Grandview Hotel.",
    answer='MATCH (s:Suspect)-[:WORKS_AT]->(:Location {name: "Grandview Hotel"}) RETURN s.name AS suspect',
)
level_3.set_ground_truth_query(LevelGroundTruth.LEVEL_3.value)
LEVELS.append(level_3)


# Level 4: Security level requirement
level_4 = Level(
    level_num=4,
    title="Keycard Access",
    lead="After discussion with hotel staff, we've learned that an employee can only get a keycard for the rooftop door if they have security level 2 or higher access. Find the names of all suspects with access level 2 or higher.",
    hint="Return the names of all suspects with their access_level property >= 2.",
    answer="MATCH (s:Suspect) WHERE s.access_level >= 2 RETURN s.name AS suspect",
)
level_4.set_ground_truth_query(LevelGroundTruth.LEVEL_4.value)
LEVELS.append(level_4)


# Level 5: Physical description
level_5 = Level(
    level_num=5,
    title="The Witness",
    lead="A witness reported seeing the suspect climb the stairs towards the rooftop. They described the suspect as having brown hair and being at least 6 feet tall. Find the names of all suspects matching this description.",
    hint="Return the names of all suspects where their hair color is 'brown' AND their height is >= 6.0.",
    answer='MATCH (s:Suspect) WHERE s.hair = "brown" AND s.height >= 6.0 RETURN s.name AS suspect',
)
level_5.set_ground_truth_query(LevelGroundTruth.LEVEL_5.value)
LEVELS.append(level_5)


# Level 6: Blood type evidence
level_6 = Level(
    level_num=6,
    title="Blood Evidence",
    lead="A shard of glass from where the bullet was fired had some dried blood on it. ABO blood testing determined that the blood type was O positive. Find the names of all suspects with O+ blood type.",
    hint="Match and return the names of all suspects with blood_type 'O+'.",
    answer='MATCH (s:Suspect) WHERE s.blood_type = "O+" RETURN s.name AS suspect',
)
level_6.set_ground_truth_query(LevelGroundTruth.LEVEL_6.value)
LEVELS.append(level_6)


# Level 7: Close friend relationship
level_7 = Level(
    level_num=7,
    title="The Murder Weapon",
    lead="The murder weapon was discovered in a nearby river. The serial number showed the last owner as John Doe. A witness said John Doe had mentioned selling the gun to a close friend. Find the names of all suspects who were close friends of the victim, John Doe.",
    hint="Get the names of suspects with a CLOSE_FRIEND_OF relationship to the victim, John Doe.",
    answer='MATCH (:Victim {name: "John Doe"})<-[:CLOSE_FRIEND_OF]-(s:Suspect) RETURN s.name AS suspect',
)
level_7.set_ground_truth_query(LevelGroundTruth.LEVEL_7.value)
LEVELS.append(level_7)


# Level 8: Financial deposits
level_8 = Level(
    level_num=8,
    title="The Money Trail",
    lead="An anonymous tip said the murderer has made deposits into different banks summing up to exactly $475,500. Find the name of the suspect whose total deposits across all banks equal this amount.",
    hint="You will need to sum the deposit amounts over all banks for each suspect using the aggregation function SUM(). This will likely require a WITH clause to group by suspect so that the SUM is calculated for each suspect.",
    answer="MATCH (s:Suspect)-[r:DEPOSITED_IN]->(:Bank) WITH s, SUM(r.amount) AS total WHERE total = 475500 RETURN s.name AS suspect",
)
level_8.set_ground_truth_query(LevelGroundTruth.LEVEL_8.value)
LEVELS.append(level_8)


# Level 9: Case Closed
level_9 = Level(
    level_num=9,
    title="Case Closed",
    lead="It seems we've found our guy, good work detective. John Doe's family can finally find some peace knowing that the murderer has been caught. It's been a pleasure working with you. Until next time...\n\n- Officer L. Grant",
    hint="What do you need a hint for? Go get a coffee or something.",
    answer="Not everything is as it seems. Try: 37ff4d2021",
)
level_9.set_ground_truth_query(LevelGroundTruth.LEVEL_9.value)
LEVELS.append(level_9)


def get_level(level_num: int) -> Level:
    """Get a level by its number"""
    if 0 <= level_num < len(LEVELS):
        return LEVELS[level_num]
    return None


def get_total_levels() -> int:
    """Get total number of levels"""
    return len(LEVELS)
