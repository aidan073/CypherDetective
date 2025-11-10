from enum import Enum


class LevelGroundTruth(Enum):
    LEVEL_1 = """
    MATCH (s:Suspect)
    WHERE s.verified_alibi = true
    RETURN s.name AS suspect
    """

    LEVEL_2 = """
    MATCH (s:Suspect)-[:WAS_AT]->(l:Location {name: "Victim's Apartment Building"})
    RETURN s.name AS suspect
    """

    LEVEL_3 = """
    MATCH (s:Suspect)-[:WORKS_AT]->(h:Location {name: "Grandview Hotel"})
    RETURN s.name AS suspect
    """

    LEVEL_4 = """
    MATCH (s:Suspect)-[:WORKS_AT]->(h:Location {name: "Grandview Hotel"})
    WHERE s.access_level >= 2
    RETURN s.name AS suspect
    """

    LEVEL_5 = """
    MATCH (s:Suspect)
    WHERE s.hair = "brown" AND s.height >= 6.0
    RETURN s.name AS suspect
    """

    LEVEL_6 = """
    MATCH (s:Suspect)
    WHERE s.blood_type = "O+"
    RETURN s.name AS suspect
    """

    LEVEL_7 = """
    MATCH (v:Victim {name: "John Doe"})<-[:CLOSE_FRIEND_OF]-(s:Suspect)
    RETURN s.name AS suspect
    """

    LEVEL_8 = """
    MATCH (s:Suspect)-[r:DEPOSITED_IN]->(:Bank)
    WITH s, SUM(r.amount) AS total
    WHERE total = 475500
    RETURN s.name AS suspect
    """
