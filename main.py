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

def query():
	user_query = input ("\nInput your query: ")
	query_parse(user_query)

def query_parse(user_query):
	if "NODES" in user_query.upper():
		query_node_parse()
	elif "RELATION" in user_query.upper():
		query_relation_parse()
	# elif "NODES NO-RELATION" in user_query.upper():
	# 	print("NR!")
	else:
		print("Query is not recognized!")

def query_node_parse():
	class_name = input("Input Class Name: ")
	query_execution = "MATCH (n {class:'"+class_name+"'}) return n"

	print("\nList of Nodes of "+class_name+":")

	total_data = 0
	for r in g.run(query_execution):
		n = r['n']
		print(f'{format_node(n)}')
		total_data += 1

	if total_data < 1:
		print("There is no data")

def query_relation_parse():
	name = input("Input Element Name: ")
	limit = input("(Optional) Input maximum depth level integer: ")
	class_name = input("(Optional) Input specific class type: ")

	if limit == "":
		limit_query = 10
	else:
		limit_query = limit

	if class_name == "":
		query_execution = "MATCH (n)<-[*1.."+str(limit_query)+"]-(c{name:'"+name+"'}) RETURN c, n"
	else:
		query_execution = "MATCH (n {class:'"+class_name+"'})<-[*1.."+str(limit_query)+"]-(c{name:'"+name+"'}) RETURN c, n"

	print("\nList of connected Nodes from "+name+":")

	total_data = 0
	for r in g.run(query_execution):
		c, n = r['c'], r['n']
		print(f'{format_node(n)}')
		total_data += 1

	if total_data < 1:
		print("There is no data")

def main():
    print_warnings()
   
    while(True):
    	query()

if __name__ == '__main__':
    main()
