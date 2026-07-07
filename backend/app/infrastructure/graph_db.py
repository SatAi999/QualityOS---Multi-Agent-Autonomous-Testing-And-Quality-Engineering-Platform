from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, AsyncGraphDatabase
from app.core.config import settings

class GraphDatabaseManager:
    """
    Neo4j connection and schema manager. Handles code dependency graphs,
    requirement traceabilities, and agent workflow state transition logs.
    """
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        self.driver = None

    def connect(self):
        """Sync driver connection."""
        if not self.driver:
            self.driver = GraphDatabase.driver(self.uri, auth=self.auth)

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Execute a Cypher query synchronously inside a transaction."""
        self.connect()
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

class AsyncGraphDatabaseManager:
    """Async variant of GraphDatabaseManager for FastAPI context."""
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.auth = (settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        self.driver = None

    async def connect(self):
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=self.auth)

    async def close(self):
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        await self.connect()
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            records = []
            async for record in result:
                records.append(record.data())
            return records

# Singletons for application injection
graph_db = GraphDatabaseManager()
async_graph_db = AsyncGraphDatabaseManager()
