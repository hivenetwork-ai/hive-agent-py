import os

from dotenv import load_dotenv

from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.openai import OpenAI

from sqlalchemy import create_engine


load_dotenv()

llm = OpenAI(temperature=0.1, model=os.getenv("MODEL", "gpt-3.5-turbo"))


def text_2_sql(db_url: str, prompt: str, tables=None):
    """
    Convert a natural language prompt into an SQL query and execute it against the specified database.

    :param db_url: The database URL connection string.
    :param prompt: The natural language query to convert into SQL.
    :param tables: Optional list of tables to include in the query. Defaults to ["entries"] if not specified.
    :return: The response from the query execution.
    """

    if tables is None:
        tables = ["entries"]

    engine = create_engine(db_url)
    sql_database = SQLDatabase(engine, include_tables=tables)

    query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=["entries"], llm=llm
    )

    answer = query_engine.query(prompt)

    return answer.response
