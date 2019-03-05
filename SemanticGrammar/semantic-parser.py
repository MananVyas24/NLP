#!/usr/bin/env python

import itertools, sys

from nltk.parse import RecursiveDescentParser, ShiftReduceParser, ViterbiParser
from nltk import Nonterminal, nonterminals, Production, CFG, PCFG
from nltk.grammar import is_terminal

##############################################################################


def isFloatNum(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def parseNums(tokens):
    return ["*VAR-NUM*" if (tkn.isdigit() or isFloatNum(tkn)) else tkn
            for tkn in tokens]


def is_terminal_production(p):
    return all([type(n) == unicode for n in p._rhs])


def extract_words_from_grammar(grammar):
    categories = set()
    words = set()
    for p in grammar.productions():
        for x in p._rhs:
            if type(x) == unicode or type(x) == str:
                words.add(x)
    return words


def identify_unknown_words(sentence, grammar):
    unknown_words = set()
    ws = extract_words_from_grammar(grammar)
    for word in sentence:
        if word not in ws:
            unknown_words.add(word)
    return list(unknown_words)


def get_open_categories():
    return ['VAR_ACTIVITY', 'VAR_COMPLIANCE', 'VAR_DIRECTION',
            'VAR_EVENT', 'VAR_ITEM', 'VAR_STATUS', 'ADJ',
            'VAR_PHASE', 'ADVERB']


def create_lexical_production(category, word):
    return Production(Nonterminal(category), [word])


def add_terminal_production_to_grammar(production, grammar):
    return CFG(start=grammar._start,
               productions=grammar._productions+[production])


def read_grammar_from_file(filename):
    with open(filename, 'r') as f_grammar:
        return CFG.fromstring('\n'.join([line.strip()
                              for line in f_grammar]))


def read_sentences_from_file(filename):
    with open(filename, 'r') as f_sents:
        return [line.strip() for line in f_sents]


def parse_tokens(parser, tokens, print_trees=True, max_num_parses=2):
    trees = list(itertools.islice(parser.parse(tokens), 2))
    if print_trees:
        for j, tree in enumerate(trees):
            print "Parse #%d/%d:"%(j+1, len(trees))
            print tree
    return trees


def process_sentences(sentences, grammar):
    parser = RecursiveDescentParser(grammar)
    """
    NOTE: While this demo uses a CFG, in practice we would develop a probabilistic
    context free grammar (PCFG) and then use the Viterbi parser below for efficient
    parsing.
    """
    #parser = ViterbiParser(grammar)

    print "Num sentences: " + repr(len(sentences))

    for i, sent in enumerate(sentences):
        tkns = parseNums(sent.split(" "))
        try:
            print "-"*60
            print "Parsing Sentence #%d/%d."%(i+1, len(sentences))
            print "Sentence: \"%s\""%(sent)
            print "Tokenization: " + repr(tkns)
            print ""

            # Check whether how many unknown words there are:
            unknown_words = identify_unknown_words(tkns, grammar)
            if len(unknown_words) == 0:
                trees = parse_tokens(parser, tkns)
                assert len(trees) > 0
            elif len(unknown_words) == 1:
                print "There is an novel word in this sentence: " + unknown_words[0]
                novel_word = unknown_words[0]
                # Now determine whether we can create a new production for this word.
                print "Attempting to modify grammar to incorporate the novel word..."
                proposed_prod_rules = {}
                for trialID, category in enumerate(get_open_categories()):
                    trialProduction = create_lexical_production(category, novel_word)
                    newGrammar = add_terminal_production_to_grammar(trialProduction, grammar)
                    newParser = RecursiveDescentParser(newGrammar)
                    trees = parse_tokens(newParser, tkns, print_trees=False)

                    if len(trees) > 0:
                        print "Proposed production rule #%d: [%s] ... SUCCESS"%(trialID+1, str(trialProduction))
                        proposed_prod_rules[trialID+1] = trialProduction
                    else:
                        print "Proposed production rule #%d: [%s] ... N/A"%(trialID+1, str(trialProduction))

                assert len(proposed_prod_rules) > 0
                if len(proposed_prod_rules) > 0:
                    newProdRule = None
                    if len(proposed_prod_rules) == 1:
                        print "Only one production rule works so the grammar will be modified automatically..."
                        newProdRule = list(proposed_prod_rules.itervalues())[0]
                    else:
                        # ask the user for input
                        while newProdRule == None:
                            print "More than one production rule works so human-user assistance is required."
                            x = input("Select a *successful* rule (by number): ")
                            print "You entered: " + repr((x, type(x)))
                            if type(x) == int:
                                if x in proposed_prod_rules:
                                    newProdRule = proposed_prod_rules[x]
                    print "Modifying the grammar by adding: " + repr(newProdRule)
                    grammar = add_terminal_production_to_grammar(newProdRule, grammar)
                    parser = RecursiveDescentParser(grammar)
                    parse_tokens(parser, tkns)
            else:
                print "Too many novel words in this sentence: " + repr(unknown_words)

        except Exception as e:
            print "ERROR: Failed to parse sentence."
            print e
        finally:
            print ""
            sys.stdout.flush()


def main():
    SENTENCES = read_sentences_from_file('novel_sentences.txt')
    #SENTENCES = read_sentences_from_file('test_sentences.txt')
    GRAMMAR = read_grammar_from_file('semantic-grammar.txt')
    process_sentences(SENTENCES, GRAMMAR)

    # Useful for debugging.
    #SENTENCES = [s for (_, s) in sorted([(len(s.split()), s) for s in SENTENCES])]
    #SENTENCES = list(reversed(SENTENCES))


if __name__ == '__main__':
    main()
