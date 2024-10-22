
import os
import sys

from typing import Any, Dict

import json
import pandas as pd
from io import BytesIO

import data_integration_demo as did
from agents_lib import agent_util as agents



def JSONStrWithIndex(json_output, raw_row_list, header_list, prefix):
        length = len(header_list)
        updated_rows = []
        for i, row in enumerate(raw_row_list):
            new_row = {}
            for j, col in enumerate(row):
                new_row[f"{prefix}{j}"] = str(col)
            updated_rows.append(new_row)
        json_output["rows"] = updated_rows

        updated_header = {}
        for i in range(length):
            updated_header[f"{prefix}{i}"] = str(header_list[i])
        json_output["headers"] = updated_header

        return json.dumps(json_output, indent=2)

def onlyRowsStrWithIndex(raw_row_list, header_list, prefix=""):
    new_json = {}
    updated_rows = []
    
    for i, row in enumerate(raw_row_list):
        new_row = {}
        for j, col in enumerate(row):
            if prefix == "":
                col_name = header_list[j]
            else:
                col_name = f"{prefix}{j}"
            new_row[col_name] = str(col)
        updated_rows.append(new_row)
    new_json["rows"] = updated_rows
    return json.dumps(new_json, indent=2)


def onlyHeadersStrWithIndex(header_list, prefix="", fix_header_name=False):
    new_json = {}
    updated_header_list = []
    updated_headers = {}
    
    for i, header in enumerate(header_list):
        col_name = f"{prefix}{i}"
        if fix_header_name:
            header = header.replace(" ", "")
        updated_headers[col_name] = str(header)

    updated_header_list.append(updated_headers)
    new_json["headers"] = updated_header_list

    return json.dumps(new_json, indent=2)

def onlyHeadersStrWithIndex_flip_order(header_list, prefix="", fix_header_name=False):
    new_json = {}
    updated_headers = {}
    
    for i, header in enumerate(header_list):
        col_name = f"{prefix}{i}"
        if fix_header_name:
            header = header.replace(" ", "")
        updated_headers[str(header)] = col_name
    new_json["headers"] = updated_headers

    return json.dumps(new_json, indent=2)

def onlyHeadersStr(header_list, fix_header_name=False):
    new_json = {}
    updated_headers = []
    
    for i, header in enumerate(header_list):
        if fix_header_name:
            header = header.replace(" ", "")
        updated_headers.append(str(header))
    new_json["headers"] = updated_headers

    return json.dumps(new_json, indent=2)


def read_csv(file_path, max_rows=2):
    contents = None
    with open(file_path, "rb") as f:
            contents = f.read()

    json_output = {}
    xls = pd.ExcelFile(BytesIO(contents), engine="openpyxl")
    json_output["num_sheets"] = len(xls.sheet_names)
    json_output["sheet_names"] = xls.sheet_names
    
    details = xls.parse()
    headers = ""
    for col in details.columns.values:
        headers += str(col) + ","
    headers = headers[:-1]
    json_output["headers"] = headers

    # for rows in list(details.columns.values):
    #     print(details[rows])
    #     # for row in rows:
    #     #     print(row)
    num_rows = max_rows
    raw_rows = pd.read_excel(xls, nrows=num_rows)
    rows = []
    raw_rows_list = []
    for i in range(num_rows):
        row_list = raw_rows.iloc[i].tolist()
        raw_rows_list.append(row_list)
        full_row = ""
        for col in row_list:
            full_row += str(col) + ","
        full_row = full_row[:-1]
        full_row += "\n"
        rows.append(full_row)

    json_output["rows"] = rows
    json_output["file_name"] = file_path
    json_output["data_type"] = "Table"
    json_output["data type description"] = "A Table is an object composed of a header and rows."
    return list(details.columns.values), raw_rows_list, json_output


def compare(expected, output):
    score = 0
    if len(output) != len(expected):
        return score
    else:
        for i in range(len(output)):
            if str(output[i]) == str(expected[i]):
                score += 1
    return score


def compare_dic(expected, output):
    score = 0
    for key in output:
        out_value = output[key]
        if key not in expected:
            continue
        exp_value = expected[key]
        if len(out_value) == len(exp_value):
            for i in range(len(out_value)):
                if str(out_value[i]) == str(exp_value[i]):
                    score += 1

    return score

def create_prompt(json_str, field_name, question_before:bool=True):
    prompt = f"""Please only extract "{field_name}" column from the given content. Please pay attention to the "{field_name}" column of the given content. You must return in JSON format and no extra information. The key is "{field_name}", value is a list containing the extracted values.
Below is the content\n:
    """
    prompt += json_str
    if question_before:
        return prompt
    
    prompt += f"""\nGiven the above content, please only extract "{field_name}" column from the given content. Please pay attention to the "{field_name}" column of the given content. You must return in JSON format and no extra information. The key is "{field_name}", value is a list containing the extracted values.
        """
    return prompt

def composed_prompt(json_str, header_list, question_before:bool=True):
    query = f"""Please extract the row values for {header_list} from the given content. You must return in JSON format and no extra information. Each entry is a dic, the key is header name, value is a list containing the extracted values."""
    query += """
    e.g.{"rows": [ {"col_1": "a", "col_2": "b", "col_3": "c"}, {"col_1": "d", "col_2": "e", "col_3": "f}]}
    ]}, the extracted value for ["col_1", "col_2"] would be
    {
        "col_1": ["a", "d"],
        "col_2": ["b", "e"]
    }
    """
    prompt = query + "\n" + json_str
    prompt += "\n" + query
    return prompt


def test_main(json_str, expected_rows, header_list, model, question_before=True):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    distribution = {}
    for i, field_name in enumerate(header_list):
        prompt = create_prompt(json_str, field_name, question_before)
        if i == 0:
            print(prompt)
            # break
        response = planner.simple_ask(prompt)
        response.replace("\\", "")
        tmp = []
        try:
            json_answer = agents.getJsonFromAnswer(response)
        except Exception as e:
            print("failed to parse json answer!", field_name, "<<<", response, ">>>")
            json_answer = {}
        for key in json_answer:
            if key == field_name:
                tmp = json_answer[key]
        expected = []
        for j in range(len(expected_rows)):
            expected.append(expected_rows[j][i])
        score = compare(expected, tmp)
        print("Score for ", i, field_name, expected, tmp, score)
        total_score += score
        
        if str(score) not in distribution:
            distribution[str(score)] = []
        distribution[str(score)].append(i)

        summary = str(i) + ","+ str(score) + "\n"
        final_output += summary

    print(total_score, total_score/(len(expected) * 179.0)) 
    print(distribution)    
    print(final_output)

def test_main_composed(json_str, expected_rows, header_list, model, question_before=True, batch_size=10):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    distribution = {}

    next = 0
    expected_result = {}
    for i, filed_name in enumerate(header_list):
        rows_values = []
        for row in expected_rows:
            rows_values.append(row[i])
        expected_result[filed_name] = rows_values

    i = 0
    while i < len(header_list):
        if i+batch_size<len(header_list):
            next = i+batch_size
            asking_headers = header_list[i:next]
        else:
            next = len(header_list)
            asking_headers = header_list[i:]

        asking_headers_set = set(asking_headers)
        prompt = composed_prompt(json_str, asking_headers, question_before)
        if i == 0:
            print(prompt)
            # break
        response = planner.simple_ask(prompt)
        response.replace("\\", "")
        # print(response)
        try:
            json_answer = agents.getJsonFromAnswer(response)
        except Exception as e:
            print("failed to parse json answer!", "<<<", response, ">>>")
            json_answer = {}

        tmp = {}
        if "rows" in json_answer:
            if isinstance(json_answer["rows"], list):
                for entry in json_answer["rows"]:
                    for key in entry:
                        if key in asking_headers_set:
                            if key not in tmp:
                                tmp[key] = []
                            tmp[key].extend(entry[key])
            elif isinstance(json_answer["rows"], dict):
                for key in json_answer["rows"]:
                    if key in asking_headers_set:
                        if key not in tmp:
                            tmp[key] = []
                        tmp[key].extend(json_answer["rows"][key])

        expected = {}
        for field_name in asking_headers_set:
            expected[field_name] = expected_result[field_name]
        score = compare_dic(expected, tmp)
        print("Score for ", i, expected, tmp, "+++++++++", score)
        total_score += score

        summary = str(i) + ","+ str(score) + "\n"
        final_output += summary

        i = next

    print(total_score, total_score/(len(expected_rows) * 179.0)) 
    print(final_output)        


def test1_no_index(model=agents.Model.MIXTRAL, question_before=True):
    header_list, expected_rows, json_output = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx")
    str_json = json.dumps(json_output, indent=2)
    test_main(str_json, expected_rows, header_list, model, question_before)


def test2_index(model=agents.Model.MIXTRAL, question_before=True):
    header_list, expected_rows, json_output = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=2)
    str_json = JSONStrWithIndex(json_output, expected_rows, header_list, "col_")

    test_main(str_json, expected_rows, header_list, model, question_before)


def test3_index_onlymap(model=agents.Model.MIXTRAL, question_before=True, prefix=""):
    header_list, expected_rows, json_output = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=3)
    str_json = onlyRowsStrWithIndex(expected_rows, header_list, prefix)
    if prefix != "":
        updated_header_list = []
        for i in range(len(header_list)):
            updated_header_list.append(f"{prefix}{i}")
        header_list = updated_header_list

    test_main(str_json, expected_rows, header_list, model, question_before)


def test8_index_onlymap_composed(model=agents.Model.MIXTRAL, question_before=True, prefix=""):
    header_list, expected_rows, json_output = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=3)
    str_json = onlyRowsStrWithIndex(expected_rows, header_list, prefix)
    if prefix != "":
        updated_header_list = []
        for i in range(len(header_list)):
            updated_header_list.append(f"{prefix}{i}")
        header_list = updated_header_list

    test_main_composed(str_json, expected_rows, header_list, model, question_before, batch_size=10)



def test_header_imp(json_str, header_list, model, question_before:bool=True, prefix:str="",expected_value:list=[]):
    planner = did.Planner([model], model)
    final_output = ""
    total_score = 0
    distribution = {}
    for i, field_name in enumerate(header_list):
#         prompt = f"""You're given a map, please only extract the key of "{field_name}" from the given content. Please pay attention to the "{field_name}" of the given content. You must return in JSON format and no extra information, the key is "{field_name}", value is its value.
# Below is the content\n:
#         """
        prompt = f"""Please only extract the value of "{field_name}" from the given content. Please pay attention to the "{field_name}" entry of the given content. You must return in JSON format and no extra information. The key is "{field_name}". Below is the content:\n"""
        prompt += json_str
        if not question_before:
            prompt += f"""Please only extract the value of "{field_name}" from the given content. Please pay attention to the "{field_name}" entry of the given content. You must return in JSON format and no extra information. The key is "{field_name}".\n"""
 
        if i == 0:
            print(prompt)
            # break

        response = planner.simple_ask(prompt)
        response.replace("\\", "")
        tmp = []
        try:
            json_answer = agents.getJsonFromAnswer(response)
        except Exception as e:
            print("failed to parse json answer!", field_name, "<<<", response, ">>>")
            json_answer = {}
        for key in json_answer:
            if key == field_name:
                tmp = json_answer[key]
        expected = prefix + str(i)
        if len(expected_value) != 0:
            expected = expected_value[i]
        if isinstance(tmp, list):
            if len(tmp) > 0:
                tmp = tmp[0]
            else:
                tmp = ""
        score = 1 if str(tmp) == str(expected) else 0
        total_score += score
        if str(score) not in distribution:
            distribution[str(score)] = []
        distribution[str(score)].append(i)
        print("Score for ", i, field_name, prefix, expected, tmp, score)
        summary = str(i) + ","+ str(score) + "\n"
        final_output += summary
    
    print(total_score, total_score/179.0)
    print(distribution)
    return final_output

def test4_index_only_header_map(model=agents.Model.MIXTRAL, question_before=True, prefix=""):
    header_list, _, _ = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=3)
    json_str = onlyHeadersStrWithIndex(header_list, prefix)
    output = test_header_imp(json_str, header_list, model, question_before, prefix)
    
    print(output)    


def test5_index_only_header_map_ask_for_value(model=agents.Model.MIXTRAL, question_before=True, prefix=""):
    header_list, _, _ = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=3)
    json_str = onlyHeadersStrWithIndex(header_list, prefix)
    updated_header_list = []
    for i, header in enumerate(header_list):
        header = f"{prefix}{i}"
        updated_header_list.append(header)
    output = test_header_imp(json_str, updated_header_list, model, question_before, prefix, expected_value=header_list)
    
    print(output)   

# def test5_index_only_header_map_fix_headername(model=agents.Model.MIXTRAL, question_before=True, prefix=""):
#     header_list, _, _ = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=1)
#     json_str = onlyHeadersStrWithIndex(header_list, prefix, fix_header_name=True)
#     updated_header_list = []
#     for header in header_list:
#         header = header.replace(" ", "")
#         updated_header_list.append(header)

#     output = test_header_imp(json_str, updated_header_list, model, prefix)
    
#     print(output)


def test6_index_onlymap_flip_order(model=agents.Model.MIXTRAL, question_before=True, prefix:str=""):
    header_list, _, _ = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=1)
    json_str = onlyHeadersStrWithIndex_flip_order(header_list, prefix, fix_header_name=False)
    # updated_header_list = []
    # for header in header_list:
    #     header = header.replace(" ", "")
    #     updated_header_list.append(header)

    # header_list = updated_header_list

    output = test_header_imp(json_str, header_list, model, question_before, prefix)
    
    print(output)  


def test_header_list(json_str, header_list, model):
    planner = did.Planner([model], model)
    final_output = ""
    for i, field_name in enumerate(header_list):
#         prompt = f"""You're given a map, please only extract the of "{field_name}" from the given content. Please pay attention to the "{field_name}" of the given content. You must return in JSON format and no extra information, the key is "{field_name}", value is its value.
# Below is the content\n:
#         """
        prompt = f"""You're given a list, please only extract the index of "{field_name}" from the given content. Please pay attention to the "{field_name}" column of the given content. You must return in JSON format and no extra information, the key is "{field_name}"."""
        prompt += json_str
        prompt += f"""\nYou're given a list, please only extract the index of "{field_name}" from the given content. Please pay attention to the "{field_name}" column of the given content. You must return in JSON format and no extra information, the key is "{field_name}"."""
 
        if i == 0:
            print(prompt)
            # break

        response = planner.simple_ask(prompt)
        response.replace("\\", "")
        tmp = []
        try:
            json_answer = agents.getJsonFromAnswer(response)
        except Exception as e:
            print("failed to parse json answer!", field_name, "<<<", response, ">>>")
            json_answer = {}
        for key in json_answer:
            if key == field_name:
                tmp = json_answer[key]
        expected = str(i)
        if isinstance(tmp, list):
            if len(tmp) > 0:
                tmp = tmp[0]
            else:
                tmp = ""
        score = 1 if str(tmp) == str(expected) else 0
        print("Score for ", i, field_name, expected, tmp, score)
        summary = str(i) + ","+ str(score) + "\n"
        final_output += summary
    
    return final_output



def test7_index_only_header_list(model=agents.Model.MIXTRAL):
    header_list, _, _ = read_csv("testdata/biofabric-tiny/dou_mmc1.xlsx", max_rows=1)
    json_str = onlyHeadersStr(header_list, fix_header_name=False)

    output = test_header_list(json_str, header_list, model)
    
    print(output) 
    

# test1_no_index(model=agents.Model.MIXTRAL, question_before=True)
# print("========================================\n\n\n")
# test1_no_index(model=agents.Model.MIXTRAL, question_before=False)
# print("========================================\n\n\n")
# test2_index(model=agents.Model.MIXTRAL, question_before=True)
# print("========================================\n\n\n")
# test2_index(model=agents.Model.MIXTRAL, question_before=False)


# test3_index_onlymap(model=agents.Model.MIXTRAL, question_before=True, prefix="")
# test3_index_onlymap(model=agents.Model.MIXTRAL, question_before=False, prefix="")
# test3_index_onlymap(model=agents.Model.MIXTRAL, question_before=True, prefix="col_")
# test3_index_onlymap(model=agents.Model.MIXTRAL, question_before=False, prefix="col_")
# print("========================================\n\n\n")
# test4_index_only_header_map(model=agents.Model.MIXTRAL, question_before=True, prefix="col_")
# test4_index_only_header_map(model=agents.Model.MIXTRAL, question_before=False, prefix="col_")


# test5_index_only_header_map_ask_for_value(model=agents.Model.MIXTRAL, prefix="col_")
# test6_index_onlymap_flip_order(model=agents.Model.MIXTRAL, question_before=True, prefix="col_")
# test6_index_onlymap_flip_order(model=agents.Model.MIXTRAL, question_before=False, prefix="col_")
# test7_index_only_header_list()
test8_index_onlymap_composed(model=agents.Model.MIXTRAL, question_before=True, prefix="")