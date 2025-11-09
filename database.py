"""
Neo4j database connection and query execution module for CypherDetective
"""
from neo4j import GraphDatabase
import os


class DatabaseConnection:
    """Manages connection to Neo4j database"""
    
    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize database connection
        
        Args:
            uri: Neo4j URI (defaults to Aura connection)
            user: Database username (defaults to 'detective')
            password: Database password (defaults to '073')
        
        Note: Set NEO4J_URI environment variable or provide URI directly.
        Format: neo4j+s://<instance-id>.databases.neo4j.io
        """
        # Try to get from environment variables first, then use defaults
        self.uri = uri or os.getenv("NEO4J_URI", "")
        self.user = user or os.getenv("NEO4J_USER", "detective")
        self.password = password or os.getenv("NEO4J_PASSWORD", "073")
        
        if not self.uri:
            raise ValueError(
                "Neo4j URI not provided. Please set NEO4J_URI environment variable.\n"
                "Example: export NEO4J_URI='neo4j+s://your-instance-id.databases.neo4j.io'"
            )
        
        self.driver = None
        self.connect()
    
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connection
            self.driver.verify_connectivity()
            print(f"Connected to Neo4j database as {self.user}")
        except Exception as e:
            print(f"Error connecting to Neo4j: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query, parameters=None):
        """
        Execute a read-only Cypher query
        
        Args:
            query: Cypher query string
            parameters: Optional query parameters
            
        Returns:
            List of records from the query result
        """
        if not self.driver:
            raise Exception("Database not connected")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                records = [record.data() for record in result]
                return records
        except Exception as e:
            raise Exception(f"Query execution error: {str(e)}")
    
    def validate_query(self, query):
        """
        Validate that a query is read-only (no write operations)
        
        Args:
            query: Cypher query string
            
        Returns:
            bool: True if query appears to be read-only
        """
        query_upper = query.upper().strip()
        
        # Check for write operations
        write_keywords = ['CREATE', 'DELETE', 'SET', 'REMOVE', 'MERGE', 'DETACH', 'DROP']
        for keyword in write_keywords:
            if keyword in query_upper:
                return False
        
        return True

