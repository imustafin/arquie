from py2neo import Graph

g = Graph(user='neo4j', password='123')

def format_node(n):
    return '#' + str(n['id']) + ' ' + n['class'] + ' "' + n['name'] + '"'

def print_duplicate_name_warnings():
    for r in g.run(
            'MATCH (n), (m) WHERE n.name = m.name '
            'AND n <> m AND ID(n) < ID(m) RETURN n, m'):
        n, m = r['n'], r['m']
        print(f'Duplicate name: {format_node(n)} and {format_node(m)} '
              'have the same name')

def print_warnings():
    print_duplicate_name_warnings()

def main():
    print_warnings()

if __name__ == '__main__':
    main()
