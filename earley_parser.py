#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Python implementation of Earley Parser algorithm.

(C) 2015 by Anton Zhernov <typedef@yandex.ru>

"""

__author__  = "Anton Zhernov <typedef@yandex.ru>"
__date__    = "$Feb 20, 2015$"
__version__ = "0.2"

import copy
import sys
from optparse import OptionParser

class StringLikeObject:
	def __eq__(self, other):
		return str(self) == str(other)

	def __hash__(self):
		return hash(str(self))

class Symbol(StringLikeObject):
	EMPTY_STRING_TERMINAL = "epsilon"
	MAIN_NONTERMINAL = "main"
		
	def __init__(self, name):
		self.name = name
		assert self.name
	
	def __str__(self):
		return self.name

	def isTerminal(self):
		return self.name[0].islower() or self.isEmptyStringTerminal()

	def isEmptyStringTerminal(self):
		return self.name == Symbol.EMPTY_STRING_TERMINAL

	@staticmethod
	def emptyStringTerminal():
		return Symbol(Symbol.EMPTY_STRING_TERMINAL)

	@staticmethod
	def mainNonTerminal():
		return Symbol(Symbol.MAIN_NONTERMINAL)

class Rule(StringLikeObject):
	def __init__(self, line):
		symbols = line.split(' ')
		assert len(symbols)
		self.lhs = Symbol(symbols[0])
		if len(symbols) == 1:
			self.rhs = [Symbol.emptyStringTerminal()]
		else:
			self.rhs = [Symbol(s) for s in symbols[1:]]

	def __str__(self):
		rhs = [s.name for s in self.rhs]
		return self.lhs.name + " -> " + " ".join(rhs)

class State(StringLikeObject):
	def __init__(self, rule, rule_pos, input_pos):
		assert rule_pos >= 0 and rule_pos <= len(rule.rhs)
		assert input_pos >= 0
		self.rule = rule
		self.rule_pos = rule_pos
		self.input_pos = input_pos

	def __str__(self):
		rhs = [str(s) for s in self.rule.rhs]
		rhs.insert(self.rule_pos, "*")
		return self.rule.lhs.name + " -> " + \
			" ".join(rhs) + " (" + str(self.input_pos) + ")"

	def isIncomplete(self):
		return self.rule_pos < len(self.rule.rhs)

	def getNext(self):
		return self.rule.rhs[self.rule_pos]

	def getScanned(self):
		return State(self.rule, self.rule_pos + 1, self.input_pos)

class Grammar:
	def __init__(self, stringRules):
		self.rules = [Rule(r) for r in stringRules]
		assert len(self.rules)
		self.rules.append(self.fakeStartRule())

	def fakeStartRule(self):
		return Rule(Symbol.mainNonTerminal().name + " " + self.rules[0].lhs.name)

	def getDerivedFrom(self, non_terminal):
		return [p for p in self.rules if p.lhs == non_terminal]

class SingleUseSet(set):
	def __init__(self):
		set.__init__(self)
		self.used = set()

	def add(self, item):
		if item not in self.used:
			set.add(self, item)
			self.used.add(item)

class EarleyParser:
	def parse(self, word, grammar, debug=False):
		self.chart = [SingleUseSet() for i in range(1 + len(word))]
		self.chart[0].add(State(grammar.fakeStartRule(), 0, 0))

		for i in range(1 + len(word)):
			while self.chart[i]:
				state = self.chart[i].pop()
				if state.isIncomplete():
					if state.getNext().isTerminal():
						self.scan(state, i, word)
					else:
						self.predict(state, grammar, i)
				else:
					self.complete(state, i)

		if debug:
			for i, states in enumerate(self.chart):
				print i, ":"
				for s in states.used:
					print s
				print "\n"

		return State(grammar.fakeStartRule(), 1, 0) in self.chart[len(word)].used

	def scan(self, state, i, word):
		if state.getNext().isEmptyStringTerminal():
			self.chart[i].add(state.getScanned())
		elif i < len(word) and state.getNext().name == word[i]:
			self.chart[i + 1].add(state.getScanned())

	def predict(self, state, grammar, i):
		for d in grammar.getDerivedFrom(state.getNext()):
			self.chart[i].add(State(d, 0, i))

	def complete(self, state, i):
		completed = [p.getScanned() for p in self.chart[state.input_pos].used
			if p.isIncomplete() and p.getNext() == state.rule.lhs]
		for p in completed:
			self.chart[i].add(p)

def main(options, args):
	grammar = Grammar([line.strip() for line in open(options.grammar_file)])
	for line in sys.stdin:
		parser = EarleyParser()
		print "YES" if parser.parse(line.strip(), grammar, options.debug) else "NO"

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option("-g", "--grammar", dest="grammar_file",
			help="file with grammar")
	parser.add_option("-d", "--debug",
			action="store_true", dest="debug", default=False,
			help="print all states to stdout")
	(options, args) = parser.parse_args()
	main(options, args)
