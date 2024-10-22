from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import json

class SmallKG:
    def __init__(self):
        # Define a small knowledge graph with meaningful relations
        self.triples = [
            # Academic relations
            ('student1', 'studies_at', 'university1'),
            ('professor1', 'works_at', 'university1'),
            ('student1', 'advised_by', 'professor1'),
            ('professor1', 'researches', 'topic1'),
            ('student1', 'researches', 'topic1'),
            ('student2', 'studies_at', 'university2'),
            ('student3', 'studies_at', 'university3'),
            ('student1', 'studies', 'Computer Science'),
            ('student2', 'studies', 'Mathematics'),
            ('student3', 'studies', 'Physics'),
            ('student1', 'interested_in', 'Artificial Intelligence'),
            ('student2', 'interested_in', 'Data Science'),
            ('student3', 'interested_in', 'Quantum Mechanics'),
            ('student1', 'enrolled_in', 'course1'),
            ('student2', 'enrolled_in', 'course2'),
            ('student3', 'enrolled_in', 'course3'),
            ('course1', 'offered_by', 'university1'),
            ('course2', 'offered_by', 'university2'),
            ('course3', 'offered_by', 'university3'),
            
            # Geographic relations
            ('CityA', 'located_in', 'country1'),
            ('company1', 'based_in', 'city1'),
            ('university1', 'located_in', 'CityA'),
            ('university2', 'located_in', 'CityB'),
            ('university3', 'located_in', 'CityC'),
            
            # Professional relations
            ('professor1', 'collaborates_with', 'professor2'),
            ('professor2', 'works_at', 'university2'),
            ('company1', 'partners_with', 'university1'),
('university1', 'offers_program_in', 'Computer Science'),
('university2', 'offers_program_in', 'Mathematics'),
('university3', 'offers_program_in', 'Physics'),
            
            # Publication relations
            ('professor1', 'published', 'paper1'),
            ('student1', 'published', 'paper1'),
            ('paper1', 'cites', 'paper2'),
            ('paper2', 'about', 'topic2')
        ]
        
        self.json_data = self._create_json_structure_raw()
        
    def _create_graph(self):
        G = nx.DiGraph()
        for h, r, t in self.triples:
            G.add_edge(h, t, relation=r)
        return G
    
    def _get_entities(self):
        entities = set()
        for h, _, t in self.triples:
            entities.add(h)
            entities.add(t)
        return sorted(list(entities))
    
    def _get_relations(self):
        return sorted(list(set(r for _, r, _ in self.triples)))
    
    def print_statistics(self):
        print("\nKnowledge Graph Statistics:")
        print(f"Number of entities: {len(self.entities)}")
        print(f"Number of relations: {len(self.relations)}")
        print(f"Number of triples: {len(self.triples)}")
        print(f"Graph density: {nx.density(self.graph):.5f}")
        
        # Entity types statistics
        entity_types = {
            'person': len([e for e in self.entities if 'student' in e or 'professor' in e]),
            'organization': len([e for e in self.entities if 'university' in e or 'company' in e]),
            'location': len([e for e in self.entities if 'city' in e or 'country' in e]),
            'paper': len([e for e in self.entities if 'paper' in e]),
            'topic': len([e for e in self.entities if 'topic' in e])
        }
        
        print("\nEntity Types Distribution:")
        for type_name, count in entity_types.items():
            print(f"{type_name}: {count}")
    
    def visualize(self):
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(self.graph, k=1, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color='lightblue', 
                             node_size=1000)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, arrows=True, 
                             arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(self.graph, 'relation')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels)
        
        plt.title("Small Knowledge Graph")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def _create_json_structure_raw(self):
        # Create the JSON structure using defaultdict
        graph_dict = defaultdict(dict)
        
        # Convert triples to the required format
        for h, r, t in self.triples:
            src_node = h
            dst_node = t
            edge = r
            graph_dict[src_node][edge] = dst_node
        
        return dict(graph_dict)
    
    def save_json(self, filename='small_kg.json'):
        # Save the JSON structure
        with open(filename, 'w') as f:
            json.dump(self.json_data, f, indent=4)

# Create and save the JSON representation
kg_json = SmallKG()
kg_json.save_json()

# Print a sample of the JSON structure
print("\nSample of JSON structure:")
sample_nodes = list(kg_json.json_data.keys())
sample_data = {node: kg_json.json_data[node] for node in sample_nodes}
print(json.dumps(sample_data, indent=4))