import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from lib import read_words

import unittest
from unittest.mock import mock_open, patch

class TestReadWords(unittest.TestCase):
    def test_read_words(self):
        # Mock content of the 'add_words.txt' file
        mock_file_content = "kanji1\nkanji2\nkanji3\n"
        
        # Use patch to mock open function and provide mock_file_content
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = read_words()
        
        # Expected result after stripping newline characters
        expected_result = ["kanji1", "kanji2", "kanji3"]
        
        # Assert if the function's output matches the expected result
        self.assertEqual(result, expected_result)

# Run the test
if __name__ == '__main__':
    unittest.main()