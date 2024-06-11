import unittest

from unittest.mock import patch

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean

from hive_agent.tools.agent_db.schema import get_db_schemas


class TestGetDBSchemas(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()

        self.table = Table(
            "users",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50), nullable=False),
            Column("email", String(100), nullable=True),
            Column("is_active", Boolean, nullable=False, default=True),
        )
        metadata.create_all(self.engine)

    def tearDown(self):
        self.engine.dispose()

    @patch("hive_agent.tools.agent_db.schema.create_engine")
    def test_get_db_schemas(self, mock_create_engine):
        mock_create_engine.return_value = self.engine

        schemas = get_db_schemas("sqlite:///:memory:")

        expected_schema = [
            {"name": "id", "type": "INTEGER", "primary_key": True, "nullable": False},
            {
                "name": "name",
                "type": "VARCHAR(50)",
                "primary_key": False,
                "nullable": False,
            },
            {
                "name": "email",
                "type": "VARCHAR(100)",
                "primary_key": False,
                "nullable": True,
            },
            {
                "name": "is_active",
                "type": "BOOLEAN",
                "primary_key": False,
                "nullable": False,
            },
        ]

        self.assertIn("users", schemas)
        self.assertListEqual(schemas["users"], expected_schema)

    def test_empty_database(self):
        schemas = get_db_schemas("sqlite:///:memory:")
        self.assertEqual(schemas, {})
