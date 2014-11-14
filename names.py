from nltk.corpus import ieer
import nltk

def tree_search(tree, filt):
    for node in tree:
        if filt(node):
            yield node
        elif isinstance(node, nltk.tree.Tree):
            for sub in tree_search(node, filt):
                yield sub

def is_person(t):
    if not isinstance(t, nltk.tree.Tree):
        return False
    return t.label()=="PERSON"

docs = ieer.parsed_docs('NYT_19980315')
for doc in docs:
    for elem in tree_search(doc.text, is_person):
        print ' '.join(elem.leaves())
