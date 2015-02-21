#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import earley_parser

class SimpleGrammarTestCase(unittest.TestCase):
    def setUp(self):
        self.grammar = earley_parser.Grammar([
            'S a S b S',
            'S'
        ])
        self.parser = earley_parser.EarleyParser()

    def runTest(self):
        expected = [
            ("abbab", False),
            ("aaababbb", True),
            ("abba", False),
            ("ab", True),
            ("", True)
        ]
        for string, result in expected:
            self.assertEqual(self.parser.parse(string, self.grammar), result)

class ArithmeticsGrammarTestCase(unittest.TestCase):
    def setUp(self):
        self.grammar = earley_parser.Grammar([
            'S S p M',
            'S M',
            'M M m T',
            'M T',
            'T a',
            'T b',
            'T c',
            'T d'
        ])
        self.parser = earley_parser.EarleyParser()

    def runTest(self):
        expected = [
            ("apbmd", True),
            ("apbmcpd", True),
            ("apd", True),
            ("a", True),
            ("apmd", False),
            ("dp", False),
            ("p", False)
        ]
        for string, result in expected:
            self.assertEqual(self.parser.parse(string, self.grammar), result)

if __name__ == '__main__':
    unittest.main()
