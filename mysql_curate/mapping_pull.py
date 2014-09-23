from split import is_mysql_script, get_commands, get_substring_instances
from rdp import *
import re

MAP_COMMAND_GRAMMAR = None
COMMAND = Symbol('cmd')
COLS = Symbol('cols')
VAL_REFS = Symbol('val_refs')
VAL_REF = Symbol('val_ref')
TMP_TBL = Symbol('tmp_tbl')
SRC_TBL = Symbol('src_tbl')
COL = Symbol('col')
VAL = Symbol('val')

def parse_node_to_substrings(string, node):
    return get_substring_instances(string, list(node.nonepsilon_terms()))

def __get_map_command_grammar__():
    global MAP_COMMAND_GRAMMAR
    if MAP_COMMAND_GRAMMAR is not None:
        return MAP_COMMAND_GRAMMAR
    opt_ws = RegexTerminal(r'\s*', flags=re.MULTILINE)
    insert = KeywordTerminal('insert')
    opt_ignore = Symbol('ignore?')
    ignore = KeywordTerminal('ignore')
    into = KeywordTerminal('into')
    select = KeywordTerminal('select')
    from_kw = KeywordTerminal('from')
    where = KeywordTerminal('where')
    as_kw = KeywordTerminal('as')

    obj = Symbol('obj')
    back_ap = StringTerminal('`')
    obj_name = RegexTerminal(r'(\w+)', name="obj_name")

    rr_share = StringTerminal('RR_Share.')

    left_par = StringTerminal('(')
    right_par = StringTerminal(')')

    comma = StringTerminal(',')

    col_ref = Symbol('col_ref')
    as_clause = Symbol('as_clause')
    VAL = Symbol('val')
    null = KeywordTerminal('null')
    int_term = RegexTerminal(r'(\d+)', name="int")
    dot = StringTerminal('.')

    string = Symbol('str')
    esc_ap = StringTerminal("''")
    del_ap = StringTerminal("'")
    not_ap = RegexTerminal(r"[^']", name="not_ap")
    str_body_char = Symbol('str_body_char')
    str_body = Symbol('str_body')

    star = RegexTerminal(r'.*', flags=re.MULTILINE|re.DOTALL)

    rules = [
        Rule(COMMAND, [
            opt_ws, insert, opt_ws, opt_ignore,
            into, opt_ws, rr_share, TMP_TBL, opt_ws,
            left_par, opt_ws, COLS, opt_ws, right_par, opt_ws,
            select, opt_ws, VAL_REFS, opt_ws,
            from_kw, opt_ws, rr_share, SRC_TBL, opt_ws,
            where, star
        ]),

        Rule(opt_ignore, [ignore, opt_ws]),
        Rule(opt_ignore, []),

        Rule(TMP_TBL, [obj]),
        Rule(SRC_TBL, [obj]),

        Rule(obj, [obj_name]),
        Rule(obj, [back_ap, obj_name, back_ap]),

        Rule(COLS, [COL, opt_ws, comma, opt_ws, COLS]),
        Rule(COLS, [COL]),
        Rule(COL, [obj]),

        Rule(VAL_REFS, [VAL_REF, opt_ws, comma, opt_ws, VAL_REFS]),
        Rule(VAL_REFS, [VAL_REF]),

        Rule(VAL_REF, [VAL, as_clause]),
        Rule(VAL_REF, [col_ref, as_clause]),
        Rule(col_ref, [COL]),
        Rule(col_ref, [obj, opt_ws, dot, opt_ws, COL]),

        Rule(as_clause, [opt_ws, as_kw, opt_ws, obj]),
        Rule(as_clause, []),

        Rule(VAL, [string]),
        Rule(VAL, [int_term]),
        Rule(VAL, [null]),

        Rule(string, [del_ap, str_body, del_ap]),
        Rule(str_body_char, [esc_ap]),
        Rule(str_body_char, [not_ap]),
        Rule(str_body, [str_body_char, str_body]),
        Rule(str_body, []),
    ]
    MAP_COMMAND_GRAMMAR = Grammar(rules, start=COMMAND)
    MAP_COMMAND_GRAMMAR.compile()
    return MAP_COMMAND_GRAMMAR

class MapCommandParser:
    def __init__(self, string):
        self.string = string
        self.stream = StringStream(string)
        self.parser = Parser(self.stream, __get_map_command_grammar__())
        self.is_map_command = self.parser.parse_full()
        if(self.is_map_command):
            self.parse_tree = self.parser.to_parse_tree()
    def is_valid(self):
        return self.is_map_command
    def get_template_table(self):
        assert(self.is_valid())
        node = self.parse_tree.find_node(lambda x:x.symbol==TMP_TBL)
        names = parse_node_to_substrings(self.string, node)
        assert(len(names)==1)
        return names[0]
    def get_source_table(self):
        assert(self.is_valid())
        node = self.parse_tree.find_node(lambda x:x.symbol==SRC_TBL)
        names = parse_node_to_substrings(self.string, node)
        assert(len(names)==1)
        name = names[0]
        assert(re.match('[A-Z]{2}\w+',name))
        return name[2:]
    def get_template_columns(self):
        assert(self.is_valid())
        root = self.parse_tree.find_node(lambda x:x.symbol==COLS)
        nodes = filter(lambda x:x.symbol==COL, root.iter_nodes())
        cols = [parse_node_to_substrings(self.string, n) for n in nodes]
        assert all(len(c)==1 for c in cols)
        return [c[0] for c in cols]
    def get_source_references(self):
        assert(self.is_valid())
        root = self.parse_tree.find_node(lambda x:x.symbol==VAL_REFS)
        nodes = filter(lambda x:x.symbol in [COL,VAL], root.iter_nodes())
        references = []
        for node in nodes:
            subs = parse_node_to_substrings(self.string, node)
            assert(len(subs)==1)
            ref = ('column' if node.symbol==COL else 'value', subs[0])
            references.append(ref)
        return references
    def get_mappings(self):
        src_tbl = self.get_source_table()
        tmp_tbl = self.get_template_table()
        tmp_cols = self.get_template_columns()
        src_refs = self.get_source_references()
        assert(len(tmp_cols)==len(src_refs))
        mappings = []
        for (src_type, src_col), tmp_col in zip(src_refs, tmp_cols):
            if src_type=='column':
                mappings.append((src_tbl.lower(), src_col.lower(), tmp_tbl.lower(), tmp_col.lower()))
        return mappings

if __name__=='__main__':
    cmd = """
insert ignore 
  into RR_Share.InHouseRepDataClean(state_cd, date, crd, first, middle, last, suffix) 
select 'Regulatory-MO', '2014-09-11', individualcrdnumber, firstname, middlename, lastname, suffixname 
  from RR_Share.MOComposite 
 where individualcrdnumber in (select individualcrdnumber 
                                 from RR_Share.MORegistrationsActiveEmployments 
                where status = 'APPROVED' 
                  and registrationcategory = 'AG');
    """
    p = MapCommandParser(cmd)
    print p.is_valid()
    print p.get_template_table()
    print p.get_template_columns()
    print p.get_source_table()
    print p.get_source_references()
    for mapping in p.get_mappings():
        print mapping
    

    cmd = """
delete RR.CurrentRegistration
    from RR.CurrentRegistration
    join RR_Share.MORegistrationsActiveEmployments
        on CurrentRegistration.CRD = MORegistrationsActiveEmployments.IndividualCRDNumber
 where CurrentRegistration.RegCategory = MORegistrationsActiveEmployments.RegistrationCategory
     and CurrentRegistration.RegDate <= '2014-09-11';
    """
    p = MapCommandParser(cmd)
    print p.is_valid()
