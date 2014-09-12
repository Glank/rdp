# -*- coding: latin-1 -*-
from grammar import *
from streams import *
from terms import *
from parser import *

S = Symbol('S')
A = Symbol('A')
B = Symbol('B')
a = StringTerminal('a')
b = StringTerminal('b')
rules = [
    Rule(S, [A,B]),
    Rule(A, [a]),
    Rule(A, [S,A]),
    Rule(B, [b]),
    Rule(B, [S,B]),
]
gram = Grammar(rules)
print gram
gram.compile()
print "*"*35
print gram
print "*"*35


stream = StringStream("aabb")
parser = Parser(stream, gram)
print parser.parse_full()
dec_list,_ = parser.get_generation_lists()
print dec_list
print len(gram.to_parent_transforms)
print gram.transform_to_parent(dec_list)
exit()
dec_lists = gram.transform_to_parent(
    dec_list, include_intermediates=True
)
for dl in dec_lists:
    print dl
exit()


exit()

for trans in gram.to_parent_transforms:
    print trans

exit()
for i, g in enumerate(gram.intermediates):
    latex = str(g)
    lines = latex.split('\n')
    lines = [l[l.index('\t')+1:] for l in lines]
    latex = "\\\\\n".join(lines)
    latex = latex.replace("->","&\\rightarrow")
    latex = latex.replace("_0","Z")
    latex = latex.replace("_S0","S'")
    latex = latex.replace("'a'","a")
    latex = latex.replace("'b'","b")
    latex = latex.replace("ε","\\epsilon")
    latex = "\\begin{align}\n"+latex
    latex = "\\setcounter{equation}{0}\n"+latex
    latex+= "\n\\end{align}"
    print "Grammar %d:"%(i+1)
    print latex
