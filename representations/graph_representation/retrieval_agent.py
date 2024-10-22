from enum import Enum
import random
from typing import Optional
import os
import pandas as pd
import regex as re # Use regex instead of re to used variable length lookbehind
import json
from agents_lib import dspy_utils


from typing import Any, Dict

# Get a specific environment variable
api_key = os.environ.get('TOGETHER_API_KEY')
if api_key is None:
    print("NO API IS PROVIDED!")


def primary_key_wrapper(shot_num=1):
    one_shot = """
<example>
Q: Please extract the value for "<key>=node_3", please put the final answer in JSON format.
DataSource:
{{
    "<key>=node_3": <node_3>
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    </node_3>,
    "<key>=node_1": <node_1>
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    </node_1>,
}}
A: In the given dictionary, extract the value for "<key>=node_3", so the answer is 
    {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }}
</example>
"""

    two_shot = one_shot + """
<example>
Q: Please extract the value for "<key>=node_1", please put the final answer in JSON format.
DataSource:
{{
    "<key>=node_3": {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }},
    "<key>=node_1": {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }},
}}
A: In the given dictionary, extract the value for "<key>=node_1", so the answer is 
    {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }}
</example>
"""
    if shot_num == 1:
        return one_shot
    elif shot_num == 2:
        return two_shot

    return ""


def primary_key_withoutwrapper(shot_num=1):
    one_shot = """
<example>
Q: Please extract the value for "<key>=node_3", please put the final answer in JSON format.
DataSource:
{{
    "<key>=node_3": {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }},
    "<key>=node_1": {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }},
}}
A: In the given dictionary, extract the value for "<key>=node_3", so the answer is 
    {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }}
</example>
"""

    two_shot = one_shot + """
<example>
Q: Please extract the value for "<key>=node_1", please put the final answer in JSON format.
DataSource:
{{
    "<key>=node_3": {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }},
    "<key>=node_1": {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }},
}}
A: In the given dictionary, extract the value for "<key>=node_1", so the answer is 
    {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }}
</example>
"""
    if shot_num == 1:
        return one_shot
    elif shot_num == 2:
        return two_shot

    return ""


def primary_key(shot_num=1, wrapper=False):
    if wrapper:
        return primary_key_wrapper(shot_num)
    return primary_key_withoutwrapper(shot_num)


def secondary_key(shot_num=1):
    one_shot = """
<example>
Q: Please extract the value for "edge_1", please put the final answer in JSON format.
DataSource:
{{
    "edge_1": "node_4",
    "edge_2": "node_15",
    "edge_3": "node_61"
}}

A: In the given dictionaries, extract the value for "edge_1", so the answer is {{"edge_1": "node_4"}}
</example>
"""
    two_shot = one_shot + """
<example>
Q: Please extract the value for "edge_2", please put the final answer in JSON format.
DataSource:
{{
    "edge_1": "node_14",
    "edge_2": "node_50",
    "edge_3": "node_24"
}}

A: In the given dictionaries, extract the value for "edge_2", so the answer is {{"edge_2": "node_50"}}
</example>
"""
    if shot_num == 1:
        return one_shot
    elif shot_num == 2:
        return two_shot

    return ""


QUESTION = """
Q: Please extract the value for "{key}", please put the final answer in JSON format.
DataSource:
{source}
"""

def updateSource(source):
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
        name_start = source.find("<key>=", startIndex)
        name=source[name_start+6:str_start-3]
        # if len(name) > 10:
        #     name = name[:10]
        start_name = "<"+name+">"
        end_name = "</"+name+">"
        source = source.replace("{", start_name, 1)
        source = source.replace("}", end_name, 1)
        startIndex = source.find(end_name) + len(end_name)
        endIndex = len(source) - 1

    return "{\n"+source+"\n}"
    


class RetrievalWorker:
    def __init__(self, role="", model="mistralai/Mixtral-8x7B-Instruct-v0.1", temp=0.0):
        self.role_prompt = role

        param = {"temperature": temp}
        self.model = dspy_utils.TogetherHFAdaptor(model, apiKey=api_key, **param)

    def retrieve(self, source, key, is_print=False):
        prompt = self.role_prompt.format(source=source, key=key)
        if is_print:
            print(prompt)
        response = self.model.request(prompt=prompt)
        answer_str = response["choices"][0]["text"]
        return answer_str


