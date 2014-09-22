from split import is_mysql_script, get_commands
from rdp import *

MAP_COMMAND_GRAMMAR = None
COMMAND = Symbol('cmd')

opt_ws = RegexTerminal(r'\s*', flags=re.MULTILINE)
insert = KeywordTerminal('insert')
opt_ignore = Symbol('ignore?')
ignore = KeywordTerminal('ignore')
into = KeywordTerminal('into')

rules = [
    Rule(COMMAND, [opt_ws, insert, opt_ws, opt_ignore, into, opt_ws]),
    Rule(opt_ignore, [ignore, opt_ws]),
    Rule(opt_ignore, []),
]
gram = Grammar(rules, start=COMMAND)
gram.compile()

def is_map_command(s):
    stream = StringStream(s)
    parser = Parser(stream, gram)
    return parser.parse_full()

if __name__=='__main__':
    print is_map_command(cmd)
