from py2neo import Graph

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


def derive_app_serves_interface_to_app():
    ans = []
    for r in g.run(
            'MATCH (sa)-[:AssignmentRelationships]->'
            '(s)-[r:ServingRelationships]->(sc)'
            'WHERE sa.class="ApplicationComponent"'
            ' AND s.class="ApplicationService"'
            ' AND sc.class="ApplicationComponent"'
            ' AND NOT (sa)-[:ServingRelationships]-(sc)'
            'RETURN sa, sc, s'):
        sa = r['sa']
        sc = r['sc']
        s = r['s']

        ans.append({
            'from': sa,
            'type': 'Serves',
            'to': sc,
            'desc': (format_node(sa)
                     + ' serves interface '
                     + format_node(s)
                     + ' which serves to '
                     + format_node(sc)
                     + ', this means that '
                     + format_node(sa)
                     + ' serves '
                     + format_node(sc))
        })

    return ans

def derive_relationships():
    rels = []
    rels += derive_app_serves_interface_to_app()

    return rels


def main():
    print_warnings()

    rels = derive_relationships()
    for r in rels:
        print('~~~')
        print(format_rel(r))

if __name__ == '__main__':
    main()
