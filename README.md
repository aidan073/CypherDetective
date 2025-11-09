# CypherDetective

A noir-themed detective game where you solve crimes by writing Cypher queries to explore a Neo4j graph database.

## Overview

CypherDetective is an educational game that teaches Neo4j Cypher query language through an engaging detective story. Each level presents you with a clue, and you must write the correct Cypher query to find the information in the database. As you progress, levels unlock progressively, and your progress is saved automatically.

## Features

- 🎮 Noir detective theme with pygame
- 📊 Neo4j database integration
- 🎯 Progressive level unlocking
- 💾 Automatic save system
- 🔍 Query validation and feedback
- 🎨 Beautiful dark UI with sepia accents

## Requirements

- Python 3.7+
- Neo4j Aura database (or any Neo4j instance)
- pygame
- neo4j Python driver

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Neo4j connection:
   - Get your Neo4j Aura instance URI (format: `neo4j+s://<instance-id>.databases.neo4j.io`)
   - Set environment variables:
     ```bash
     # Windows PowerShell
     $env:NEO4J_URI="neo4j+s://your-instance-id.databases.neo4j.io"
     $env:NEO4J_USER="detective"
     $env:NEO4J_PASSWORD="073"
     
     # Linux/Mac
     export NEO4J_URI="neo4j+s://your-instance-id.databases.neo4j.io"
     export NEO4J_USER="detective"
     export NEO4J_PASSWORD="073"
     ```
   
   Alternatively, you can edit `database.py` directly to set the URI, username, and password.

## Running the Game

```bash
python main.py
```

## Game Controls

- **Menu Screen:**
  - `P` or `ENTER` - Start playing
  - `ESC` - Quit

- **Level Select:**
  - `1-5` - Select level (if unlocked)
  - `ESC` - Return to menu

- **Gameplay:**
  - Type your Cypher query
  - `ENTER` - Execute query
  - `ESC` - Return to level select
  - `TAB` - Insert spaces for indentation

## Game Structure

### Levels

Each level presents a new clue about the crime. You must write a Cypher query that:
1. Executes successfully
2. Returns results matching the clue
3. Uses only read operations (MATCH, RETURN, WHERE, etc.)

### Progress Saving

Your progress is automatically saved to `.user_data/progress.json`. This includes:
- Highest unlocked level
- Completed levels
- Statistics (queries attempted, correct, etc.)

## Database Schema

The game expects a Neo4j database with nodes and relationships such as:

- **Nodes:**
  - `Person` - People in the database
  - `Location` - Places (e.g., "Crime Scene")
  
- **Properties:**
  - `Person.eyeColor` - Eye color of a person
  - `Person.name` - Name of person
  
- **Relationships:**
  - `AT` - Person at Location (with `time` property)
  - `KNOWS` - Person knows Person

**Note:** You'll need to populate your database with sample data matching the expected schema for the levels to work properly.

## Example Queries

### Level 1: Find people with green eyes
```cypher
MATCH (p:Person)
WHERE p.eyeColor = 'green'
RETURN p
```

### Level 2: Find people at crime scene
```cypher
MATCH (p:Person)-[r:AT]->(l:Location)
WHERE l.name = 'Crime Scene'
RETURN p, l
```

### Level 3: Find people at location during specific time
```cypher
MATCH (p:Person)-[r:AT]->(l:Location)
WHERE l.name = 'Crime Scene' 
  AND r.time >= '20:00' 
  AND r.time <= '22:00'
RETURN p, r.time
```

## Customization

### Adding New Levels

Edit `levels.py` to add new level definitions:

```python
def validate_level_6(results):
    # Your validation logic
    return True

level_6 = Level(
    level_num=6,
    title="Your Level Title",
    lead="Your clue text",
    hint="Optional hint"
)
level_6.set_validator(validate_level_6)
LEVELS.append(level_6)
```

### Modifying Colors/Theme

Edit the `COLORS` dictionary in `main.py` to customize the noir theme.

## Troubleshooting

- **Database Connection Error:** Make sure your Neo4j URI, username, and password are correct. Check that your Aura instance is running.
- **Query Not Working:** Ensure your database schema matches the expected structure. Check the example queries above.
- **Levels Not Unlocking:** Check `.user_data/progress.json` to verify your progress is being saved.

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
