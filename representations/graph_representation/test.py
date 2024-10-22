import os
import sys

from typing import Any, Dict

import json
import pandas as pd
from io import BytesIO
from agents_lib import agent_util as agents


import regex as re # Use regex instead of re to used variable length lookbehind


def test1():

    #load the data
    edge_df, node_df = load_got()
    print(node_df, type(node_df))
    print(edge_df)
    #init Jaal and run server
    # Jaal(edge_df, node_df).plot()
    jaal = Jaal.create()
    jaal.add_node(0)
    jaal.add_node(1)
    jaal.add_edge(0, 1)
    jaal.plot()


def test2():
    import igraph as ig
    import gravis as gv
    import networkx as nx

    graph = {'graph': {'nodes': {'A': {}, 'B': {}}, 'edges': [{'source': 'A', 'target': 'B'}]}}
    fig = gv.vis(graph)
    fig.display()

    graph = nx.powerlaw_cluster_graph(n=120, m=2, p=0.95)
    fig = gv.three(graph)
    fig.export_html('powerlaw_cluster.html')

    graph = ig.Graph.Forest_Fire(120, 0.15)
    fig = gv.d3(graph, zoom_factor=0.25)
    fig.export_svg('forest_fire.svg')


def test3():
    text = """
```json
"26209be4-828e-4460-89d5-668db0f701c2": "8eb61333-9fc2-4a81-9dd7-e32376c0d901"
```    """
    print(agents.getJsonFromAnswer(text))

def updateSource(source, key):
    source ="""
{
    "<key>=node_11": {
        "edge_5e_11": "node_6",
        "edge_4e_11": "node_7",
        "edge_1e_11": "node_12",
        "edge_2e_11": "node_13",
        "edge_3e_11": "node_14"
    },
    "<key>=node_32": {
        "edge_5e_32": "node_27",
        "edge_4e_32": "node_28",
        "edge_1e_32": "node_33",
        "edge_2e_32": "node_34",
        "edge_3e_32": "node_35"
    }
}
  """
    startIndex = source.find("{")
    endIndex = source.rfind("}")
    source = source[startIndex+1:endIndex]
    startIndex = 0
    endIndex = len(source) - 1
    while startIndex < endIndex:
        str_start = source.find("{", startIndex)
        str_end = source.find("}", startIndex)
        if str_start == -1 or str_end == -1:
            break
        print("index", str_start, str_end)
        name_start = source.find("<key>=", startIndex)
        name=source[name_start+6:str_start-3]
        print("name>>>>", name)
        start_name = "<"+name+">"
        end_name = "</"+name+">"
        source = source.replace("{", start_name, 1)
        source = source.replace("}", end_name, 1)
        startIndex = source.find(end_name) + len(end_name)
        endIndex = len(source) - 1
        print(startIndex, endIndex)
        print(source)

    return "{\n"+source+"\n}"

# updateSource("", "")

test3()