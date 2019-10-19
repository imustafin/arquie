from py2neo import Graph, Relationship, Node

g = Graph(user='neo4j', password='123')

def format_node(n):
    return '(' + n['class'] + ' "' + n['name'] + '")'

def format_rel(r):
    return (format_node(r['from'])
            + '-[' + r['type']
            + ']->'
            + format_node(r['to'])
            +'\n'
            +r['desc'])

def print_duplicate_name_warnings():
    for r in g.run(
            'MATCH (n), (m) WHERE n.name = m.name '
            'AND n <> m AND ID(n) < ID(m) RETURN n, m'):
        n = r['n']
        m = r['m']
        print(f'Duplicate name: {format_node(n)} and {format_node(m)} '
              'have the same name')

def print_warnings():
    print_duplicate_name_warnings()

APP = 'ApplicationComponent'
APP_SRV = 'ApplicationService'
API = 'ApplicationInterface'
ASSGN = 'AssignmentRelationships'
SERVES = 'ServingRelationships'
BUS_PROC = 'BusinessProcess'
COMP = 'CompositionRelationships'
APP_FUNC = 'ApplicationFunction'
REALIZES = 'RealizationRelationships'


RULES = [
    ((APP, ASSGN, APP_SRV, SERVES, APP), SERVES),
    ((APP, ASSGN, APP_SRV, SERVES, BUS_PROC), SERVES),
    ((APP, COMP, API, SERVES, APP), SERVES),
    ((APP, ASSGN, APP_FUNC, REALIZES, APP_SRV), REALIZES),
    ((APP, ASSGN, APP_FUNC, COMP, APP_FUNC), ASSGN)
]

def derive_by_rule(rule):
    types, rel_type = rule
    tsa, t1, ts, t2, tsc = types

    ans = []
    for r in g.run(
            'MATCH (sa)-[:' + t1 + ']->'
            '(s)-[r:' + t2 + ']->(sc)'
            'WHERE sa.class="' + tsa + '"'
            ' AND s.class="' + ts + '"'
            ' AND sc.class="' + tsc + '"'
            ' AND NOT (sa)-[:' + rel_type + ']-(sc)'
            'RETURN sa, sc, s'):
        sa = r['sa']
        sc = r['sc']
        s = r['s']

        ans.append({
            'from': sa,
            'type': 'Serves',
            'to': sc,
            'desc': (format_node(sa)
                     + ' ' + t1 + ' '
                     + format_node(s)
                     + ' ' + t2 + ' '
                     + format_node(sc)
                     + ', this means that '
                     + format_node(sa)
                     + ' ' + rel_type + ' '
                     + format_node(sc))
        })

    return ans

def derive_relationships():
    rels = []
    for r in RULES:
        rels += derive_by_rule(r)

    return rels

def make_rels():
    n = 0
    m = 0
    while True:
        n += 1
        # print('Deriving relationships, iteration', n)
        
        rels = derive_relationships()
        if not rels:
            break

        for r in rels:
            m += 1
            # g.create(Relationship(r['from'], r['type'], r['to']))
            print(r['desc'])

        return

    print('Derived', m, 'relationships in total')

def main():
    print_warnings()

    make_rels()

if __name__ == '__main__':
    main()
