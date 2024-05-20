import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.exc import ArgumentError

from llama_index.core.query_engine import NLSQLTableQueryEngine

from hive_agent.tools.agent_db.nl_query import text_2_sql

load_dotenv = MagicMock()

OpenAI = MagicMock()


class TestText2SQL(unittest.TestCase):
    def setUp(self):
        self.db_url = 'sqlite:///:memory:'
        self.engine = create_engine(self.db_url)
        self.connection = self.engine.connect()
        self.metadata = MetaData()

        entries = Table('entries', self.metadata,
                        Column('id', Integer, primary_key=True),
                        Column('name', String),
                        Column('age', Integer))
        self.metadata.create_all(self.engine)

        self.connection.execute(entries.insert(), [
            {'name': 'Alice', 'age': 25},
            {'name': 'Bob', 'age': 32},
            {'name': 'Charlie', 'age': 19}
        ])

    def tearDown(self):
        self.connection.close()
        self.engine.dispose()

    @patch('hive_agent.tools.agent_db.nl_query.create_engine')
    @patch.object(NLSQLTableQueryEngine, 'query')
    def test_text_2_sql_success(self, mock_query, mock_create_engine):
        mock_create_engine.return_value = self.engine
        mock_query.return_value.response = "Mock LLM response"

        prompt = "What are the names of people in the entries table?"
        response = text_2_sql(self.db_url, prompt)
        self.assertEqual(response, "Mock LLM response")

        prompt = "What are the names of people older than 20 in the entries table?"
        response = text_2_sql(self.db_url, prompt)
        self.assertEqual(response, "Mock LLM response")

        prompt = "What are the ages of people in the entries table?"
        response = text_2_sql(self.db_url, prompt, tables=["entries"])
        self.assertEqual(response, "Mock LLM response")

    @patch('hive_agent.tools.agent_db.nl_query.create_engine')
    def test_invalid_url(self, mock_create_engine):
        mock_create_engine.side_effect = ArgumentError("Invalid URL")

        with self.assertRaises(ArgumentError) as context:
            text_2_sql('invalid_url', "What are the names of people in the entries table?")

        self.assertTrue('Invalid URL' in str(context.exception))

    @patch('hive_agent.tools.agent_db.nl_query.create_engine')
    def test_nonexistent_table(self, mock_create_engine):
        mock_create_engine.return_value = self.engine

        with self.assertRaises(ValueError) as context:
            text_2_sql(
                self.db_url,
                "What are the names of people in the non_existent_table?",
                tables=["non_existent_table"]
            )

        self.assertTrue("include_tables {'non_existent_table'} not found in database" in str(context.exception))

    @patch('hive_agent.tools.agent_db.nl_query.create_engine')
    @patch.object(NLSQLTableQueryEngine, 'query')
    def test_invalid_prompt(self, mock_query, mock_create_engine):
        mock_create_engine.return_value = self.engine
        mock_query.side_effect = ValueError("Could not generate SQL query from prompt")

        with self.assertRaises(ValueError) as context:
            text_2_sql(self.db_url, "This is not a valid prompt")

        self.assertTrue('Could not generate SQL query from prompt' in str(context.exception))

    @patch('hive_agent.tools.agent_db.nl_query.create_engine')
    @patch.object(NLSQLTableQueryEngine, 'query')
    def test_malformed_parameters(self, mock_query, mock_create_engine):
        mock_create_engine.return_value = self.engine
        mock_query.side_effect = TypeError("Bad input")

        with self.assertRaises(TypeError) as context:
            text_2_sql(self.db_url, 12345)

        self.assertTrue('Bad input' in str(context.exception))

