"""
Neo4j database connection and query execution module for CypherDetective
"""

from src.enums.game_states import GamePlayState
from src.save_handler.save_system import complete_level

from neo4j import GraphDatabase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.states.gameplay import GameplayState


class DatabaseConnection:
    """Manages connection to Neo4j database"""

    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize database connection

        Args:
            uri: Neo4j URI (defaults to Aura connection)
            user: Database username (defaults to 'detective')
            password: Database password (defaults to 'detective073')
        """
        # Get db values from environment variables or use defaults
        self.uri = "neo4j+s://2de166ea.databases.neo4j.io"
        self.user = "detective"
        self.password = "detective073"

        self.driver = None
        self.connect()

    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
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

    def execute_user_query(self, state: "GameplayState"):
        """
        Execute the player's Cypher query with validation and level completion logic

        Args:
            state: GameplayState instance to update with results
        """

        current_query = state.query_input.get_text()
        current_level = state.game.current_level

        if not current_query.strip():
            state.error_message = "Please enter a query."
            state.sub_state = GamePlayState.QUERY_RESULT
            return

        try:
            # Execute query
            user_results = self.execute_query(current_query)
            ground_truth_results = self.execute_query(current_level.ground_truth_query)
            print(f"User results: {user_results}")
            print(f"\nGround truth results: {ground_truth_results}")

            # print(f"User results: {user_results}")
            # print(f"Ground truth results: {ground_truth_results}")
            user_results_sorted = sorted(user_results, key=lambda d: sorted(d.items()))
            ground_truth_results_sorted = sorted(
                ground_truth_results, key=lambda d: sorted(d.items())
            )
            print("--------------------------------")
            print(f"User results sorted: {user_results_sorted}")
            print(f"\nGround truth results sorted: {ground_truth_results_sorted}")

            # Validate results using level validator
            if user_results_sorted == ground_truth_results_sorted:
                complete_level(current_level.level_num)
                state.success_message = f"Level {current_level.level_num} completed."
                state.sub_state = GamePlayState.QUERY_RESULT
            else:
                state.error_message = "Query executed successfully, but the results don't match the clue. Try again."
                state.sub_state = GamePlayState.QUERY_RESULT

        except Exception as e:
            state.query_result = None
            state.error_message = f"Query error: {str(e)}"
            state.sub_state = GamePlayState.QUERY_RESULT
            return
