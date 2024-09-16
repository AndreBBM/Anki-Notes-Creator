import unittest
from unittest.mock import patch, MagicMock
import json
import urllib

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from lib import invoke, request


# Unit test class
class TestInvokeFunction(unittest.TestCase):

    @patch('urllib.request.urlopen')
    def test_invoke_success(self, mock_urlopen):
        # Mock a valid response from AnkiConnect
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'result': 'success', 'error': None}).encode('utf-8')
        mock_urlopen.return_value = mock_response

        # Call invoke function and assert the result
        result = invoke('someAction')
        self.assertEqual(result, 'success')

    @patch('urllib.request.urlopen')
    def test_invoke_error_in_response(self, mock_urlopen):
        # Mock a response with an error
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'result': None, 'error': 'Some error occurred'}).encode('utf-8')
        mock_urlopen.return_value = mock_response

        # Call invoke function and assert that an exception is raised
        with self.assertRaises(Exception) as context:
            invoke('someAction')
        
        self.assertEqual(str(context.exception), 'Some error occurred')

    @patch('urllib.request.urlopen')
    def test_invoke_missing_result_field(self, mock_urlopen):
        # This one will never succed because in the current implementation, the unexpected number of fields will be raised first
        # Mock a response missing the 'result' field
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'error': None}).encode('utf-8')
        mock_urlopen.return_value = mock_response

        # Call invoke function and assert that an exception is raised
        with self.assertRaises(Exception) as context:
            invoke('someAction')
        
        self.assertEqual(str(context.exception), 'response is missing required result field')

    @patch('urllib.request.urlopen')
    def test_invoke_unexpected_number_of_fields(self, mock_urlopen):
        # Mock a response with an unexpected number of fields
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({'result': 'success', 'error': None, 'extraField': 'extra'}).encode('utf-8')
        mock_urlopen.return_value = mock_response

        # Call invoke function and assert that an exception is raised
        with self.assertRaises(Exception) as context:
            invoke('someAction')
        
        self.assertEqual(str(context.exception), 'response has an unexpected number of fields')

# Run the tests
if __name__ == '__main__':
    unittest.main()
