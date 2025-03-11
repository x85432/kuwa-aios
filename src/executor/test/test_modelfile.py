import unittest
import logging
from kuwa.executor.modelfile import extract_text_from_quotes


class TestExtractTextFromQuotes(unittest.TestCase):
    test_cases = {
        '"This is a text"': "This is a text",
        '"It\'s a text"': "It's a text",
        '"""multi-line\ntext"""': "multi-line\ntext",
        '"it\'s a text"': "it's a text",
        "'Made with \"love\"'": 'Made with "love"',
        '"""multi-line\ntext\nMade with "love""""': 'multi-line\ntext\nMade with "love"',
        '"""multi-line\ntext\nMade with \'love\'"""': "multi-line\ntext\nMade with 'love'",
        "'He said, \"Hello!\"'": 'He said, "Hello!"',
        "\"She replied, 'Hi there!'\"": "She replied, 'Hi there!'",
        "No quotes here": "No quotes here",
        "Invalid 'syntax'": "Invalid 'syntax'",
        " No quote with spaces  ": "No quote with spaces",
        ' "Quote with space "   ': "Quote with space ",
    }

    def test(self):
        for test_case, correct_result in self.test_cases.items():
            result = extract_text_from_quotes(test_case)
            self.assertEqual(result, correct_result)


if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    unittest.main()
