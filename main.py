from py2neo import Graph

g = Graph(user='neo4j', password='123')

print('Hi! You have these nodes in your db:')

for r in g.run('MATCH (n) RETURN n'):
    n = r['n']
    print(dict(n))
