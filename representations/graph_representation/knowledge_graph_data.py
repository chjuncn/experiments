import requests

# url = "http://api.conceptnet.io/query?node=/c/en/bicycle"
# response = requests.get(url).json()

# for edge in response['edges']:
#     print(f"{edge['start']['label']} {edge['rel']['label']} {edge['end']['label']}")


# from SPARQLWrapper import SPARQLWrapper, JSON

# sparql = SPARQLWrapper("https://dbpedia.org/sparql")
# sparql.setQuery("""
# SELECT ?city WHERE {
#     ?city rdf:type dbo:City .
#     ?city dbo:country "Canada" .
# } LIMIT 20
# """)
# sparql.setReturnFormat(JSON)
# results = sparql.query().convert()

# for result in results["results"]["bindings"]:
#     print(f"City: {result['city']['value']}, Country: {result['country']['value']}")




API_KEY = 'YOUR_GOOGLE_API_KEY'
url = f'https://kgsearch.googleapis.com/v1/entities:search?query=Albert%20Einstein&key={API_KEY}&limit=10&indent=True'
response = requests.get(url).json()

for element in response['itemListElement']:
    print(f"Name: {element['result']['name']}, Description: {element['result']['description']}")
