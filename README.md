# NLP

* Improve the grammar (and adapt to 'novel' words)
* Develop a simple system for acquiring new terminal production rules.

The basic idea is that if the parser encounters a sentence in which exactly one word does not have an entry in the grammar, we can try assigning each category to that word and seeing if the parser can then parse the sentence — if it can, then there is either one parse or several. 

If there is one parse, then the system automatically assigns the word to that category. If there are several it prompts the user to assist in selecting which category. By improving the grammar, the system is able to assign pretty accurate parses and build up its grammar.

This process is documented in the output of the program.

The files contains an adaptible semantic-syntactic grammar and parser, semantic-parser.py  - some of the novel sentences it
automatically can adapt to are given in acquisition-output.txt.
and localization in localization-output-updated.txt
Currently, it just adapts to novel words, but it’s straightforward to extend that same idea to novel phrasing as well.
