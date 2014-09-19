# -*- coding: latin-1 -*-
from grammar import *
from streams import *
from terms import *
from parser import *
import re

command = Symbol('cmd')
line_comment = RegexTerminal(r'--.*?\n', flags=re.MULTILINE, name="line_comment")
block_comment = RegexTerminal(r'/\*.*?\*/', flags=re.MULTILINE|re.DOTALL, name="block_comment")
shell_cmd = RegexTerminal(r'\!.*?\n', flags=re.MULTILINE, name="shell_cmd")
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
    Rule(command, [cmd_body]),
    Rule(cmd_body, [line_comment, cmd_body]),
    Rule(cmd_body, [shell_cmd, cmd_body]),
    Rule(cmd_body, [block_comment, cmd_body]),
    Rule(cmd_body, [string, cmd_body]),
    Rule(string, [del_ap, str_body, del_ap]),
    Rule(str_body_char, [esc_ap]),
    Rule(str_body_char, [not_ap]),
    Rule(str_body, [str_body_char, str_body]),
    Rule(str_body, []),
    Rule(cmd_body, [not_block_start, cmd_body]),
    Rule(cmd_body, []),
]
gram = Grammar(rules, start=command)
print gram
gram.compile()

def is_mysql_command(s):
    stream = StringStream(s)
    parser = Parser(stream, gram)
    if parser.parse_partial():
        return s[:stream.index]
    return False

cmd = """Select * from some_table /* with
multi-line block comments; and
statemens */ with reasons --- comments;
and other stuff 'like;' this.;;"""
print is_mysql_command(cmd)
