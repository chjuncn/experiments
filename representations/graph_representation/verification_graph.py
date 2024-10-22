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


def test_1hop(model, raw_json_graph, updated_json_graph, stop_words="", shot_num=0, is_abs=False, error_log_file=""):
    if error_log_file != "":
        error_log_file += model[0:20] + ".txt"
    updated_json_str = json.dumps(updated_json_graph, indent=2)
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    all_error_message = ""
    for i, name in enumerate(raw_json_graph.keys()):
        for j, predicate in enumerate(raw_json_graph[name]):
            full_score += 1
            expected_target_node = raw_json_graph[name][predicate]
            print(i, name, predicate, expected_target_node)
            prompt = create_prompt_1hop(updated_json_str, name, predicate, "", shot_num=shot_num, is_abs=is_abs)
            if i == 0:
                print(prompt)
                all_error_message += prompt + "\n"
            response = planner.simple_ask(prompt)
            response.replace("\\", "")
            tmp = []
            try:
                json_answer = agents.getJsonFromAnswer(response)
            except Exception as e:
                error_message = "failed to parse json answer!" + str(e) + "i, name, " + str(i) + ", name=" + str(name) + ", predicate=" + str(predicate) + ", response=" + str(response) + "\n"
                print(error_message)
                json_answer = {}
            if isinstance(json_answer, str):
                tmp = json_answer
            else:
                for key in json_answer:
                    if key == name or key == "source_node_name" or key == predicate or key == "$FINAL_VALUE":
                        tmp = json_answer[key]
                        if isinstance(tmp, dict):
                            tmp = list(tmp.values())

            score = compare_list(expected_target_node, tmp) 
            total_score += score
            if score < 1:
                error_message = "++++++ raw output" + str(response) + ", " + str(json_answer) + ", " + str(expected_target_node) + ", " +str(tmp) + ", " +str(score) + "\n"
                print(error_message)
                all_error_message += error_message

            error_message = "++++++ expected" + ", " + str(expected_target_node) + ", " +str(tmp) + ", " + str(score) + "\n"
            all_error_message += error_message
            print(error_message)

            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary


    print("++++++++++++++++++++++++++++++", model, updated_json_str[:100], len(updated_json_graph), len(updated_json_str))
    print(total_score, full_score, total_score/float(full_score))
    print(distribution)
    print(final_output)

    f = open("one_hop_performance.txt", "a")
    message = "++++++++++++++++++++++++++++++"+str(model)+", "+str(updated_json_str[:200])+"\n"
    message += str(len(updated_json_graph))+", " + str(len(prompt)) + "\n"
    message += str(total_score)+", "+str(full_score)+","+str(total_score/float(full_score))+"\n"
    # message += str(distribution)+"\n"
    message += final_output + "\n\n\n"
    f.write(message)
    f.close()


    if error_log_file != "":
        f = open(error_log_file, "a")
        all_error_message += message
        f.write(all_error_message)
        f.close()


def test_2hop(model, raw_json_graph, updated_json_graph, stop_words="", shot_num=0, is_abs=True, error_log_file=""):
    if error_log_file != "":
        error_log_file += model[0:20] + ".txt"
    updated_json_str = json.dumps(updated_json_graph, indent=2)
    planner = did.Planner([model], model) #agents.TogetherCall(model, stop_words=stop_words)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    all_error_message = ""
    error_message = ""
    for i, name in enumerate(raw_json_graph.keys()):
        for j, predicate1 in enumerate(raw_json_graph[name]):
            one_hop_node = raw_json_graph[name][predicate1]
            for k, predicate2 in enumerate(raw_json_graph[one_hop_node]):
                full_score += 1
                expected_target_node = raw_json_graph[one_hop_node][predicate2]
                print(i, name, predicate1, one_hop_node, predicate2, expected_target_node)
                # if "<key>=" in name:
                #     unique_key_name = "<key>="
                # else:
                #     unique_key_name = ""
                prompt = create_prompt_2hop(updated_json_str, name, predicate1, predicate2, unique_key_name="", shot_num=shot_num, is_abs=is_abs)
                if i == 0 and j == 0 and k==0:
                    print(prompt)
                    all_error_message += prompt + "\n"
                response = planner.simple_ask(prompt)
                response.replace("\\", "")
                tmp = []
                try:
                    json_answer = agents.getJsonFromAnswer(response)
                except Exception as e:
                    # print("failed to parse json answer!", i, name, "<<<", response, ">>>")
                    json_answer = {}
                if isinstance(json_answer, str):
                    tmp = json_answer
                else:
                    for key in json_answer:
                        if key == name or key == "source_node_name" or key == predicate1 or key == "$FINAL_VALUE" or key == predicate2:
                            tmp = json_answer[key]
                            if isinstance(tmp, dict):
                                tmp = extract_final_value(tmp)

                score = compare_list(expected_target_node, tmp) 
                total_score += score
                if score < 1:
                    print("++++++ raw output", response)
                    print(json_answer)
                    print(expected_target_node, tmp, score)

                    error_message = "++++++ raw output" + ", " +str(response) + ", " +str(json_answer)+ "\n"
                    all_error_message += error_message
                    print(error_message)

                print("++++++ expected", expected_target_node, tmp, score)
                all_error_message += "++++++ expected" + ", " + str(expected_target_node) + ", " +str(tmp) + ", " + str(score) + "\n"
                if str(score) not in distribution:
                    distribution[str(score)] = []
                distribution[str(score)].append(i)

                summary = str(i) + ","+ str(score) + "\n"
                final_output += summary

 
    print("++++++++++++++++++++++++++++++", model, updated_json_str[:100], len(prompt))
    print(total_score, full_score, total_score/float(full_score))
    print(distribution)
    print(final_output)
    
    f = open("two_hop_performance.txt", "a")
    message = "++++++++++++++++++++++++++++++"+str(model)+", "+str(updated_json_str[:100])+ ", " + str(len(updated_json_str)) + ", " + str(len(prompt))+"\n"
    message += str(total_score)+", "+str(full_score)+", "+str(total_score/float(full_score))+"\n"
    # message += str(distribution)+"\n"
    message += final_output + "\n\n\n"
    f.write(message)
    f.close()

    if error_log_file != "":
        f = open(error_log_file, "a")
        all_error_message += message
        f.write(all_error_message)
        f.close()



def different_appendingtokens_performance(graph_file_name, position="before", error_log_file=""):
    json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json = different_tokens_edge(graph_file_name, position)

    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,json_graph)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,substring_key_json)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, full_key_json)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, random_token_json)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,wrapper_token_json)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, substring_keyhead_json)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, primary_key_substring_key_json)

    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, json_graph)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, full_key_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, random_token_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, wrapper_token_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_keyhead_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, primary_key_substring_key_json)

    # test_1hop("google/gemma-2-9b-it", json_graph, json_graph)
    # test_1hop("google/gemma-2-9b-it", json_graph, substring_key_json)
    test_1hop("google/gemma-2-9b-it", json_graph, full_key_json)
    # test_1hop("google/gemma-2-9b-it", json_graph, random_token_json)
    # test_1hop("google/gemma-2-9b-it", json_graph, wrapper_token_json)
    # test_1hop("google/gemma-2-9b-it", json_graph, substring_keyhead_json)
    # test_1hop("google/gemma-2-9b-it", json_graph, primary_key_substring_key_json)

    # test_1hop("google/gemma-2-27b-it", json_graph, json_graph)
    # test_1hop("google/gemma-2-27b-it", json_graph, substring_key_json)
    test_1hop("google/gemma-2-27b-it", json_graph, full_key_json)
    # test_1hop("google/gemma-2-27b-it", json_graph, random_token_json)
    # test_1hop("google/gemma-2-27b-it", json_graph, wrapper_token_json)
    # test_1hop("google/gemma-2-27b-it", json_graph, substring_keyhead_json)
    # test_1hop("google/gemma-2-27b-it", json_graph, primary_key_substring_key_json)

    # test_1hop(agents.Model.MIXTRAL, json_graph, json_graph)
    # test_1hop(agents.Model.MIXTRAL, json_graph, substring_key_json)
    # test_1hop(agents.Model.MIXTRAL, json_graph, full_key_json)
    # test_1hop(agents.Model.MIXTRAL, json_graph, random_token_json)
    # test_1hop(agents.Model.MIXTRAL, json_graph, wrapper_token_json)
    # test_1hop(agents.Model.MIXTRAL, json_graph, substring_keyhead_json)
    # test_1hop(agents.Model.MIXTRAL, json_graph, primary_key_substring_key_json)

    print("\\\\\\\\\\\\\\\\n\n\n\n")
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, json_graph)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, full_key_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, random_token_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, wrapper_token_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_keyhead_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, primary_key_substring_key_json)

    # test_1hop("Qwen/Qwen2-72B-Instruct", json_graph)
    # test_1hop("Qwen/Qwen2-72B-Instruct", substring_key_json)
    # test_1hop("Qwen/Qwen2-72B-Instruct", full_key_json)
    # test_1hop("Qwen/Qwen2-72B-Instruct", random_token_json)
    # test_1hop("Qwen/Qwen2-72B-Instruct", wrapper_token_json)
    # test_1hop("Qwen/Qwen2-72B-Instruct", substring_keyhead_json)
    # test_1hop("Qwen/Qwen2-72B-Instruct", primary_key_substring_key_json)


def two_hop_performance(graph_file_name, position="before", shot_num=0):
    json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json = different_tokens_edge(graph_file_name, position)

    test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, json_graph, shot_num=shot_num)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", substring_key_json)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, full_key_json, shot_num=shot_num)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", random_token_json)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", wrapper_token_json)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, substring_keyhead_json, shot_num=shot_num)
    # test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, primary_key_substring_key_json, shot_num=shot_num)

    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, json_graph, shot_num=shot_num)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", substring_key_json)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, full_key_json, shot_num=shot_num)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", random_token_json)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", wrapper_token_json)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_keyhead_json, shot_num=shot_num)
    # test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, primary_key_substring_key_json, shot_num=shot_num)

    test_2hop("google/gemma-2-9b-it", json_graph, json_graph, shot_num=shot_num)
    # test_2hop("google/gemma-2-9b-it", substring_key_json)
    test_2hop("google/gemma-2-9b-it", json_graph, full_key_json, shot_num=shot_num)
    # test_2hop("google/gemma-2-9b-it", random_token_json)
    # test_2hop("google/gemma-2-9b-it", wrapper_token_json)
    test_2hop("google/gemma-2-9b-it", json_graph, substring_keyhead_json, shot_num=shot_num)
    test_2hop("google/gemma-2-9b-it", json_graph, primary_key_substring_key_json, shot_num=shot_num)

    test_2hop("google/gemma-2-27b-it", json_graph, json_graph, shot_num=shot_num)
    # test_2hop("google/gemma-2-27b-it", substring_key_json)
    test_2hop("google/gemma-2-27b-it", json_graph, full_key_json, shot_num=shot_num)
    # test_2hop("google/gemma-2-27b-it", random_token_json)
    # test_2hop("google/gemma-2-27b-it", wrapper_token_json)
    test_2hop("google/gemma-2-27b-it", json_graph, substring_keyhead_json, shot_num=shot_num)
    test_2hop("google/gemma-2-27b-it", json_graph, primary_key_substring_key_json, shot_num=shot_num)

    # test_2hop(agents.Model.MIXTRAL, json_graph)
    # test_2hop(agents.Model.MIXTRAL, substring_key_json)
    # test_2hop(agents.Model.MIXTRAL, full_key_json)
    # test_2hop(agents.Model.MIXTRAL, random_token_json)
    # test_2hop(agents.Model.MIXTRAL, wrapper_token_json)
    # test_2hop(agents.Model.MIXTRAL, substring_keyhead_json)
    # test_2hop(agents.Model.MIXTRAL, primary_key_substring_key_json)

    # print("\\\\\\\\\\\\\\\\n\n\n\n")
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", substring_key_json)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", full_key_json)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", random_token_json)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", wrapper_token_json)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", substring_keyhead_json)
    # test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", primary_key_substring_key_json)

    # test_2hop("Qwen/Qwen2-72B-Instruct", json_graph)
    # test_2hop("Qwen/Qwen2-72B-Instruct", substring_key_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", full_key_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", random_token_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", wrapper_token_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", substring_keyhead_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", primary_key_substring_key_json)


def different_token_position_performance(graph_file_name, position="after"):
    json_graph, before_substring_key_json, after_substring_key_json, both_substring_key_json = different_token_position_edge(graph_file_name, position)

    # test_1hop(agents.Model.MIXTRAL, json_graph)
    # test_1hop(agents.Model.MIXTRAL, before_substring_key_json)
    # test_1hop(agents.Model.MIXTRAL, after_substring_key_json)
    # test_1hop(agents.Model.MIXTRAL, both_substring_key_json)

    # # print("\\\\\\\\\\\\\\\\n\n\n\n")
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", before_substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", after_substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", both_substring_key_json)

    #     # print("\\\\\\\\\\\\\\\\n\n\n\n")
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", before_substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", after_substring_key_json)
    # test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", both_substring_key_json)

    test_1hop("google/gemma-2-27b-it", json_graph)
    test_1hop("google/gemma-2-27b-it", before_substring_key_json)
    test_1hop("google/gemma-2-27b-it", after_substring_key_json)
    test_1hop("google/gemma-2-27b-it", both_substring_key_json)



# two_hop_performance("node_num_10_b6.txt", shot_num=1)

# different_appendingtokens_performance("node_num_30_b6.txt")
# different_appendingtokens_performance("node_num_5_b12.txt")
# different_appendingtokens_performance("node_num_10_b12.txt")
different_appendingtokens_performance("node_num_20_b12.txt")



# generateRawGraphToFile_12(5)
