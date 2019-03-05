#!/usr/bin/env python

import itertools, sys

from nltk.parse import RecursiveDescentParser, ShiftReduceParser, ViterbiParser
from nltk import Nonterminal, nonterminals, Production, CFG, PCFG


TEST_SENTENCES = [

    "acoustic contact on DIFAR 95 , bearing 090 , frequency 1.234 .",
    "additional buoys of interest are 95 and 94 .",
    "updated bearing of 095 out of DIFAR 95 .",
    "roger .",
    "standby for localization pattern .",
    "turning inbound , drop heading is 120 .",
    "standby for buoy drops .",
    "sonobuoy power .",
    "sonobuoy arm , buoy available .",
    "DIFAR 94 away .",
    "good signal on all buoys .",
    "currently in the localization phase and monitoring all sensors for subsurface contact .",
    "all buoys tuned and processing .",
    "we currently have contact on DIFAR 94 bearing 072 and on DIFAR 93 bearing 290 .",
    "contact is assessed as a Chinese nuclear submarine based on frequency of 1.234 hertz .",
    "contact is now coming in on DIFAR 94 bearing 072 and on DIFAR 93 bearing 290 .",
    "roger .",
    "new fix position established .",
    "gentrack with initial course estimate of 225 and speed 5 knots .",
    "contact is classified as Chinese nuclear submarine based on detected frequencies of 123.4 hertz .",
    "send contact report using the gentrack course and speed .",
    "wilco .",
    "contact report has been sent to the TOC QSL 0945 Zulu .",
    "we are transitioning from the localization to tracking .",
    "I estimate the TOI course and speed to be 225 at 8 knots ."

    ]


grammar = CFG.fromstring("""

S -> CP '.'
S -> CP CONJ S
S -> NP


CP -> VAR_COMPLIANCE
CP -> NP ADJ
CP -> VP
CP -> VP PP
CP -> VP VP
CP -> NP PP

NP -> DET NP
NP -> ADJ NP
NP -> N
NP -> N NP
NP -> N PP
NP -> N CONJ NP

PP -> P NP
PP -> P PP
PP -> P NP PP
PP -> P NP CONJ PP

VP -> V
VP -> NP V
VP -> V NP
VP -> V NP PP
VP -> V NP NP
VP -> NP V NP
VP -> NP V NP NP
VP -> ADVERB VP

V -> AUX
V -> AUX V
V -> VAR_INSTRUCTION | VAR_ACTIVITY
V -> 'established' | 'classified' | 'away' | 'tuned' | 'processing'
V -> 'estimate' | 'updated' | 'arm' | 'power' | 'updated' | 'using'
V -> 'sent' | 'coming' | 'assessed' | 'detected'
V -> 'to' 'be'


ADVERB -> 'now' | 'currently'

AUX -> 'is' | 'was' | 'are' | 'were' | 'has' | 'be' | 'have'
AUX -> 'has' 'been'

ADJ -> VAR_STATUS
ADJ -> 'new' | 'additional' | 'available'

P -> 'for' | 'in' | 'of' | 'on' | 'from' | 'to' | 'with' | 'at' | 'as'
P -> 'out' PP
P -> 'based' PP

N -> VAR_INFO | VAR_DATA | VAR_PHASE | VAR_EVENT | VAR_ITEM | '*VAR-NUM*' | VAR_DIRECTION | VAR_PRONOUN | VAR_LOCATION
N -> 'signal' | 'interest' | 'speed' | 'TOI' | 'course' | 'frequency' | 'frequencies'
N -> VAR_ITEM VAR_INFO
N -> 'TOI' VAR_INFO



DET -> 'the' | 'a' | 'an' | 'this' | 'all'
CONJ -> 'and' | 'or' | ',' | ';'



VAR_COMPLIANCE -> 'roger' | 'wilco'
VAR_STATUS -> 'good' | 'bad' | 'great' | 'horrible' | 'terrible'
VAR_INSTRUCTION -> 'standby' | 'send'
VAR_PRONOUN -> 'I' | 'you' | 'he' | 'she' | 'we' | 'they' | 'contact' | 'who'
ATION -> 'TOC' 'QSL' '*VAR-NUM*' 'Zulu'
VAR_ACTIVITY -> 'monitoring' | 'studying' | 'turning' | 'transitioning'
VAR_INFO -> 'course' 'and' 'speed' | 'drop' 'heading' | 'fix' 'position' | 'initial' 'course' 'estimate' | 'bearing'
VAR_PHASE -> 'localization' | 'localization' 'phase' | 'localization' 'pattern' | 'tracking' | 'tracking' 'phase' | 'tracking' 'pattern'
VAR_DIRECTION -> 'inbound'
VAR_EVENT -> 'buoy' 'drops' | 'subsurface' 'contact' | 'acoustic' 'contact'
VAR_ITEM -> 'all' 'buoys' | 'buoy' | 'buoys' | 'sonobuoy' | 'sonobuoys' | 'Chinese' 'nuclear' 'submarine' | 'contact' 'report' | 'sensors' | 'gentrack' | 'all' 'sensors'
VAR_DATA -> DATATYPE '*VAR-NUM*'
VAR_DATA -> '*VAR-NUM*' DATATYPE
DATATYPE -> 'DIFAR' | 'bearing' | 'frequency' | 'frequencies' | 'knots' | 'hertz'

""")



##############################################################################



def isFloatNum(x):
    try:
        float(x)
        return True

    except ValueError:
        return False



def parseNums(tokens):
    return ["*VAR-NUM*" if (tkn.isdigit() or isFloatNum(tkn)) else tkn for tkn in tokens]



def main(sentences):

    parser = RecursiveDescentParser(grammar)
    """
    NOTE: While this demo uses a CFG, in practice we would develop a probabilistic
    context free grammar (PCFG) and then use the Viterbi parser below for efficient
    parsing.
    """

    #parser = ViterbiParser(grammar)
    sentences_to_skip = [12, 13]
    print "Num sentences: " + repr(len(sentences))



    for i, sent in enumerate(sentences):

        tkns = parseNums(sent.split(" "))
        try:

            print "-"*60
            print "Parsing Sentence #%d/%d."%(i+1, len(sentences))
            print "Sentence: \"%s\""%(sent)
            print "Tokenization: " + repr(tkns)

            if i in sentences_to_skip:
                print "Skipping this sentence as it takes a bit too long to parse without PCFG."
                continue

            print ""



            # Just take the first two parses produced for the demo.
            trees = list(itertools.islice(parser.parse(tkns), 2))

            for j, t in enumerate(trees):

                print "Parse #%d/%d:"%(j+1, len(trees))
                print t

            assert len(trees) > 0

        except Exception as e:
            print "ERROR: Failed to parse sentence."
            print e

        finally:
            print ""
            sys.stdout.flush()



if __name__=='__main__':

    #ordered_sents = [s for (_, s) in sorted([(len(s.split()), s) for s in TEST_SENTENCES])]
    #main(ordered_sents)
    main(TEST_SENTENCES)