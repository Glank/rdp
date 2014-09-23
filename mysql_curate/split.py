import sys, os
sys.path.append(os.getcwd())
import re
from rdp import *
from sqlstr import SQLString

MYSQL_SCRIPT_GRAMMAR = None
COMMAND = Symbol('cmd')
LINE_COMMENT = RegexTerminal(r'--.*?\n', flags=re.MULTILINE, name="line_comment")
BLOCK_COMMENT = RegexTerminal(r'/\*.*?\*/', flags=re.MULTILINE|re.DOTALL, name="block_comment")
SHELL_CMD = RegexTerminal(r'\\!.*?\n', flags=re.MULTILINE, name="shell_cmd")

def __get_mysql_script_grammar__():
    global MYSQL_SCRIPT_GRAMMAR
    if MYSQL_SCRIPT_GRAMMAR is not None:
        return MYSQL_SCRIPT_GRAMMAR
    script = Symbol('S')
    command = Symbol('cmd')
    cmd_body = Symbol('cmd_body')
    semi_colon = StringTerminal(";")
    not_block_start = RegexTerminal("[^;']", name="not_block_start")
    string = Symbol('str')
    esc_ap = StringTerminal("''")
    del_ap = StringTerminal("'")
    not_ap = RegexTerminal(r"[^']", name="not_ap")
    str_body_char = Symbol('str_body_char')
    str_body = Symbol('str_body')
    rules = [
        Rule(script, [command, semi_colon, script]),
        Rule(script, [command]),
        Rule(COMMAND, [cmd_body]),
        Rule(cmd_body, [LINE_COMMENT, cmd_body]),
        Rule(cmd_body, [SHELL_CMD, cmd_body]),
        Rule(cmd_body, [BLOCK_COMMENT, cmd_body]),
        Rule(cmd_body, [string, cmd_body]),
        Rule(cmd_body, [not_block_start, cmd_body]),
        Rule(cmd_body, []),
        Rule(string, [del_ap, str_body, del_ap]),
        Rule(str_body_char, [esc_ap]),
        Rule(str_body_char, [not_ap]),
        Rule(str_body, [str_body_char, str_body]),
        Rule(str_body, []),
    ]
    gram = Grammar(rules)
    gram.compile()
    MYSQL_SCRIPT_GRAMMAR = gram
    return MYSQL_SCRIPT_GRAMMAR

def is_mysql_script(s):
    stream = StringStream(s)
    parser = Parser(stream, __get_mysql_script_grammar__())
    return parser.parse_full()

def merge_ranges(ranges):
    ranges = list(ranges)
    if not ranges:
        return []
    ranges.sort(key=lambda x:x[1])
    ranges.sort(key=lambda x:x[0])
    new_ranges = []
    start = ranges[0][0]
    for i in xrange(len(ranges)-1):
        if ranges[i][1]<ranges[i+1][0]:
            r = start, ranges[i][1]
            start = ranges[i+1][0]
            new_ranges.append(r)
    r = start, ranges[-1][1]
    new_ranges.append(r)
    return new_ranges

def ranges_to_subs(s, ranges):
    return [s[r[0]:r[1]] for r in ranges]

def get_substring_instances(s, nodes):
    if not nodes:
        return []
    ranges = [n.range for n in nodes]
    ranges = merge_ranges(ranges)
    return ranges_to_subs(s,ranges)

def get_commands(s, remove_comments=False, remove_shell_cmds=False):
    stream = StringStream(s)
    parser = Parser(stream, __get_mysql_script_grammar__())
    assert(parser.parse_full())
    def cmd_node(n):
        return n.symbol==COMMAND
    command_nodes = filter(cmd_node, parser.to_parse_tree().iter_nodes())
    cmds = []
    for cmd_node in command_nodes:
        to_remove = []
        if remove_comments:
            to_remove+=[LINE_COMMENT, BLOCK_COMMENT]
        if remove_shell_cmds:
            to_remove+=[SHELL_CMD]
        not_removed = lambda x:x.symbol not in to_remove
        net = lambda x:not x.children and x.symbol!=Epsilon()
        nodes = filter(net, cmd_node.iter_nodes(pfilter=not_removed))
        strings = get_substring_instances(s, nodes)    
        cmds.append(''.join(strings))
    return cmds

if __name__=='__main__':
    cmd = """Select * from some_table /* with
    multi-line block comments'; and
    statemens */ with reasons --- 'comments;
    and other stuff 'like;' this.;or;
    like this \\!with; a shell cmd'
    and other junk"""
    print is_mysql_script(cmd)
    print get_commands(cmd, remove_comments=True, remove_shell_cmds=True)
