import os
import random
import uuid
import json
from matplotlib import pyplot as plt
import pyvis
from pyvis.network import Network
import networkx as nx
import gravis as gv

from jaal.datasets import load_got
from jaal import Jaal
import pandas as pd

import networkx as nx
import random
import numpy as np

# node <-- node+3
# node --> node+1
# node --> node+2
def updateNodeWithLabels(edges, node_index, predicate, total_node_num, all_nodes:list=None, json_graph:dict=None):
    node_name = all_nodes[node_index]
    json_node = json_graph.get(node_name, {})
    json_node["label"] = node_index
    if "edges" not in json_node:
        json_node["edges"] = {}

    for i in range(1, 3):
        if node_index + i < total_node_num:
            json_node["edges"].update({predicate+str(i): all_nodes[node_index + i]})
            edges.append((node_index, node_index + i, 10, "medium"))
    json_graph.update({node_name: json_node})

    if node_index +3 < total_node_num:
        source_node_name = all_nodes[node_index + 3]
        source_node = json_graph.get(source_node_name, {})
        source_node["label"] = node_index + 3
        if "edges" not in source_node:
            source_node["edges"] = {}
        source_node["edges"].update({predicate+str(3): node_name})
        edges.append((node_index+3, node_index, 10, "medium"))
        json_graph.update({source_node_name: source_node})


def updateNodeWithoutLabels(edges, node_index, predicate, total_node_num, all_nodes:list=None, json_graph:dict=None, fanin_num=1, fanout_num=2, unique_key_name="<key>=", uinique_edge_name=False):
    node_name = all_nodes[node_index]
    node_name = unique_key_name+node_name
    json_node = json_graph.get(node_name, {})
    for i in range(1, 1+fanout_num):
        if node_index + i < total_node_num:
            edge_name = predicate+str(i)
            if uinique_edge_name:
                edge_name = edge_name + node_name[-4:]
            
            json_node[edge_name] = all_nodes[node_index + i]
            # json_node[edge_name] = node_index + i
            edges.append((node_index, node_index + i, 10, "medium"))
    json_graph.update({node_name: json_node})
    # json_graph.update({str(node_index): json_node})

    # Update fanin nodes
    for i in range(1+fanout_num, 1+fanout_num+fanin_num):
        if node_index +i < total_node_num:
            source_node_name = all_nodes[node_index + i]
            source_node_name = unique_key_name+source_node_name
            source_node = json_graph.get(source_node_name, {})
            edge_name = predicate+str(i)
            if uinique_edge_name:
                    edge_name = edge_name + source_node_name[-4:]
            source_node[edge_name] = all_nodes[node_index]
            # source_node[edge_name] = node_index
            edges.append((node_index+i, node_index, 10, "medium"))
            json_graph.update({source_node_name: source_node})
            # json_graph.update({str(node_index+i): source_node})


def generateGraphWithLabels(total_node_num):
    all_nodes = [str(uuid.uuid4()) for _ in range(total_node_num)]
    columns=["id", "name"]
    data = []
    for i in range(total_node_num):
        data.append([i, all_nodes[i]])
    node_df = pd.DataFrame(data, columns=columns)

    json_graph = {}
    edges = []
    for i in range(total_node_num):
        updateNodeWithLabels(edges, i, "point_to_", total_node_num, all_nodes, json_graph)

    edge_df = pd.DataFrame(edges, columns=['from', 'to', 'weigth', 'strength'])

    # sort json
    keys = list(json_graph.keys())
    random.shuffle(keys)
    sorted_json_graph = {}
    for key in keys:
        sorted_json_graph[key] = json_graph[key]

    return sorted_json_graph, edge_df, node_df


def existingGraph(node_num=50, fanin=1, fanout=2):
    source_str = ""
    if node_num==50 and fanin==1 and fanout==2:
        source_str = """
{
  "<key>=e7f22915-2230-4f27-af78-7967c463df62": {
    "edge_3df62": "5ceae0f2-ce30-4e85-904f-c53dd3ebee5e",
    "edge_1df62": "a6d4d8e8-e4dd-46dd-b0d6-fc96beb69b70",
    "edge_2df62": "d2e6eb02-fea5-4d42-a1c0-bf22d26e6b0e"
  },
  "<key>=829333df-77b1-4916-922d-3e271ef5f068": {
    "edge_3f068": "ffcefb18-bdcb-437c-972a-e86d87cab1ef",
    "edge_1f068": "e977d57b-2f5f-409b-ac3e-e2b285b302fa",
    "edge_2f068": "3e298c35-2a95-4ff1-842b-73341c7620a5"
  },
  "<key>=5ceae0f2-ce30-4e85-904f-c53dd3ebee5e": {
    "edge_1ee5e": "ce49ce9a-701d-4103-bd3b-6f22a905deb3",
    "edge_2ee5e": "f9ae9f63-821e-4420-9eb2-8e65a19eb1bd"
  },
  "<key>=06d987f0-0fd5-4191-a8b9-6adcab652ebf": {
    "edge_32ebf": "c59cecd9-c579-4c0a-bd96-03e470eb0692",
    "edge_12ebf": "626935d0-d34b-4f2d-b0c9-c32d8e64a3a3",
    "edge_22ebf": "fe41a4b1-9661-4670-ab4b-2251f8f9e6c6"
  },
  "<key>=ce49ce9a-701d-4103-bd3b-6f22a905deb3": {
    "edge_3deb3": "bf8d9a8a-4b54-4039-b914-1736c039f47a",
    "edge_1deb3": "f9ae9f63-821e-4420-9eb2-8e65a19eb1bd",
    "edge_2deb3": "e7f22915-2230-4f27-af78-7967c463df62"
  },
  "<key>=bf8d9a8a-4b54-4039-b914-1736c039f47a": {
    "edge_1f47a": "4173a0d3-0cd2-459a-b221-824de7736731",
    "edge_2f47a": "5ceae0f2-ce30-4e85-904f-c53dd3ebee5e"
  },
  "<key>=a6d4d8e8-e4dd-46dd-b0d6-fc96beb69b70": {
    "edge_39b70": "ce49ce9a-701d-4103-bd3b-6f22a905deb3",
    "edge_19b70": "d2e6eb02-fea5-4d42-a1c0-bf22d26e6b0e",
    "edge_29b70": "18a83b70-5388-4405-bdd8-5a84d53002b3"
  },
  "<key>=f9ae9f63-821e-4420-9eb2-8e65a19eb1bd": {
    "edge_3b1bd": "4173a0d3-0cd2-459a-b221-824de7736731",
    "edge_1b1bd": "e7f22915-2230-4f27-af78-7967c463df62",
    "edge_2b1bd": "a6d4d8e8-e4dd-46dd-b0d6-fc96beb69b70"
  },
  "<key>=5100561d-3608-45dd-9b7c-22bdc15d24ec": {
    "edge_324ec": "3031d870-8f1f-4fea-ad9e-6fbe41aad195",
    "edge_124ec": "829333df-77b1-4916-922d-3e271ef5f068",
    "edge_224ec": "e977d57b-2f5f-409b-ac3e-e2b285b302fa"
  },
  "<key>=b0523b95-e6c6-44b7-a78a-a93ac758f8c9": {
    "edge_3f8c9": "beaa42ba-808e-4416-aa20-8adf153934ec",
    "edge_1f8c9": "74b0da55-6d78-4213-afe8-bc5c803fc789",
    "edge_2f8c9": "d720b947-fafb-46da-91ff-9f2b3f9b52a4"
  },
  "<key>=fe41a4b1-9661-4670-ab4b-2251f8f9e6c6": {
    "edge_3e6c6": "a1338458-f9e0-440e-b939-8f09ae60b051",
    "edge_1e6c6": "5f4556d8-c47a-4e2e-9027-49c1d6b22533",
    "edge_2e6c6": "3031d870-8f1f-4fea-ad9e-6fbe41aad195"
  },
  "<key>=74b0da55-6d78-4213-afe8-bc5c803fc789": {
    "edge_3c789": "b4092713-0781-4494-9704-872e83f5df2e",
    "edge_1c789": "d720b947-fafb-46da-91ff-9f2b3f9b52a4",
    "edge_2c789": "9b35f25b-a630-4e77-b073-17c97238ad22"
  },
  "<key>=9976aa43-dcea-4fa7-8583-b41df7cfe89f": {
    "edge_3e89f": "3f8aee6f-9dac-43d8-849e-c2f361af7791",
    "edge_1e89f": "820ec180-4099-4c3b-866a-83b86a7264ff",
    "edge_2e89f": "b688b9c0-ff30-41d4-a054-433312dc6dd0"
  },
  "<key>=d9d0388b-b7cf-4ab5-935d-565993fcabff": {
    "edge_3abff": "b688b9c0-ff30-41d4-a054-433312dc6dd0",
    "edge_1abff": "beaa42ba-808e-4416-aa20-8adf153934ec",
    "edge_2abff": "b4092713-0781-4494-9704-872e83f5df2e"
  },
  "<key>=15755e62-69a2-4eac-b215-125dafe8c0dd": {
    "edge_3c0dd": "18a83b70-5388-4405-bdd8-5a84d53002b3",
    "edge_1c0dd": "0623c289-ce76-4c7a-a631-d141b18b7ff6",
    "edge_2c0dd": "57d6e1ee-5989-45c8-8778-57df3465da5b"
  },
  "<key>=57d6e1ee-5989-45c8-8778-57df3465da5b": {
    "edge_3da5b": "56967a18-e437-4884-8a7d-d74c5cfc7173",
    "edge_1da5b": "86db5ce0-ea2a-49a8-9f48-01d69b7a224c",
    "edge_2da5b": "abb31621-13f8-44de-9416-3ec890bdc8fd"
  },
  "<key>=56967a18-e437-4884-8a7d-d74c5cfc7173": {
    "edge_37173": "d2e6eb02-fea5-4d42-a1c0-bf22d26e6b0e",
    "edge_17173": "15755e62-69a2-4eac-b215-125dafe8c0dd",
    "edge_27173": "0623c289-ce76-4c7a-a631-d141b18b7ff6"
  },
  "<key>=b688b9c0-ff30-41d4-a054-433312dc6dd0": {
    "edge_36dd0": "6f5f2dc4-5087-42e4-9416-9a6fadac8bf9",
    "edge_16dd0": "4125f52a-cbce-40e5-a640-a3c82c6b3139",
    "edge_26dd0": "8c2eb4a4-ed6d-4807-a7cf-4aa18c69c1fb"
  },
  "<key>=ffcefb18-bdcb-437c-972a-e86d87cab1ef": {
    "edge_3b1ef": "fe41a4b1-9661-4670-ab4b-2251f8f9e6c6",
    "edge_1b1ef": "d1483b4a-0d77-468d-98d4-5b785748ae0b",
    "edge_2b1ef": "5100561d-3608-45dd-9b7c-22bdc15d24ec"
  },
  "<key>=d1483b4a-0d77-468d-98d4-5b785748ae0b": {
    "edge_3ae0b": "5f4556d8-c47a-4e2e-9027-49c1d6b22533",
    "edge_1ae0b": "5100561d-3608-45dd-9b7c-22bdc15d24ec",
    "edge_2ae0b": "829333df-77b1-4916-922d-3e271ef5f068"
  },
  "<key>=626935d0-d34b-4f2d-b0c9-c32d8e64a3a3": {
    "edge_3a3a3": "a21ad503-1781-4971-8b40-beb07676d196",
    "edge_1a3a3": "fe41a4b1-9661-4670-ab4b-2251f8f9e6c6",
    "edge_2a3a3": "5f4556d8-c47a-4e2e-9027-49c1d6b22533"
  },
  "<key>=b4092713-0781-4494-9704-872e83f5df2e": {
    "edge_3df2e": "8c2eb4a4-ed6d-4807-a7cf-4aa18c69c1fb",
    "edge_1df2e": "12ddf920-3bb3-418b-a966-90e52cdc3a20",
    "edge_2df2e": "b0523b95-e6c6-44b7-a78a-a93ac758f8c9"
  },
  "<key>=a0ed9513-b7ae-4d3b-81d4-771e4b469534": {
    "edge_39534": "e977d57b-2f5f-409b-ac3e-e2b285b302fa",
    "edge_19534": "6f5f2dc4-5087-42e4-9416-9a6fadac8bf9",
    "edge_29534": "9976aa43-dcea-4fa7-8583-b41df7cfe89f"
  },
  "<key>=a21ad503-1781-4971-8b40-beb07676d196": {
    "edge_3d196": "abb31621-13f8-44de-9416-3ec890bdc8fd",
    "edge_1d196": "a1338458-f9e0-440e-b939-8f09ae60b051",
    "edge_2d196": "06d987f0-0fd5-4191-a8b9-6adcab652ebf"
  },
  "<key>=5f4556d8-c47a-4e2e-9027-49c1d6b22533": {
    "edge_32533": "06d987f0-0fd5-4191-a8b9-6adcab652ebf",
    "edge_12533": "3031d870-8f1f-4fea-ad9e-6fbe41aad195",
    "edge_22533": "ffcefb18-bdcb-437c-972a-e86d87cab1ef"
  },
  "<key>=6f5f2dc4-5087-42e4-9416-9a6fadac8bf9": {
    "edge_38bf9": "3e298c35-2a95-4ff1-842b-73341c7620a5",
    "edge_18bf9": "9976aa43-dcea-4fa7-8583-b41df7cfe89f",
    "edge_28bf9": "820ec180-4099-4c3b-866a-83b86a7264ff"
  },
  "<key>=86db5ce0-ea2a-49a8-9f48-01d69b7a224c": {
    "edge_3224c": "15755e62-69a2-4eac-b215-125dafe8c0dd",
    "edge_1224c": "abb31621-13f8-44de-9416-3ec890bdc8fd",
    "edge_2224c": "99548187-0c23-4f17-9a0e-96ed07a70ae1"
  },
  "<key>=c59cecd9-c579-4c0a-bd96-03e470eb0692": {
    "edge_30692": "86db5ce0-ea2a-49a8-9f48-01d69b7a224c",
    "edge_10692": "a21ad503-1781-4971-8b40-beb07676d196",
    "edge_20692": "a1338458-f9e0-440e-b939-8f09ae60b051"
  },
  "<key>=820ec180-4099-4c3b-866a-83b86a7264ff": {
    "edge_364ff": "a0ed9513-b7ae-4d3b-81d4-771e4b469534",
    "edge_164ff": "b688b9c0-ff30-41d4-a054-433312dc6dd0",
    "edge_264ff": "4125f52a-cbce-40e5-a640-a3c82c6b3139"
  },
  "<key>=4125f52a-cbce-40e5-a640-a3c82c6b3139": {
    "edge_33139": "9976aa43-dcea-4fa7-8583-b41df7cfe89f",
    "edge_13139": "8c2eb4a4-ed6d-4807-a7cf-4aa18c69c1fb",
    "edge_23139": "d9d0388b-b7cf-4ab5-935d-565993fcabff"
  },
  "<key>=12ddf920-3bb3-418b-a966-90e52cdc3a20": {
    "edge_33a20": "d9d0388b-b7cf-4ab5-935d-565993fcabff",
    "edge_13a20": "b0523b95-e6c6-44b7-a78a-a93ac758f8c9",
    "edge_23a20": "74b0da55-6d78-4213-afe8-bc5c803fc789"
  },
  "<key>=18a83b70-5388-4405-bdd8-5a84d53002b3": {
    "edge_302b3": "e7f22915-2230-4f27-af78-7967c463df62",
    "edge_102b3": "5e8c5aec-d547-45a7-a9c6-3c1f2768c6ec",
    "edge_202b3": "56967a18-e437-4884-8a7d-d74c5cfc7173"
  },
  "<key>=0623c289-ce76-4c7a-a631-d141b18b7ff6": {
    "edge_37ff6": "5e8c5aec-d547-45a7-a9c6-3c1f2768c6ec",
    "edge_17ff6": "57d6e1ee-5989-45c8-8778-57df3465da5b",
    "edge_27ff6": "86db5ce0-ea2a-49a8-9f48-01d69b7a224c"
  },
  "<key>=3f8aee6f-9dac-43d8-849e-c2f361af7791": {
    "edge_37791": "829333df-77b1-4916-922d-3e271ef5f068",
    "edge_17791": "a0ed9513-b7ae-4d3b-81d4-771e4b469534",
    "edge_27791": "6f5f2dc4-5087-42e4-9416-9a6fadac8bf9"
  },
  "<key>=a1338458-f9e0-440e-b939-8f09ae60b051": {
    "edge_3b051": "99548187-0c23-4f17-9a0e-96ed07a70ae1",
    "edge_1b051": "06d987f0-0fd5-4191-a8b9-6adcab652ebf",
    "edge_2b051": "626935d0-d34b-4f2d-b0c9-c32d8e64a3a3"
  },
  "<key>=9b35f25b-a630-4e77-b073-17c97238ad22": {
    "edge_3ad22": "b0523b95-e6c6-44b7-a78a-a93ac758f8c9",
    "edge_1ad22": "e19fe11d-5f8f-4688-a704-9b2c61e5e139",
    "edge_2ad22": "3447b69b-2a4e-4781-8c5b-b19837d942ff"
  },
  "<key>=d2e6eb02-fea5-4d42-a1c0-bf22d26e6b0e": {
    "edge_36b0e": "f9ae9f63-821e-4420-9eb2-8e65a19eb1bd",
    "edge_16b0e": "18a83b70-5388-4405-bdd8-5a84d53002b3",
    "edge_26b0e": "5e8c5aec-d547-45a7-a9c6-3c1f2768c6ec"
  },
  "<key>=d720b947-fafb-46da-91ff-9f2b3f9b52a4": {
    "edge_352a4": "12ddf920-3bb3-418b-a966-90e52cdc3a20",
    "edge_152a4": "9b35f25b-a630-4e77-b073-17c97238ad22",
    "edge_252a4": "e19fe11d-5f8f-4688-a704-9b2c61e5e139"
  },
  "<key>=5e8c5aec-d547-45a7-a9c6-3c1f2768c6ec": {
    "edge_3c6ec": "a6d4d8e8-e4dd-46dd-b0d6-fc96beb69b70",
    "edge_1c6ec": "56967a18-e437-4884-8a7d-d74c5cfc7173",
    "edge_2c6ec": "15755e62-69a2-4eac-b215-125dafe8c0dd"
  },
  "<key>=3031d870-8f1f-4fea-ad9e-6fbe41aad195": {
    "edge_3d195": "626935d0-d34b-4f2d-b0c9-c32d8e64a3a3",
    "edge_1d195": "ffcefb18-bdcb-437c-972a-e86d87cab1ef",
    "edge_2d195": "d1483b4a-0d77-468d-98d4-5b785748ae0b"
  },
  "<key>=3e298c35-2a95-4ff1-842b-73341c7620a5": {
    "edge_320a5": "5100561d-3608-45dd-9b7c-22bdc15d24ec",
    "edge_120a5": "3f8aee6f-9dac-43d8-849e-c2f361af7791",
    "edge_220a5": "a0ed9513-b7ae-4d3b-81d4-771e4b469534"
  },
  "<key>=e977d57b-2f5f-409b-ac3e-e2b285b302fa": {
    "edge_302fa": "d1483b4a-0d77-468d-98d4-5b785748ae0b",
    "edge_102fa": "3e298c35-2a95-4ff1-842b-73341c7620a5",
    "edge_202fa": "3f8aee6f-9dac-43d8-849e-c2f361af7791"
  },
  "<key>=4173a0d3-0cd2-459a-b221-824de7736731": {
    "edge_16731": "5ceae0f2-ce30-4e85-904f-c53dd3ebee5e",
    "edge_26731": "ce49ce9a-701d-4103-bd3b-6f22a905deb3"
  },
  "<key>=beaa42ba-808e-4416-aa20-8adf153934ec": {
    "edge_334ec": "4125f52a-cbce-40e5-a640-a3c82c6b3139",
    "edge_134ec": "b4092713-0781-4494-9704-872e83f5df2e",
    "edge_234ec": "12ddf920-3bb3-418b-a966-90e52cdc3a20"
  },
  "<key>=8c2eb4a4-ed6d-4807-a7cf-4aa18c69c1fb": {
    "edge_3c1fb": "820ec180-4099-4c3b-866a-83b86a7264ff",
    "edge_1c1fb": "d9d0388b-b7cf-4ab5-935d-565993fcabff",
    "edge_2c1fb": "beaa42ba-808e-4416-aa20-8adf153934ec"
  },
  "<key>=162d105b-042d-44bd-b18c-d5fc74409021": {
    "edge_39021": "9b35f25b-a630-4e77-b073-17c97238ad22"
  },
  "<key>=3447b69b-2a4e-4781-8c5b-b19837d942ff": {
    "edge_342ff": "d720b947-fafb-46da-91ff-9f2b3f9b52a4",
    "edge_142ff": "162d105b-042d-44bd-b18c-d5fc74409021"
  },
  "<key>=e19fe11d-5f8f-4688-a704-9b2c61e5e139": {
    "edge_3e139": "74b0da55-6d78-4213-afe8-bc5c803fc789",
    "edge_1e139": "3447b69b-2a4e-4781-8c5b-b19837d942ff",
    "edge_2e139": "162d105b-042d-44bd-b18c-d5fc74409021"
  },
  "<key>=abb31621-13f8-44de-9416-3ec890bdc8fd": {
    "edge_3c8fd": "0623c289-ce76-4c7a-a631-d141b18b7ff6",
    "edge_1c8fd": "99548187-0c23-4f17-9a0e-96ed07a70ae1",
    "edge_2c8fd": "c59cecd9-c579-4c0a-bd96-03e470eb0692"
  },
  "<key>=99548187-0c23-4f17-9a0e-96ed07a70ae1": {
    "edge_30ae1": "57d6e1ee-5989-45c8-8778-57df3465da5b",
    "edge_10ae1": "c59cecd9-c579-4c0a-bd96-03e470eb0692",
    "edge_20ae1": "a21ad503-1781-4971-8b40-beb07676d196"
  }
}
"""
    return source_str

def generateGraphWithoutLabels(total_node_num, edge_prefix="edge_", fanin_num=1, fanout_num=2, unique_key_name="", unique_edge_name=False, simple_names=False):
    if simple_names:
        all_nodes = ["node_"+str(i) for i in range(total_node_num)]
    else:
        all_nodes = [str(uuid.uuid4()) for i in range(total_node_num)]
    columns=["id", "name"]
    node_info = []

    for i in range(total_node_num):
        node_info.append([i, all_nodes[i]])
    node_df = pd.DataFrame(node_info, columns=columns)

    json_graph = {}
    edges = []
    for i in range(total_node_num):
        updateNodeWithoutLabels(edges, i, edge_prefix, total_node_num, all_nodes, json_graph, fanin_num, fanout_num, unique_key_name, unique_edge_name)

    edge_df = pd.DataFrame(edges, columns=['from', 'to', 'weigth', 'strength'])

    # sort json
    # sorted_json_graph = {}
    # for k, v in json_graph.items():
    #     v = dict(sorted(v.items(), key=lambda item: item[0]))
    #     sorted_json_graph[k] = v
    
    # randomize the order of the nodes, so they don't always find the answer from the nearest node.
    keys = list(json_graph.keys())
    random.shuffle(keys)
    sorted_json_graph = {}
    for key in keys:
        sorted_json_graph[key] = json_graph[key]

    # source_str = existingGraph(node_num=total_node_num, fanin=fanin_num, fanout=fanout_num)
    # if source_str != "":
    #     sorted_json_graph = json.loads(source_str)

    return sorted_json_graph, edge_df, node_df, node_info


def generateGraphByPredicates(total_edges_num, total_node_num, max_node_to_edgeNum=3, edge_to_tNodeNum=1, unique_key_name="", simple_names=False):
    if simple_names:
        all_edges = ["edge_"+str(i) for i in range(total_edges_num)]
        all_nodes = ["node_"+str(i) for i in range(total_node_num)]
    else:
        all_edges = [str(uuid.uuid4()) for i in range(total_edges_num)]
        all_nodes = [str(uuid.uuid4()) for i in range(total_node_num)]

    columns=["id", "name"]
    node_data = []
    node_dict = {}
    json_graph = {}
    json_graph_by_edge = {}
    for i in range(total_node_num):
        name = all_nodes[i]
        node_data.append([i, name])
        name = unique_key_name+name
        node_dict[name] = i
        json_graph[name] = {}
    node_df = pd.DataFrame(node_data, columns=columns)

    for i in range(total_edges_num):
        json_graph_by_edge[all_edges[i]] = {}
    
    edges = []
    edge_set = set()
    # for i, edge in enumerate(all_edges):
    #     temp_nodes = all_nodes.copy()
    #     startNodes = random.sample(temp_nodes, max_fanin)
    #     for s_node in startNodes: # for each start node, create some fanout nodes
    #         temp_nodes.remove(s_node)
    #         endNodes = random.sample(temp_nodes, max_fanout)
    #         for e_node in endNodes:
    #             if (s_node, e_node) in edge_set:
    #                 continue
    #             json_node = json_graph.get(s_node, {})
    #             if edge not in json_node:
    #                 json_node[edge] = []
    #             json_node[edge].append(e_node)
    #             edges.append((node_dict[s_node], node_dict[e_node], 10, "medium"))
    #             edge_set.add((s_node, e_node))
    #             json_graph.update({s_node: json_node})
    for i, node in enumerate(all_nodes):
        temp_nodes = all_nodes.copy()
        temp_nodes.remove(node)
        node = unique_key_name+node
        chosen_edges = random.sample(all_edges, random.randint(1, max_node_to_edgeNum))
        for edge in chosen_edges:
            target_nodes = random.sample(temp_nodes, edge_to_tNodeNum)
            for j, target_node in enumerate(target_nodes):
                if (node, target_node) in edge_set:
                    continue
                if target_node in node: # avoid self loop, substring match
                    continue
                json_node = json_graph.get(node, {})
                if edge not in json_node:
                    json_node[edge] = []
                json_node[edge].append(target_node)
                edges.append((node_dict[node], node_dict[unique_key_name+target_node], 10, "medium"))
                edge_set.add((node, target_node))
                json_graph.update({node: json_node})

                # update json by edge
                json_edge = json_graph_by_edge.get(edge, {})
                if node not in json_edge:
                    json_edge[node] = []
                json_edge[node].append(target_node)
                json_graph_by_edge.update({edge: json_edge})

    edge_df = pd.DataFrame(edges, columns=['from', 'to', 'weigth', 'strength'])

    # sort json
    keys = list(json_graph.keys())
    random.shuffle(keys)
    sorted_json_graph = {}
    for key in keys:
        sorted_json_graph[key] = json_graph[key]
    # sorted_json_graph = dict(sorted(json_graph.items(), key=lambda item: item[0]))
    # for k, v in sorted_json_graph.items():
    #     v = dict(sorted(v.items(), key=lambda item: item[0]))
    #     sorted_json_graph[k] = v

    return sorted_json_graph, json_graph_by_edge, edge_df, node_df


def test1():
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(10, fanin_num=2, fanout_num=3, unique_key_name="", unique_edge_name=False)
    json_str = json.dumps(json_graph, indent=2)
    print(json_str)

    Jaal(edge_df, node_df).plot(directed=True)

def test2(simple_names=False):
    json_graph, json_edge_grah, edge_df, node_df = generateGraphByPredicates(total_edges_num=20, total_node_num=50, max_node_to_edgeNum=3, edge_to_tNodeNum=1, simple_names=simple_names)
    json_str = json.dumps(json_graph, indent=2)
    json_edge_str = json.dumps(json_edge_grah, indent=2)
    print(json_str)
    print(json_edge_str)

    Jaal(edge_df, node_df).plot(directed=True)

# test2(simple_names=True)

    


def GenDAGImpl(N, p, w_min, w_max, n_min, n_max):
    # Create a directed acyclic graph
    G = nx.DiGraph()
    
    # Add N nodes in topological order
    nodes = list(range(N))
    G.add_nodes_from(nodes)
    
    # For each node, consider edges to all subsequent nodes
    for i in range(N):
        for j in range(i+1, N):
            # Add edge with probability p
            if random.random() < p:
                # Generate random weight and noise standard deviation
                weight = random.uniform(w_min, w_max)
                noise_std = random.uniform(n_min, n_max)
                
                # Add edge with attributes
                G.add_edge(i, j, weight=weight, noise_std=noise_std)
    
    return G


def GenDataImpl(G, L, v_min, v_max):
    # Get the number of nodes in the graph
    N = G.number_of_nodes()
    
    # Initialize the dataset
    dataset = np.zeros((L, N))
    
    # Identify source nodes (nodes with no incoming edges)
    source_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
    
    # Generate L data points
    for i in range(L):
        # Assign random values to source nodes
        for node in source_nodes:
            dataset[i, node] = np.random.uniform(v_min, v_max)
        
        # Process nodes in topological order
        for node in nx.topological_sort(G):
            if node not in source_nodes:
                # Calculate value based on incoming edges
                incoming_values = []
                for pred in G.predecessors(node):
                    edge_data = G[pred][node]
                    weight = edge_data['weight']
                    noise_std = edge_data['noise_std']
                    
                    # Multiply predecessor's value by edge weight and add noise
                    value = dataset[i, pred] * weight
                    value += np.random.normal(0, noise_std)
                    incoming_values.append(value)
                
                # Sum up all incoming values
                dataset[i, node] = sum(incoming_values)
    
    return dataset


def GenData():
  # Example usage (assuming we have a graph G from GenDAG)
  L = 1000  # Number of data points
  v_min, v_max = -1, 1  # Range for source node values

  N = 20  # Number of nodes
  p = 0.5  # Probability of edge creation
  w_min, w_max = 1, 10  # Range for edge weights
  n_min, n_max = 0.001, 2  # Range for noise standard deviations

  G = GenDAGImpl(N, p, w_min, w_max, n_min, n_max)
  # data = GenDataImpl(G, L, v_min, v_max)

  print(f"Number of nodes: {G.number_of_nodes()}")
  print(f"Number of edges: {G.number_of_edges()}")
  print("\nEdge details:")
  for edge in G.edges(data=True):
      print(f"Edge {edge[0]} -> {edge[1]}: weight={edge[2]['weight']:.2f}, noise_std={edge[2]['noise_std']:.2f}")
      
  # # Print some information about the generated dataset
  # print(f"Dataset shape: {data.shape}")
  # print("\nFirst few rows of the dataset:")
  # print(data[:5])

  # # Calculate and print some basic statistics
  # print("\nDataset statistics:")
  # print(f"Mean: {np.mean(data, axis=0)}")
  # print(f"Standard deviation: {np.std(data, axis=0)}")
  # print(f"Min: {np.min(data, axis=0)}")
  # print(f"Max: {np.max(data, axis=0)}")


def generate_ws_graph_impl(n, k, p):
    """Generates a Watts-Strogatz small-world graph.

    Args:
        n: Number of nodes.
        k: Each node is connected to k nearest neighbors in a ring lattice.
        p: Probability of rewiring each edge.

    Returns:
        A NetworkX Graph object.
    """

    # G = nx.watts_strogatz_graph(n, k, p, seed=None)
    G = nx.connected_watts_strogatz_graph(n, k, p, seed=None)
    return G

def generate_and_save_ws_graph(n=10, k=4, p=0.05):
  """
   n: Number of nodes
   k: Each node is connected to k nearest neighbors
   p: Probability of rewiring each edge
  """
  print(n, k, p)
  json_graph = {}
  all_nodes = [str(uuid.uuid4()) for _ in range(n)]
  ws_graph = generate_ws_graph_impl(n, k, p)
  print(f"Number of nodes: {ws_graph.number_of_nodes()}")
  print(f"Number of edges: {ws_graph.number_of_edges()}")
  print("\nEdge details:")
  for edge in ws_graph.edges(data=True):
      print(f"Edge {edge[0]} -> {edge[1]}")
      this_node = all_nodes[edge[0]]
      if this_node not in json_graph:
        json_graph[this_node] = {}
      edge_num = len(json_graph[this_node])
      json_graph[this_node][f"edge_{edge_num}"] = all_nodes[edge[1]]
  
  keys = list(json_graph.keys())
  random.shuffle(keys)
  sorted_json_graph = {}
  for key in keys:
      sorted_json_graph[key] = json_graph[key]
  json_str = json.dumps(sorted_json_graph, indent=2)
  print(json_str)
  # file_name = f"graph_n{n}_k{k}_p{p*100}.txt"
  # if os.path.exists(file_name):
  #     print("File already exists!", file_name)
  #     return

  # f = open(file_name, "a")
  # f.write(json.dumps(json_graph, indent=2))
  # f.close()


def gnp_random_graph(n, p):
  json_graph = {}
  all_nodes = [str(uuid.uuid4()) for _ in range(n)]
  g = nx.gnp_random_graph(n, p, directed=True)
  print(f"Number of nodes: {g.number_of_nodes()}")
  print(f"Number of edges: {g.number_of_edges()}")
  print("\nEdge details:")
  for edge in g.edges(data=True):
      print(f"Edge {edge[0]} -> {edge[1]}")
      this_node = all_nodes[edge[0]]
      if this_node not in json_graph:
        json_graph[this_node] = {}
      edge_num = len(json_graph[this_node])
      json_graph[this_node][f"edge_{edge_num}"] = all_nodes[edge[1]]
      # if edge[0] not in json_graph:
      #     json_graph[edge[0]] = {}
      # edge_num = len(json_graph[edge[0]])
      # json_graph[edge[0]][f"edge_{edge_num}"] = edge[1]

  keys = list(json_graph.keys())
  random.shuffle(keys)
  sorted_json_graph = {}
  for key in keys:
      sorted_json_graph[key] = json_graph[key]
  json_str = json.dumps(sorted_json_graph, indent=2)
  
  print(json_str)
  return json_str



def gen_graph_and_save_to_file(n, p):
  g = gnp_random_graph(n, p)
  file_name = f"gnp_n{n}_p{int(p*100)}.txt"
  if os.path.exists(file_name):
      print("File already exists!", file_name)
      return

  f = open(file_name, "a")
  f.write(g)
  f.close()

# gen_graph_and_save_to_file(25, p=0.5)


# GenData()
