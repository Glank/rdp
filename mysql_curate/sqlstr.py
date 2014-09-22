import sys, os
sys.path.append(os.getcwd())
from rdp import *

class SQLString(ComplexTerminalSymbol):
    def __init__(self):
        string = Symbol('str')
        esc_ap = StringTerminal("''")
        del_ap = StringTerminal("'")
        not_ap = RegexTerminal(r"[^']", name="not_ap")
        str_body_char = Symbol('str_body_char')
        str_body = Symbol('str_body')
        rules = [
            Rule(string, [del_ap, str_body, del_ap]),
            Rule(str_body_char, [esc_ap]),
            Rule(str_body_char, [not_ap]),
            Rule(str_body, [str_body_char, str_body]),
            Rule(str_body, []),
        ]
        gram = Grammar(rules, start=string)
        gram.compile()
        ComplexTerminalSymbol.__init__(self, 'SQL String', gram)

if __name__=='__main__':
    gram = Grammar([Rule(Symbol('S'),[SQLString(), SQLString()])])
    stream = StringStream("'Testin''''Testing''")
    parser = Parser(stream, gram)
    print parser.parse_full()
