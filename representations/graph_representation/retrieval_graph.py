import os
import sys

from typing import Any, Dict

import json
import pandas as pd
from io import BytesIO

import data_integration_demo as did
from agents_lib import agent_util as agents
from generate_graph import generateGraphWithLabels, generateGraphWithoutLabels, generateGraphByPredicates
from graph_prompts import create_prompt_1hop, create_prompt_2hop, create_prompt_1hop_1toN
from retrieval_agent import RetrievalWorker, QUESTION,primary_key, secondary_key, updateSource

from jaal import Jaal
import pandas as pd


def compare_list(expected, output):
    score = 0
    if output is None:
        return score
    
    if isinstance(expected, str):
        expected = [expected]
    if isinstance(output, str):
        output = [output]

    if len(output) != len(expected):
        return score
    else:
        
        for i in range(len(output)):
            if str(output[i]) == str(expected[i]):
                score += 1
    return score
    

def test_main_impl_1hop(json_str, model, json_graph, edge_df, node_df):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        for predicate in json_graph[name]["edges"]:
            full_score += 1
            expected_target_node = json_graph[name]["edges"][predicate]
            print(id, name, predicate, expected_target_node)
            prompt = create_prompt_1hop(json_str, name, predicate)
            if i == 0:
                print(prompt)
            response = planner.simple_ask(prompt)
            response.replace("\\", "")
            tmp = []
            try:
                json_answer = agents.getJsonFromAnswer(response)
            except Exception as e:
                print("failed to parse json answer!", i, name, "<<<", response, ">>>")
                json_answer = {}
            print("++++++ output json_answer", json_answer)
            for key in json_answer:
                if key == name or key == "source_node_name" or key == predicate:
                    tmp = json_answer[key]
                    if isinstance(tmp, dict):
                        tmp = list(tmp.values())

            score = compare_list(expected_target_node, tmp) 
            total_score += score
            
            print("++++++ expected", expected_target_node, tmp, score)
            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_output)


# def request_1hop(json_str, model, json_graph, edge_df, node_df):


def test_main_impl_1hop_withoutLabel(json_str, model, json_graph, edge_df, node_df, unique_key_name="", shot_num=1, is_abs=False):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        name = unique_key_name + name
        for j, predicate in enumerate(json_graph[name]):
            full_score += 1
            expected_target_node = json_graph[name][predicate]
            print(id, name, predicate, expected_target_node)
            # json_str = updateSource(json_str)
            prompt = create_prompt_1hop(json_str, name, predicate, unique_key_name, shot_num=shot_num, is_abs=is_abs)
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
            print("++++++ output json_answer", json_answer)
            if isinstance(json_answer, str):
                tmp = json_answer
            else:
                for key in json_answer:
                    if key == name or key == "source_node_name" or key == predicate:
                        tmp = json_answer[key]
                        if isinstance(tmp, dict):
                            tmp = list(tmp.values())

            score = compare_list(expected_target_node, tmp) 
            total_score += score
            if score < 1:
                print("++++++ raw output", response)
            
            print("++++++ expected", expected_target_node, tmp, score)
            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_output)
    print("++++++++++++++++++++++++++++++", model, unique_key_name, shot_num, is_abs)

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


def test_main_impl_2hop(json_str, model, json_graph, edge_df, node_df, unique_key_name="", shot_num=1, is_abs=False, wrapper=False):
    if wrapper:
        json_str = updateSource(json_str)

    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        name = unique_key_name + name
        for j, predicate1 in enumerate(json_graph[name]):
            one_hop_node = json_graph[name][predicate1]
            keyed_one_hop_node = unique_key_name + one_hop_node
            for k, predicate2 in enumerate(json_graph[keyed_one_hop_node]):
                full_score += 1

                expected_target_node = json_graph[keyed_one_hop_node][predicate2]
                print(id, name, predicate1, one_hop_node, predicate2, expected_target_node)
                prompt = create_prompt_2hop(json_str, name, predicate1, predicate2, unique_key_name=unique_key_name, shot_num=shot_num, is_abs=is_abs, wrapper=wrapper)
                if i == 0 and j ==0 and k ==0:
                    print(prompt)
                response = planner.simple_ask(prompt)
                response.replace("\\", "")
                tmp = []
                try:
                    json_answer = agents.getJsonFromAnswer(response)
                except Exception as e:
                    print("failed to parse json answer!", i, name, "<<<", response, ">>>")
                    json_answer = {}
                print("++++++ output json_answer", json_answer)
                if isinstance(json_answer, str):
                    tmp = json_answer
                else:
                    for key in json_answer:
                        if key == name or key == "source_node_name" or key == predicate2:
                            tmp = json_answer[key]
                            if isinstance(tmp, dict):
                                tmp = extract_final_value(tmp)

                score = compare_list(expected_target_node, tmp)
                if score < 1:
                    print("++++++ raw output", response)
                print("++++++ expected", expected_target_node, tmp, score)
                total_score += score
                if str(score) not in distribution:
                    distribution[str(score)] = []
                distribution[str(score)].append(i)

                summary = str(i) + ","+ str(score) + "\n"
                final_output += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_output)


def test_impl_1hop_edgeM(json_str, model, json_graph, edge_df, node_df, question_before=True, unique_key_name="", shot_num=1, source_type="3-1"):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        name = unique_key_name + name
        for j, predicate in enumerate(json_graph[name]):
            expected_target_nodes = json_graph[name][predicate]
            full_score += len(expected_target_nodes)

            print(id, name, predicate, expected_target_nodes)
            prompt = create_prompt_1hop_1toN(json_str, name, predicate, shot_num=shot_num, unique_key_name=unique_key_name, source_type=source_type, is_abs=True)
            if i == 0 and j == 0:
                print(prompt)
            response = planner.simple_ask(prompt)
            response.replace("\\", "")
            print("+++++++++ intial response", response)
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
                    if key == name or key == "source_node_name" or key == predicate:
                        tmp = json_answer[key]
                        if isinstance(tmp, dict):
                            tmp = extract_final_value(tmp)

            score = compare_list(expected_target_nodes, tmp) 
            total_score += score
            
            print("++++++ expected", expected_target_nodes, tmp, score)
            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_output)


def test_agent_1hop(json_str, model, json_graph, edge_df, node_df, unique_key_name="", shot_num=1, is_abs=False):
    primary_key_retrieval = RetrievalWorker(role=primary_key(shot_num=shot_num)+QUESTION, model=model)
    secondary_key_retrieval = RetrievalWorker(role=secondary_key(shot_num=shot_num)+QUESTION, model=model)
    final_output = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        name = unique_key_name + name
        for j, predicate in enumerate(json_graph[name]):
            full_score += 1
            expected_target_node = json_graph[name][predicate]
            print(id, name, predicate, expected_target_node)

            # step 1
            step_one_response = primary_key_retrieval.retrieve(json_str, name, (i==0 and j==0))
            try:
                json_answer_one = agents.getJsonFromAnswer(step_one_response)
            except Exception as e:
                print("step one parse failed", i, name, "<<<", step_one_response, ">>>")
                json_answer_one = {}
            if json_answer_one == {}:
                print("step one failed return!!!!", step_one_response)
                continue

            # step 2
            step_two_response = secondary_key_retrieval.retrieve(json.dumps(json_answer_one, indent=2), predicate, (i ==0 and j==0))
            step_two_response.replace("\\", "")
            tmp = []
            try:
                json_answer_two = agents.getJsonFromAnswer(step_two_response)
            except Exception as e:
                print("step two parse failed!", i, name, "<<<", step_two_response, ">>>")
                json_answer_two = {}

            if isinstance(json_answer_two, str):
                tmp = json_answer_two
            else:
                for key in json_answer_two:
                    if key == name or key == "source_node_name" or key == predicate:
                        tmp = json_answer_two[key]
                        if isinstance(tmp, dict):
                            tmp = list(tmp.values())

            score = compare_list(expected_target_node, tmp) 
            total_score += score
            if score < 1:
                print("++++++ raw output 1", step_one_response, json_answer_one)
                print("++++++ raw output 2", step_two_response, json_answer_two)
            
            print("++++++ expected", expected_target_node, tmp, score)
            if str(score) not in distribution:
                distribution[str(score)] = []
            distribution[str(score)].append(i)

            summary = str(i) + ","+ str(score) + "\n"
            final_output += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_output)


def test_agent_2hop(json_str, model, json_graph, edge_df, node_df, unique_key_name="", shot_num=1, is_abs=False, wrapper=False):
    if wrapper:
        json_str = updateSource(json_str)
    primary_key_retrieval = RetrievalWorker(role=primary_key(shot_num=shot_num, wrapper=wrapper)+QUESTION, model=model)
    secondary_key_retrieval = RetrievalWorker(role=secondary_key(shot_num=shot_num)+QUESTION, model=model)
    final_list_scores = ""
    total_score = 0
    full_score = 0
    distribution = {}
    num_nodes = node_df.shape[0]
    for i in range(num_nodes):
        id, name = node_df.iloc[i]
        name = unique_key_name + name
        for j, predicate1 in enumerate(json_graph[name]):
            one_hop_node = json_graph[name][predicate1]
            keyed_one_hop_node = unique_key_name + one_hop_node
            for k, predicate2 in enumerate(json_graph[keyed_one_hop_node]):
                # if full_score >= 30:
                #     break
                full_score += 1

                expected_target_node = json_graph[keyed_one_hop_node][predicate2]
                print(id, name, predicate1, one_hop_node, predicate2, expected_target_node)

                hop_num = 2
                primarykey = name
                predicate = predicate1
                one_hop_final_output = []
                while hop_num > 0:
                    # step 1
                    print("agency processing...", primarykey, predicate)
                    step_one_response = primary_key_retrieval.retrieve(json_str, primarykey, (i==0 and j==0 and k==0))
                    try:
                        json_answer_one = agents.getJsonFromAnswer(step_one_response)
                    except Exception as e:
                        json_answer_one = {}
                    if json_answer_one == {}:
                        print("step one failed return!!!!!!", step_one_response)
                        break

                    # step 2
                    step_two_response = secondary_key_retrieval.retrieve(json.dumps(json_answer_one, indent=2), predicate, (i ==0 and j==0 and k==0))
                    step_two_response.replace("\\", "")
                    tmp = []
                    try:
                        json_answer_two = agents.getJsonFromAnswer(step_two_response)
                    except Exception as e:
                        json_answer_two = {}  
                    if json_answer_two == {}:
                        print("step two failed return!", step_two_response)
                        break  

                    if isinstance(json_answer_two, str):
                        tmp = json_answer_two
                    else:
                        for key in json_answer_two:
                            if key == name or key == "source_node_name" or key == predicate1 or key == predicate2:
                                tmp = json_answer_two[key]
                                if isinstance(tmp, dict):
                                    tmp = list(tmp.values())
                    
                    if isinstance(tmp, list):
                        if len(tmp) > 0:
                            tmp = tmp[0]
                        else:
                            tmp = ""
                    primarykey = unique_key_name + str(tmp)
                    predicate = predicate2
                    one_hop_final_output = tmp
                    hop_num -= 1

                # compute the score
                score = compare_list(expected_target_node, one_hop_final_output) 
                total_score += score
                if score < 1:
                    print("++++++ raw output 1", step_one_response, json_answer_one)
                    print("++++++ raw output 2", step_two_response, json_answer_two)
                
                print("++++++ expected", expected_target_node, tmp, score)
                if str(score) not in distribution:
                    distribution[str(score)] = []
                distribution[str(score)].append(i)

                summary = str(i) + ","+ str(score) + "\n"
                final_list_scores += summary


    print(total_score, full_score, total_score/float(full_score))
    print(distribution)    
    print(final_list_scores)


def test1_1hop_with_labels(model=agents.Model.MIXTRAL, question_before=False):
    json_graph, edge_df, node_df = generateGraphWithLabels(50)
    str_json = json.dumps(json_graph, indent=2)
    print(str_json)
    test_main_impl_1hop(str_json, model, json_graph, edge_df, node_df, question_before)


def test1_1hop(model=agents.Model.MIXTRAL, unique_key_name="", unique_edge_name=False, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name=unique_key_name, unique_edge_name=unique_edge_name)
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_1hop_withoutLabel(str_json, model, json_graph, edge_df, node_df, unique_key_name=unique_key_name, shot_num=shot_num, is_abs=is_abs) 

def test1_1hop_unique_key(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=")
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_1hop_withoutLabel(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs)

def test1_1hop_unique_key_edge(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=", unique_edge_name=True)
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_1hop_withoutLabel(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs)

def test1_1hop_unique_key_edge_complex_graph(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, fanin_num=2, fanout_num=3, unique_key_name="<key>=", unique_edge_name=True)
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_1hop_withoutLabel(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs)

def test1_1hop_unique_key_edge_complex_graph_agent(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, fanin_num=2, fanout_num=3, unique_key_name="<key>=", unique_edge_name=True, simple_names=False)
    str_json = json.dumps(json_graph, indent=2)
    test_agent_1hop(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs)



def test2_2hop_unique_key_edge(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=", unique_edge_name=True)
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_2hop(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs, wrapper=True)


def test2_2hop_unique_key_edge_simple_nodeid(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False, wrapper=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=", unique_edge_name=True, simple_names=True)
    str_json = json.dumps(json_graph, indent=2)
    test_main_impl_2hop(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs, wrapper=wrapper)



def test2_2hop_unique_key_edge_agent(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=", unique_edge_name=True)
    str_json = json.dumps(json_graph, indent=2)
    test_agent_2hop(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs)


def test2_2hop_unique_key_edge_agent_wrapper(model=agents.Model.MIXTRAL, shot_num=1, is_abs=False):
    json_graph, edge_df, node_df, _ = generateGraphWithoutLabels(50, unique_key_name="<key>=", unique_edge_name=True)
    str_json = json.dumps(json_graph, indent=2)
    test_agent_2hop(str_json, model, json_graph, edge_df, node_df, unique_key_name="<key>=", shot_num=shot_num, is_abs=is_abs, wrapper=True)



def test3_edgeM_1hop_graph(model=agents.Model.MIXTRAL,unique_key_name="", shot_num=1, source_type="3-1"):
    json_graph, json_graph_by_edge, edge_df, node_df = generateGraphByPredicates(total_edges_num=20, total_node_num=50, max_node_to_edgeNum=3, edge_to_tNodeNum=2, unique_key_name=unique_key_name)
    str_json = json.dumps(json_graph, indent=2)
    test_impl_1hop_edgeM(str_json, model, json_graph, edge_df, node_df, unique_key_name=unique_key_name, shot_num=shot_num, source_type=source_type)




