import os
import sys

from typing import Any, Dict

import json
import pandas as pd
from io import BytesIO

import data_integration_demo as did
from agents_lib import agent_util as agents
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

def LoadJsonGraphFromFile(file_name):
    with open(file_name) as f:
        json_data = json.load(f)
    return json_data

num_map = {0:"zero", 
           1:"one", 
           2:"two", 
           3:"three",
           4:"four",
           5:"five",
           6:"six",
           7:"seven",
           8:"eight",
           9:"nine"}

def different_tokens_edge(file_name, representation_names, position="before"):
    json_graph = LoadJsonGraphFromFile(file_name)
    pure_json_str = json.dumps(json_graph, indent=2)
    raw_keys = list(json_graph.keys())

    final_list = []
    for representation_name in representation_names.values():
        if representation_name == "baseline":
            final_list.append(json_graph.copy())
        elif representation_name == "node_id[-4:]+edge_id":
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
            final_list.append(substring_key_json.copy())
            # substring_key_json_str = json.dumps(substring_key_json, indent=2)
        elif representation_name == "node_id+edge_id":
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
            final_list.append(full_key_json.copy())
            # full_key_json_str = json.dumps(full_key_json, indent=2)
        elif representation_name == "randomStr+edge_id":
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
            final_list.append(random_token_json.copy())
            # random_token_json_str = json.dumps(random_token_json, indent=2)
        elif representation_name == "<edge_id>":
            wrapper_token_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict["<"+sub_key+">"] = value[sub_key]
                wrapper_token_json[key] = new_sub_dict
            final_list.append(wrapper_token_json.copy())
            # wrapper_token_json_str = json.dumps(wrapper_token_json, indent=2)
        elif representation_name == "node_id[:4]+edge_id":
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
            final_list.append(substring_keyhead_json.copy())
            # substring_keyhead_json_str = json.dumps(substring_keyhead_json, indent=2)
        elif representation_name == "<key=>node_id AND node_id[:4]+edge_id":
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
            final_list.append(primary_key_substring_key_json.copy())
            # primary_key_substring_key_json_str = json.dumps(primary_key_substring_key_json, indent=2)
        elif representation_name == "node_id[:4]_edge_id":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:4]+"_["+sub_key+"]"] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "baseline_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[sub_key.replace("_", "")] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "node_id[:4]_edge_id_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:4]+"_"+sub_key.replace("_", "")] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "node_id[:4]_[edge_id]_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:4]+"_["+sub_key.replace("_", "")+"]"] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "[edge_id]_node_id[:4]_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for n, sub_key in enumerate(value.keys()):
                    new_sub_dict["["+sub_key.replace("_", "") +"]_"+key[0:4]] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "(edge_id)_node_id[:4]_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:4] +"_("+sub_key.replace("_", "")+")"] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "node_id[:4]_(edge_id)_STR_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for n, sub_key in enumerate(value.keys()):
                    new_sub_dict[key[0:4] +"_("+sub_key.replace("_", "")+")"] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "randomStr+edge_id_v2":
            random_token_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                unique_string = ''.join(choice(ascii_lowercase) for i in range(4))
                for sub_key in value.keys():
                    updated_sub_key = sub_key.replace("_", "")
                    if position == "after":
                        new_sub_dict[updated_sub_key + unique_string] = value[sub_key]
                    elif position == "before":
                        new_sub_dict[unique_string + updated_sub_key] = value[sub_key]
                    else:
                        new_sub_dict[unique_string + updated_sub_key + unique_string] = value[sub_key]
                random_token_json[key] = new_sub_dict
            final_list.append(random_token_json.copy())
        elif representation_name == "[node_id[:8]]_edge_id":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict["["+key[0:8]+"]_"+sub_key] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "node_id[:8]-edge_id":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:8]+"-"+sub_key] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        elif representation_name == "node_id[:8]-edge_id_v2":
            primary_key_substring_key_json = {}
            for key in raw_keys:
                value = json_graph[key]
                new_sub_dict = {}
                for sub_key in value.keys():
                    new_sub_dict[key[0:8]+"-"+sub_key.replace("_", "")] = value[sub_key]
                primary_key_substring_key_json[key] = new_sub_dict
            final_list.append(primary_key_substring_key_json.copy())
        else:
            print("Unknown representation name: ", representation_name)
            exit(1)
        
            #primary_key_substring_key_json_str = json.dumps(primary_key_substring_key_json, indent=2)
    
    # print(pure_json_str)
    # print(substring_key_json_str)
    # print(full_key_json_str)
    # print(random_token_json_str)
    # print(wrapper_token_json_str)
    # print(substring_keyhead_json_str)
    # print(primary_key_substring_key_json_str)

    return final_list

def test_1hop(model, representation, raw_json_graph, updated_json_graph, stop_words="", shot_num=0, is_abs=False, error_log_file=""):
    if error_log_file != "":
        model_name = model.replace("-", "")
        index = model_name.rfind("/")
        if index == -1:
            index = len(model_name)-6
        graph_file = error_log_file.split("/")[-1]
        graph_file = graph_file.split(".txt")[0]
        error_log_file = graph_file + "-1-" + str(shot_num) + "-" + model_name[index+1:] + ".log"
    updated_json_str = json.dumps(updated_json_graph, indent=2)
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    message = "Model=" + str(model) + "\nGraph=" + str(updated_json_str[:100]) + "\nLEN(raw_json_graph)=" + str(len(raw_json_graph)) + "\n\n"
    all_error_message = ""
    token_usage = {}
    for i, name in enumerate(raw_json_graph.keys()):
        for j, predicate in enumerate(raw_json_graph[name]):
            full_score += 1
            expected_target_node = raw_json_graph[name][predicate]
            error_message = str(i) + ", " + str(name) + ", " + str(predicate) + ", " + str(expected_target_node) + "\n"
            all_error_message += error_message
            print(error_message)
            prompt = create_prompt_1hop(updated_json_str, name, predicate, "", shot_num=shot_num, is_abs=is_abs)
            if i == 0 and j ==0:
                print(prompt)
                all_error_message += prompt + "\n"
            response, usage = planner.simple_ask(prompt)
            if "TOO LONG CONTEXT!" in response:
                print("TOO LONG CONTEXT!")
                break
            for key_usage in usage:
                if key_usage not in token_usage:
                    token_usage[key_usage] = 0
                token_usage[key_usage] += usage[key_usage]
            all_error_message += f"Raw output: {response}\n"
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
                error_message ="\n    ++++++ Parsed answer:" +str(json_answer)+ "\n" + "    ++++++ Expected:" + str(expected_target_node) + "\n    ++++++ Got Score:" + str(score) + "\n"
                all_error_message += error_message
                # print(error_message)

            error_message = "++++++ Expected: " + str(expected_target_node) + ", Real: " +str(tmp) + ", Score: " + str(score) + "\n"
            all_error_message += error_message
            print(error_message)

            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary

    for key_usage in token_usage:
        token_usage[key_usage] = token_usage[key_usage] // full_score
    message += "Representation: " + str(representation) + "\n"
    message += "Token Usage:" + str(token_usage) + "\n"
    f = open("one_hop_performance.txt", "a")
    message += "Total_score:"+str(total_score)+", Full_score:"+str(full_score)+", Accuracy:"+str(total_score/float(full_score))+"\n"
    message += "\n\n\n"
    print(message)
    f.write(message)
    f.close()

    all_error_message += message
    if error_log_file != "":
        f = open(error_log_file, "a")
        f.write(all_error_message)
        f.close()


def test_2hop(model, representation, raw_json_graph, updated_json_graph, shot_num, stop_words="", is_abs=True, error_log_file=""):
    if error_log_file != "":
        index = model.rfind("/")
        if index == -1:
            index = len(model)-6
        error_log_file += model[index+1:] + "_2hop_error.txt"
    updated_json_str = json.dumps(updated_json_graph, indent=2)
    planner = did.Planner([model], model) #agents.TogetherCall(model, stop_words=stop_words)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    message = "Model=" + str(model) + "\nGraph=" + str(updated_json_str[:100]) + "\nLEN(raw_json_graph)=" + str(len(raw_json_graph)) + "\n\n"
    all_error_message = ""
    already_print_prompt = False
    token_usage = {}
    for i, name in enumerate(raw_json_graph.keys()):
        for j, predicate1 in enumerate(raw_json_graph[name]):
            one_hop_node = raw_json_graph[name][predicate1]
            if one_hop_node not in raw_json_graph:
                continue
            for k, predicate2 in enumerate(raw_json_graph[one_hop_node]):
                full_score += 1
                expected_target_node = raw_json_graph[one_hop_node][predicate2]
                error_message = str(i) + ", " + str(name) + ", " + str(predicate1) + ", " + str(one_hop_node) + ", " + str(predicate2) + ", " + str(expected_target_node) + "\n"
                all_error_message += error_message
                print(error_message)
                prompt = create_prompt_2hop(updated_json_str, name, predicate1, predicate2, unique_key_name="", shot_num=shot_num, is_abs=is_abs)
                if not already_print_prompt:
                    print(prompt)
                    all_error_message += prompt + "\n"
                    already_print_prompt = True
                response, usage = planner.simple_ask(prompt)
                if "TOO LONG CONTEXT!" in response:
                    print("TOO LONG CONTEXT!")
                    break
                for key_usage in usage:
                    if key_usage not in token_usage:
                        token_usage[key_usage] = 0
                    token_usage[key_usage] += usage[key_usage]
                response.replace("\\", "")
                tmp = []
                all_error_message += "    ++++++ Raw output:" +str(response) + "\n"
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
                    error_message = "\n    ++++++ Parsed answer:" +str(json_answer)+ "\n" + "    ++++++ Expected:" + str(expected_target_node) + "\n    ++++++ Got Score:" + str(score) + "\n"
                    all_error_message += error_message
                    # print(error_message)
                error_message = "++++++ Expected: " + str(expected_target_node) + ", Real: " +str(tmp) + ", Score: " + str(score) + "\n"
                all_error_message += error_message
                print(error_message)

                if str(score) not in distribution:
                    distribution[str(score)] = []
                distribution[str(score)].append(i)

                summary = str(i) + ","+ str(score) + "\n"
                final_output += summary
    
    for key_usage in token_usage:
        token_usage[key_usage] = token_usage[key_usage] // full_score

    message += "Representation: " + str(representation) + "\n"
    message += "Token Usage:" + str(token_usage) + "\n"
    f = open("two_hop_performance.txt", "a")
    message += "Total_score:"+str(total_score)+", Full_score:"+str(full_score)+", Accuracy:"+str(total_score/float(full_score))+"\n"
    message += "\n\n\n"
    print(message)
    f.write(message)
    f.close()

    all_error_message += message
    if error_log_file != "":
        f = open(error_log_file, "a")
        f.write(all_error_message)
        f.close()