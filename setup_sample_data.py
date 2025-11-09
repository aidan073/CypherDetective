"""
Script to populate Neo4j database with sample data for CypherDetective game
Run this script once to set up the database with sample crime data.
"""
from database import DatabaseConnection
import os


def create_sample_data(db: DatabaseConnection):
    """Create sample data for the game"""
    
    # Note: This script requires write access to the database
    # You may need to use a different user with write permissions
    
    queries = [
        # Clear existing data (optional - be careful!)
        # "MATCH (n) DETACH DELETE n",
        
        # Create people with different eye colors
        """
        CREATE (alice:Person {name: 'Alice', eyeColor: 'green', age: 32})
        CREATE (bob:Person {name: 'Bob', eyeColor: 'blue', age: 28})
        CREATE (charlie:Person {name: 'Charlie', eyeColor: 'green', age: 45})
        CREATE (diana:Person {name: 'Diana', eyeColor: 'brown', age: 35})
        CREATE (eve:Person {name: 'Eve', eyeColor: 'green', age: 29})
        """,
        
        # Create locations
        """
        CREATE (crimeScene:Location {name: 'Crime Scene', address: '123 Main St'})
        CREATE (office:Location {name: 'Office', address: '456 Business Ave'})
        CREATE (home:Location {name: 'Home', address: '789 Residential Rd'})
        """,
        
        # Create relationships - people at locations with times
        """
        MATCH (alice:Person {name: 'Alice'}), (crimeScene:Location {name: 'Crime Scene'})
        CREATE (alice)-[:AT {time: '21:00', date: '2024-01-15'}]->(crimeScene)
        """,
        
        """
        MATCH (bob:Person {name: 'Bob'}), (office:Location {name: 'Office'})
        CREATE (bob)-[:AT {time: '19:00', date: '2024-01-15'}]->(office)
        """,
        
        """
        MATCH (charlie:Person {name: 'Charlie'}), (crimeScene:Location {name: 'Crime Scene'})
        CREATE (charlie)-[:AT {time: '20:30', date: '2024-01-15'}]->(crimeScene)
        """,
        
        """
        MATCH (diana:Person {name: 'Diana'}), (home:Location {name: 'Home'})
        CREATE (diana)-[:AT {time: '22:00', date: '2024-01-15'}]->(home)
        """,
        
        """
        MATCH (eve:Person {name: 'Eve'}), (crimeScene:Location {name: 'Crime Scene'})
        CREATE (eve)-[:AT {time: '21:15', date: '2024-01-15'}]->(crimeScene)
        """,
        
        # Create KNOWS relationships
        """
        MATCH (alice:Person {name: 'Alice'}), (charlie:Person {name: 'Charlie'})
        CREATE (alice)-[:KNOWS {since: '2020'}]->(charlie)
        """,
        
        """
        MATCH (charlie:Person {name: 'Charlie'}), (eve:Person {name: 'Eve'})
        CREATE (charlie)-[:KNOWS {since: '2018'}]->(eve)
        """,
        
        """
        MATCH (bob:Person {name: 'Bob'}), (diana:Person {name: 'Diana'})
        CREATE (bob)-[:KNOWS {since: '2021'}]->(diana)
        """,
    ]
    
    print("Creating sample data...")
    for i, query in enumerate(queries, 1):
        try:
            # Note: These are write queries, so we need to use a session with write access
            # The DatabaseConnection class only supports read queries for safety
            # You'll need to modify this or use a different connection method
            print(f"Executing query {i}/{len(queries)}...")
            # For now, we'll just print the queries
            print(f"Query: {query[:100]}...")
        except Exception as e:
            print(f"Error executing query {i}: {e}")
    
    print("\n" + "="*60)
    print("IMPORTANT: The DatabaseConnection class only supports READ queries.")
    print("To create this data, you need to:")
    print("1. Use Neo4j Browser or another tool with write access")
    print("2. Or modify database.py to allow write operations (not recommended for game)")
    print("3. Or use the Neo4j Python driver directly with write permissions")
    print("="*60)
    print("\nHere are the queries you can run in Neo4j Browser:")
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        print(query.strip())


def main():
    """Main function"""
    print("CypherDetective - Sample Data Setup")
    print("="*60)
    
    # Check if URI is set
    if not os.getenv("NEO4J_URI"):
        print("ERROR: NEO4J_URI environment variable not set.")
        print("Please set it before running this script.")
        return
    
    try:
        # Try to connect (read-only connection)
        db = DatabaseConnection()
        print("Connected to database successfully!")
        print("\nNote: This script will show you the queries to run.")
        print("You'll need to execute them in Neo4j Browser or with write access.")
        print()
        
        create_sample_data(db)
        
        db.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

