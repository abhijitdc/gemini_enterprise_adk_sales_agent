import unittest
from unittest.mock import MagicMock, patch
from sales_agent.tools import get_authorized_bigquery_client, execute_sql, get_bigquery_tools, list_tables, get_table_schema

class TestBigQueryTools(unittest.TestCase):

    def test_get_bigquery_tools(self):
        tools = get_bigquery_tools()
        self.assertIsInstance(tools, list)
        self.assertIn(execute_sql, tools)
        self.assertIn(list_tables, tools)
        self.assertIn(get_table_schema, tools)

    @patch('sales_agent.tools.get_authorized_bigquery_client')
    def test_list_tables_success(self, mock_get_client):
        # Mock client and table list
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_table = MagicMock()
        mock_table.table_id = "test_table"
        mock_client.list_tables.return_value = [mock_table]
        
        # Call list_tables
        result = list_tables("test_project.test_dataset", tool_context=MagicMock())
        
        # Verify result
        self.assertIn("Tables in test_project.test_dataset: test_table", result)

    @patch('sales_agent.tools.get_authorized_bigquery_client')
    def test_get_table_schema_success(self, mock_get_client):
        # Mock client and table schema
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_field = MagicMock()
        mock_field.name = "revenue"
        mock_field.field_type = "NUMERIC"
        mock_table = MagicMock()
        mock_table.schema = [mock_field]
        mock_client.get_table.return_value = mock_table
        
        # Call get_table_schema
        result = get_table_schema("test_project.test_dataset.test_table", tool_context=MagicMock())
        
        # Verify result
        self.assertIn("revenue: NUMERIC", result)

    @patch('sales_agent.tools.bigquery.Client')
    @patch('sales_agent.tools.Credentials')
    def test_get_authorized_bigquery_client_with_context(self, mock_credentials, mock_bq_client):
        # Setup context with auth_id
        mock_context = MagicMock()
        mock_context.auth_id = "test-token"
        
        # Call the function
        get_authorized_bigquery_client(mock_context)
        
        # Verify Credentials was called with the token
        mock_credentials.assert_called_once_with(token="test-token")
        
        # Verify BigQuery client was initialized with those credentials
        mock_bq_client.assert_called_once()
        args, kwargs = mock_bq_client.call_args
        self.assertEqual(kwargs['credentials'], mock_credentials.return_value)

    @patch('sales_agent.tools.bigquery.Client')
    def test_get_authorized_bigquery_client_without_context(self, mock_bq_client):
        # Call without context
        get_authorized_bigquery_client(None)
        
        # Verify BigQuery client was initialized without explicit credentials (falling back to ADC)
        mock_bq_client.assert_called_once()
        args, kwargs = mock_bq_client.call_args
        self.assertNotIn('credentials', kwargs)

    @patch('sales_agent.tools.get_authorized_bigquery_client')
    def test_execute_sql_success(self, mock_get_client):
        # Mock client and query results
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_results = [
            {'revenue': 1000, 'region': 'North'},
            {'revenue': 2000, 'region': 'South'}
        ]
        mock_client.query.return_value.result.return_value = mock_results
        
        # Call execute_sql
        result = execute_sql("SELECT * FROM sales", tool_context=MagicMock())
        
        # Verify results
        self.assertIn("'revenue': 1000", result)
        self.assertIn("'region': 'North'", result)
        self.assertIn("'revenue': 2000", result)
        self.assertIn("'region': 'South'", result)

if __name__ == '__main__':
    unittest.main()
