import os
import sys

from typing import Any, Dict

import json
import pandas as pd
from io import BytesIO

import data_integration_demo as did
from agents_lib import agent_util as agents
from generate_graph import generateGraphWithoutLabels
from graph_prompts import create_prompt_1hop, create_prompt_2hop, create_prompt_1hop_1toN
from retrieval_graph import compare_list
from random import choice
from string import ascii_lowercase

import pandas as pd

def extract_final_value(nested_dict):
  if not isinstance(nested_dict, dict):
    return nested_dict

  for key, value in nested_dict.items():
    if isinstance(value, dict):
      # If the value is a dictionary, continue traversing
      result = extract_final_value(value)
      if result is not None:
        return result

  return None

PROMPT_2HOP = """
Please extract the value for "{source_node_name}"-->"{predicate1}" as V1, keep V1 in memory, and then use V1 as the key to get the final value V2 for V1--> "{predicate2}", please put the final answer V2 in JSON format.
Be concise. For example: {{"{source_node_name}": V2}}.

DataSource is below:
  """

Learnings = ""


PROMPT_1HOP_baseline = """
Task: Extract the value for "{source_node_name}"-->"{predicate}", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
DataSource is below:
{json_str}
  """



PROMPT_1HOP_RL = """
Your goal is to maximize the score of the following task:
<example>
Task: Extract the value for "{unique_key_name}node_12"-->"edge_3", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
DataSource is below:
{{
  "{unique_key_name}node_11": {{
    "edge_13": "node_0",
    "edge_3": "node_32"
  }},
  "{unique_key_name}node_12": {{
    "edge_3": "node_41",
    "edge_4": "node_13"
  }}
}}

Answer:
    Step1: Extract the value for "{unique_key_name}node_12", the result is {{"edge_3": "node_41", "edge_4": "node_13"}}. Please rethink it if the answer is not correct.
    Step2: Extract the value for "edge_3" in {{"edge_3": "node_41", "edge_4": "node_13"}}, the result is "node_41". Please rethink it if the answer is not correct.
    Step3: Put the final answer in JSON format: {{"{unique_key_name}node_12": "node_41"}}. Please rethink it if the answer is not correct.

The final answer is: {{"{unique_key_name}node_12": "node_41"}}
</example>

Task: Extract the value for "{source_node_name}"-->"{predicate}", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
DataSource is below:
{json_str}
  """


PROMPT_1HOP_feedback = """
Task: Extract the value for "{source_node_name}"-->"{predicate}", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
<Feedback>
1. You need to locate the "{source_node_name}" in the DataSource and extract the value for it, make sure it's correct.
</feedback>
DataSource is below:
{json_str}
  """


PROMPT_1HOP_1shot = """
Your goal is to maximize the score of the following task:
<example>
Task: Extract the value for "{unique_key_name}node_12" --> "edge_3", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
DataSource is below:
{{
  "{unique_key_name}node_11": {{
    "edge_13": "node_0",
    "edge_3": "node_32"
  }},
  "{unique_key_name}node_12": {{
    "edge_3": "node_41",
    "edge_4": "node_13"
  }}
}}

A: Firstly, extract "{unique_key_name}node_12" from the DataSource, the result is {{"edge_3": "node_41", "edge_4": "node_13"}}.
Secondly, extract the value for "edge_3" in {{"edge_3": "node_41", "edge_4": "node_13"}}, the result is "node_41".
Finally, put the final answer in JSON format: {{"{unique_key_name}node_12": "node_41"}}.

The answer is: {{"{unique_key_name}node_12": "node_41"}}
</example>

Task: Extract the value for "{source_node_name}"-->"{predicate}", and put the final answer in JSON format. e.g. {{"{source_node_name}": VALUE}}
DataSource is below:
{json_str}
  """

# answer2: Total Score = 1
#     Step1 [Score: 1]: Extract the value for "{unique_key_name}node_12", the result is {{"edge_3": "node_41", "edge_4": "node_13"}}
#     Step2 [Score: 0]: Extract the value for "edge_4" in {{"edge_3": "node_41", "edge_4": "node_13"}}, the result is "node_13"
#     Step3 [Score: 0]: Put the final answer in JSON format: {{"{unique_key_name}node_12": "node_13"}}

# answer3: Total Score = 0
#     Step1 [Score: 0]: Extract the value for "{unique_key_name}node_12", the result is {{"edge_3": "node_32"}} 
#     Step2 [Score: 0]: Extract the value for "edge_3" in {{"edge_3": "node_32"}}, the result is "node_32"
#     Step3 [Score: 0]: Put the final answer in JSON format: {{"{unique_key_name}node_12": "node_32"}}


def generateRawGraphToFile(node_num=50):
    json_graph, _, _, node_info = generateGraphWithoutLabels(node_num)
    file_name = f"node_num_{node_num}_b6.txt"
    if os.path.exists(file_name):
        print("File already exists!", file_name)
        return

    f = open(file_name, "a")
    f.write(json.dumps(json_graph, indent=2))
    f.close()


def generateRawGraphToFile_12(node_num=20):
    json_graph, _, _, node_info = generateGraphWithoutLabels(node_num, fanin_num=2, fanout_num=4)
    file_name = f"node_num_{node_num}_b12.txt"
    if os.path.exists(file_name):
        print("File already exists!", file_name)
        return

    f = open(file_name, "a")
    f.write(json.dumps(json_graph, indent=2))
    f.close()

def LoadJsonGraphFromFile(file_name):
    with open(file_name) as f:
        json_data = json.load(f)
    return json_data


def LoadJsonGraphFromFile(file_name):
    with open(file_name) as f:
        json_data = json.load(f)
    return json_data


def different_tokens_edge(file_name, position="before"):
    json_graph = LoadJsonGraphFromFile(file_name)
    pure_json_str = json.dumps(json_graph, indent=2)
    raw_keys = list(json_graph.keys())

    substring_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            if position == "after":
                new_sub_dict[sub_key + key[-4:]] = value[sub_key]
            elif position == "before":
                new_sub_dict[key[-4:] + sub_key] = value[sub_key]
            else:
                new_sub_dict[key[-4:] + sub_key + key[-4:]] = value[sub_key]
        substring_key_json[key] = new_sub_dict
    substring_key_json_str = json.dumps(substring_key_json, indent=2)

    full_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            if position == "after":
                new_sub_dict[sub_key + key] = value[sub_key]
            elif position == "before":
                new_sub_dict[key + sub_key] = value[sub_key]
            else:
                new_sub_dict[key + sub_key + key] = value[sub_key]
        full_key_json[key] = new_sub_dict
    full_key_json_str = json.dumps(full_key_json, indent=2)

    random_token_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        unique_string = ''.join(choice(ascii_lowercase) for i in range(4))
        for sub_key in value.keys():
            if position == "after":
                new_sub_dict[sub_key + unique_string] = value[sub_key]
            elif position == "before":
                new_sub_dict[unique_string + sub_key] = value[sub_key]
            else:
                new_sub_dict[unique_string + sub_key + unique_string] = value[sub_key]
        random_token_json[key] = new_sub_dict
    random_token_json_str = json.dumps(random_token_json, indent=2)

    wrapper_token_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            new_sub_dict["<"+sub_key+">"] = value[sub_key]
        wrapper_token_json[key] = new_sub_dict
    wrapper_token_json_str = json.dumps(wrapper_token_json, indent=2)


    substring_keyhead_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            if position == "after":
                new_sub_dict[sub_key + key[0:4]] = value[sub_key]
            elif position == "before":
                new_sub_dict[key[0:4] + sub_key] = value[sub_key]
            else:
                new_sub_dict[key[0:4] + sub_key + key[0:4]] = value[sub_key]
        substring_keyhead_json[key] = new_sub_dict
    substring_keyhead_json_str = json.dumps(substring_keyhead_json, indent=2)


    primary_key_substring_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            if position == "after":
                new_sub_dict[sub_key + key[0:4]] = value[sub_key]
            elif position == "before":
                new_sub_dict[key[0:4] + sub_key] = value[sub_key]
            else:
                new_sub_dict[key[0:4] + sub_key + key[0:4]] = value[sub_key]
        primary_key_substring_key_json["<key>="+key] = new_sub_dict
    primary_key_substring_key_json_str = json.dumps(primary_key_substring_key_json, indent=2)
    
    # print(pure_json_str)
    # print(substring_key_json_str)
    # print(full_key_json_str)
    # print(random_token_json_str)
    # print(wrapper_token_json_str)

    return json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json


def different_token_position_edge(file_name):
    json_graph = LoadJsonGraphFromFile(file_name)
    pure_json_str = json.dumps(json_graph, indent=2)
    raw_keys = list(json_graph.keys())

    after_substring_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            new_sub_dict[sub_key + key[-4:]] = value[sub_key]
        after_substring_key_json[key] = new_sub_dict
    after_substring_key_json_str = json.dumps(after_substring_key_json, indent=2)

    before_substring_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            new_sub_dict[key[-4:] + sub_key] = value[sub_key]
        before_substring_key_json[key] = new_sub_dict
    before_substring_key_json_str = json.dumps(before_substring_key_json, indent=2)

    both_substring_key_json = {}
    for key in raw_keys:
        value = json_graph[key]
        new_sub_dict = {}
        for sub_key in value.keys():
            new_sub_dict[key[-4:] + sub_key + key[-4:]] = value[sub_key]
        both_substring_key_json[key] = new_sub_dict
    both_substring_key_json_str = json.dumps(both_substring_key_json, indent=2)

    # print(pure_json_str)
    # print(before_substring_key_json_str)
    # print(after_substring_key_json_str)
    # print(both_substring_key_json_str)

    return json_graph, before_substring_key_json, after_substring_key_json, both_substring_key_json


def test_1hop_rl(model, json_graph, shot_num=0, is_abs=True, prompt_type="rl"):
    json_str = json.dumps(json_graph, indent=2)
    planner = did.Planner([model], model) #agents.TogetherCall(model, stop_words=stop_words)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    for i, name in enumerate(json_graph.keys()):
        for j, predicate in enumerate(json_graph[name]):
            # one_hop_node = json_graph[name][predicate1]
            # if "<key>=" in name:
            #     one_hop_node = "<key>=" + one_hop_node
            # for k, predicate2 in enumerate(json_graph[one_hop_node]):
            full_score += 1
            expected_target_node = json_graph[name][predicate]
            print(i, name, predicate, expected_target_node)
            # if "<key>=" in name:
            #     unique_key_name = "<key>="
            # else:
            #     unique_key_name = ""
            if shot_num > 0:
                prompt = create_prompt_1hop(json_str, name, predicate, shot_num=1, is_abs=True)
            if prompt_type == "feedback":
                prompt = PROMPT_1HOP_feedback.format(unique_key_name="", source_node_name=name, predicate=predicate, json_str=json_str)
            elif prompt_type == "rl":
                prompt = PROMPT_1HOP_RL.format(unique_key_name="", source_node_name=name, predicate=predicate, json_str=json_str)
            elif prompt_type == "1shot":
                prompt = PROMPT_1HOP_1shot.format(unique_key_name="", source_node_name=name, predicate=predicate, json_str=json_str)
            else:
                prompt = PROMPT_1HOP_baseline.format(source_node_name=name, predicate=predicate, json_str=json_str)

            if i == 0 and j == 0:
                print(prompt)
            response = planner.simple_ask(prompt)
            response.replace("\\", "")
            tmp = []
            try:
                json_answer = agents.getJsonFromAnswer(response)
            except Exception as e:
                print("failed to parse json answer!", i, name, "<<<", response, ">>>")
                json_answer = {}
            if isinstance(json_answer, str):
                tmp = json_answer
            else:
                for key in json_answer:
                    if key == name or key == "source_node_name" or key == predicate or key == "$FINAL_VALUE":
                        tmp = json_answer[key]
                        if isinstance(tmp, dict):
                            tmp = extract_final_value(tmp)

            score = compare_list(expected_target_node, tmp) 
            total_score += score
            # if score < 1:
            #     print("++++++ raw output", response, json_answer, expected_target_node, tmp, score, "\n")

            print("++++++ expected", expected_target_node, tmp, score)
            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary

 
    print("++++++++++++++++++++++++++++++", model, json_str[:100], len(json_graph))
    print(total_score, full_score, total_score/float(full_score))
    print(distribution)
    print(final_output)


def rl_one_hop(graph_file_name, position="before"):
    json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json = different_tokens_edge(graph_file_name, position)

    # test_1hop_rl("mistralai/Mistral-7B-Instruct-v0.3", substring_keyhead_json, shot_num=1) #0.58
    # test_1hop_rl("mistralai/Mistral-7B-Instruct-v0.3", json_graph, prompt_type="") # 20
    # test_1hop_rl("mistralai/Mistral-7B-Instruct-v0.3", json_graph, prompt_type="feedback") #22
    # test_1hop_rl("mistralai/Mistral-7B-Instruct-v0.3", json_graph, prompt_type="rl") # 19
    # test_1hop_rl("mistralai/Mistral-7B-Instruct-v0.3", json_graph, prompt_type="1shot") # 20
    
    # test_1hop_rl(agents.Model.MIXTRAL, json_graph, prompt_type="") # 9
    # test_1hop_rl(agents.Model.MIXTRAL, substring_keyhead_json, prompt_type="feedback") # 3
    # test_1hop_rl(agents.Model.MIXTRAL, substring_keyhead_json, prompt_type="rl") # 23
    # test_1hop_rl(agents.Model.MIXTRAL, substring_keyhead_json, prompt_type="1shot") # 21
    # test_1hop_rl(agents.Model.MIXTRAL, json_graph, shot_num=0)
    # test_1hop_rl("meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", substring_keyhead_json, shot_num=1, prompt_type="feedback")
    # test_1hop_rl("meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", substring_keyhead_json, shot_num=1, prompt_type="rl")
    # test_1hop_rl("meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", substring_keyhead_json, shot_num=1, prompt_type="1shot")
    # test_1hop_rl("meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", json_graph, shot_num=0)


rl_one_hop("node_num_10_b6.txt", position="before")
    

