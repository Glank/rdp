from grammar import *
from streams import *
from terms import *
from parser import *

def language_example():
    #First we will define some grammar rules
    S = Symbol('S')
    NP = Symbol('NP')
    VP = Symbol('VP')
    AVP = Symbol('AVP')
    N = Symbol('N')
    V = Symbol('V')
    DP = Symbol('DP')
    Det = Symbol('Det')
    Adj = Symbol('Adj')
    Adv = Symbol('Adv')
    core_rules = [
        Rule(S, [DP, VP]),
        Rule(DP, [Det, NP]),
        Rule(DP, [NP]),
        Rule(NP, [Adj, NP]),
        Rule(NP, [N]),
        Rule(VP, [AVP,DP]),
        Rule(VP, [AVP,DP,DP]),
        Rule(VP, [AVP]),
        Rule(AVP, [Adv, V]),
        Rule(AVP, [V]),
    ]
    #Lets check out what that grammar would look like
    print Grammar(core_rules)
    #Next, we will specify the parts of speach of a few words
    words = [
        ("john", [N]),
        ("car", [N]),
        ("cook", [N,V]),
        ("the", [Det]),
        ("is", [V]),
        ("run", [V]),
        ("lazy", [Adj]),
        ("fine", [N,Adj]),
        ("a", [Det]),
        ("gave", [V]),
        ("thankfully", [Adv]),
        ("hesitantly", [Adv]),
        ("cold", [V,N]),
        ("sandwich", [N]),
    ]
    word_rules = []
    for word, parts in words:
        for part in parts:
            rule = Rule(part, [WordTerminal(word)])
            word_rules.append(rule)
    #Now we can compile a full grammar:
    gram = Grammar(core_rules+word_rules)
    gram.compile()
    print gram
    #and we can try parsing a stream
    stream = WordStream("the fine cook gave".split())
    parser = Parser(stream, gram)
    parsed =  parser.parse_full()
    print parsed
    if parsed:
        print parser
        tree = parser.to_parse_tree()
        print tree

if __name__=="__main__":
    language_example()
