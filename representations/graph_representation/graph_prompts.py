
def TwoHopsCOT(unique_key_name="", shot_num=2):
    example1_1shot_2hop = f"""
<example>
Q: Please extract the final value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf"-->"edge_27ccf"-->"edge_1bd48", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": {{
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    }},
    "{unique_key_name}08a0b649-9a74-48f9-a5f7-0a3ff4e3f6ae": {{
        "edge_1f6ae": "1f32f947-8dde-406b-b57b-cecb2ba49137",
        "edge_2f6ae": "1607423e-1f69-4465-aea2-45ae6e17114e",
        "edge_3f6ae": "41958c70-3b25-4f2e-9e72-145e7bb64eb8"
    }},
    "{unique_key_name}efbac909-9b45-4813-bdf7-2470f149bd48": {{
        "edge_1bd48": "187eea0b-b64a-49c3-9028-893e7f9eb4a8",
        "edge_2bd48": "e9dd7bce-f58d-4985-af1d-4e235ce18413",
        "edge_3bd48": "4b516667-6b10-46a3-9110-021299e67ccf"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf", dic_value_1={{
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    }}, and then extract value for "edge_27ccf" from dic_value_1, the value is "efbac909-9b45-4813-bdf7-2470f149bd48", and then extract value for "{unique_key_name}efbac909-9b45-4813-bdf7-2470f149bd48" from D, the value is dic_value_2={{
        "edge_1bd48": "187eea0b-b64a-49c3-9028-893e7f9eb4a8",
        "edge_2bd48": "e9dd7bce-f58d-4985-af1d-4e235ce18413",
        "edge_3bd48": "4b516667-6b10-46a3-9110-021299e67ccf"
    }}, and then extract value for "edge_1bd48" from dic_value_2, the value is "187eea0b-b64a-49c3-9028-893e7f9eb4a8". So the final answer is
    
    {{"{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": "187eea0b-b64a-49c3-9028-893e7f9eb4a8"}}.
</example>
    """

    example2_1shot_2hop = f"""
<example>
Q: Please extract the final value for "{unique_key_name}2e10a594-a965-43a0-9322-bfc27b66b531"-->"edge_1b531"-->"edge_35d9c", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}75c858d9-6ea9-4302-99de-74769e075d9c": {{
        "edge_15d9c": "258db208-bed5-4ea3-b574-7f3f7af14c73",
        "edge_25d9c": "38913d41-46a9-46fc-9b44-ae1ab93f9f2a",
        "edge_35d9c": "bac391a7-2910-4531-a754-649122f7ca5a"
    }},
    "{unique_key_name}7e54fcc9-3d7f-4bd0-a3ae-f495c7b9f9cb": {{
        "edge_1f9cb": "2e10a594-a965-43a0-9322-bfc27b66b531",
        "edge_2f9cb": "75c858d9-6ea9-4302-99de-74769e075d9c",
        "edge_3f9cb": "45e84db9-9ac5-4af7-ad41-c99b2103d4b2"
    }},
    "{unique_key_name}2e10a594-a965-43a0-9322-bfc27b66b531": {{
        "edge_1b531": "75c858d9-6ea9-4302-99de-74769e075d9c",
        "edge_2b531": "258db208-bed5-4ea3-b574-7f3f7af14c73",
        "edge_3b531": "45cb689e-9118-47b6-ada4-e8bc1136f791"
    }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}2e10a594-a965-43a0-9322-bfc27b66b531", dic_value_1={{
        "edge_1b531": "75c858d9-6ea9-4302-99de-74769e075d9c",
        "edge_2b531": "258db208-bed5-4ea3-b574-7f3f7af14c73",
        "edge_3b531": "45cb689e-9118-47b6-ada4-e8bc1136f791"
    }}, and then extract value for "edge_1b531" from dic_value_1, the value is "75c858d9-6ea9-4302-99de-74769e075d9c", and then extract value for "{unique_key_name}75c858d9-6ea9-4302-99de-74769e075d9c" from D, the value is dic_value_2={{
        "edge_15d9c": "258db208-bed5-4ea3-b574-7f3f7af14c73",
        "edge_25d9c": "38913d41-46a9-46fc-9b44-ae1ab93f9f2a",
        "edge_35d9c": "bac391a7-2910-4531-a754-649122f7ca5a"
    }}, and then extract value for "edge_35d9c" from dic_value_2, the value is "bac391a7-2910-4531-a754-649122f7ca5a". So the final answer is
    
    {{"{unique_key_name}2e10a594-a965-43a0-9322-bfc27b66b531": "bac391a7-2910-4531-a754-649122f7ca5a"}}.
</example>
    """
    if shot_num == 1:
        return example1_1shot_2hop
    return example1_1shot_2hop + example2_1shot_2hop


def TwoHopsCOT_abs(unique_key_name="", shot_num=2):
    oneshot_2hop = f"""
<example>
Q: Please extract the final value for key "{unique_key_name}node_30" --> edge "edge_4" --> edge "edge_32", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": {{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }},
    "{unique_key_name}node_42": {{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }},
    "{unique_key_name}node_34": {{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, then extract value for edge "edge_4" from dic_value_1, the value is "node_42". The next step is to extract value for "{unique_key_name}node_42" from D, the value is dic_value_2={{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }}, finally extract value for edge "edge_32" from dic_value_2, the value is "node_3". 

So the final answer is {{"{unique_key_name}node_30": "node_3"}}.
</example>
    """

    twoshot_2hop = oneshot_2hop + f"""
<example>
Q: Please extract the final value for key "{unique_key_name}node_30" --> edge "edge_15" --> edge "edge_11", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": {{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }},
    "{unique_key_name}node_42": {{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }},
    "{unique_key_name}node_34": {{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_15" from dic_value_1, the value is "node_34", and then extract value for "{unique_key_name}node_34" from D, the value is dic_value_2={{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}, and then extract value for "edge_11" from dic_value_2, the value is "node_23". So the final answer is
    
    {{"{unique_key_name}node_30": "node_23"}}.
</example>
    """

    threeshot_2hop = twoshot_2hop + f"""
<example>
Q: Please extract the final value for key "{unique_key_name}node_30" --> edge "edge_4" --> edge "edge_32" for 2 hops traversal, please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": {{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }},
    "{unique_key_name}node_42": {{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }},
    "{unique_key_name}node_34": {{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_4" from dic_value_1, the value is "node_42", and then extract value for "{unique_key_name}node_42" from D, the value is dic_value_2={{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }}, and then extract value for "edge_32" from dic_value_2, the value is "node_3". So the final answer is
    
    {{"{unique_key_name}node_30": "node_3"}}.
</example>
    """
    if shot_num == 1:
        return oneshot_2hop
    if shot_num == 2:
        return twoshot_2hop
    return threeshot_2hop


def TwoHopsCOTWrapper_abs(unique_key_name="", shot_num=2):
    oneshot_2hop = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_30"-->"edge_4"-->"edge_32", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": <node_30>
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    </node_30>,
    "{unique_key_name}node_42": <node_42>
        "edge_5": "node_25",
        "edge_32": "node_3"
    </node_42>,
    "{unique_key_name}node_34": <node_34>
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    </node_34>
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_4" from dic_value_1, the value is "node_42", and then extract value for "{unique_key_name}node_42" from D, the value is dic_value_2={{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }}, and then extract value for "edge_32" from dic_value_2, the value is "node_3". So the final answer is
    
    {{"{unique_key_name}node_30": "node_3"}}.
</example>
    """

    twoshot_2hop = oneshot_2hop + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_30"-->"edge_15"-->"edge_11", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": <node_30>
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    </node_30>,
    "{unique_key_name}node_42": <node_42>
        "edge_5": "node_25",
        "edge_32": "node_3"
    </node_42>,
    "{unique_key_name}node_34": <node_34>
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    </node_34>
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_15" from dic_value_1, the value is "node_34", and then extract value for "{unique_key_name}node_34" from D, the value is dic_value_2={{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}, and then extract value for "edge_11" from dic_value_2, the value is "node_23". So the final answer is
    
    {{"{unique_key_name}node_30": "node_23"}}.
</example>
    """

    threeshot_2hop = twoshot_2hop + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_30"-->"edge_4"-->"edge_32", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": <node_30>
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    </node_30>,
    "{unique_key_name}node_42": <node_42>
        "edge_5": "node_25",
        "edge_32": "node_3"
    </node_42>,
    "{unique_key_name}node_34": <node_34>
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    </node_34>
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_4" from dic_value_1, the value is "node_42", and then extract value for "{unique_key_name}node_42" from D, the value is dic_value_2={{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }}, and then extract value for "edge_32" from dic_value_2, the value is "node_3". So the final answer is
    
    {{"{unique_key_name}node_30": "node_3"}}.
</example>
    """
    if shot_num == 1:
        return oneshot_2hop
    if shot_num == 2:
        return twoshot_2hop
    return threeshot_2hop


def TwoHopsCOTDifferentSource_abs(unique_key_name="", shot_num=2):
    oneshot_2hop = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_30"-->"edge_4"-->"edge_32", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_30": {{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }},
    "{unique_key_name}node_42": {{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }},
    "{unique_key_name}node_34": {{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_30", dic_value_1={{
        "edge_15": "node_34",
        "edge_4": "node_42",
        "edge_10": "node_7"
    }}, and then extract value for "edge_4" from dic_value_1, the value is "node_42", and then extract value for "{unique_key_name}node_42" from D, the value is dic_value_2={{
        "edge_5": "node_25",
        "edge_32": "node_3"
    }}, and then extract value for "edge_32" from dic_value_2, the value is "node_3". So the final answer is
    
    {{"{unique_key_name}node_30": "node_3"}}.
</example>
    """

    twoshot_2hop = oneshot_2hop + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_41"-->"edge_20"-->"edge_19", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_10": {{
        "edge_0": "node_38",
        "edge_3": "node_17",
        "edge_19": "node_25",
        "edge_27": "node_17"
    }},
    "{unique_key_name}node_41": {{
        "edge_28": "node_43",
        "edge_20": "node_10"
    }},
    "{unique_key_name}node_29": {{
        "edge_4": "node_49",
        "edge_20": "node_0",
        "edge_52": "node_15"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_41", dic_value_1={{
        "edge_28": "node_43",
        "edge_20": "node_10"
    }}, and then extract value for "edge_20" from dic_value_1, the value is "node_10", and then extract value for "{unique_key_name}node_10" from D, the value is dic_value_2={{
        "edge_0": "node_38",
        "edge_3": "node_17",
        "edge_19": "node_25",
        "edge_27": "node_17"
    }}, and then extract value for "edge_19" from dic_value_2, the value is "node_25". So the final answer is
    
    {{"{unique_key_name}node_41": "node_25"}}.
</example>
    """

    threeshot_2hop = twoshot_2hop + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_16"-->"edge_51"-->"edge_2", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_16": {{
        "edge_51": "node_25",
        "edge_10": "node_4",
        "edge_13": "node_49"
    }},
    "{unique_key_name}node_25": {{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_16", dic_value_1={{
        "edge_51": "node_25",
        "edge_10": "node_4",
        "edge_13": "node_49"
    }}, and then extract value for "edge_51" from dic_value_1, the value is "node_25", and then extract value for "{unique_key_name}node_25" from D, the value is dic_value_2={{
        "edge_11": "node_23",
        "edge_25": "node_30",
        "edge_2": "node_8"
    }}, and then extract value for "edge_2" from dic_value_2, the value is "node_8". So the final answer is
    
    {{"{unique_key_name}node_16": "node_8"}}.
</example>
    """
    if shot_num == 1:
        return oneshot_2hop
    if shot_num == 2:
        return twoshot_2hop
    return threeshot_2hop


def OneHopsCOTWithEdge3_3(shot_num=2, unique_key_name=""):
    one_shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_25"-->"cb4c2769-aa72-494c-9cc7-31229ced647d", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_25": {{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "node_3",
      "node_14"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "node_10",
      "node_1",
      "node_6"
    ],
    "fc87b456-230b-4f46-a7aa-608d3d64b6a1": [
      "node_23"
    ]
  }},
  "{unique_key_name}node_26": {{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "node_6",
      "node_14",
      "node_12"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "node_11",
      "node_25",
      "node_17"
    ]
  }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_25", dic_value={{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "node_3",
      "node_14"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "node_10",
      "node_1",
      "node_6"
    ],
    "fc87b456-230b-4f46-a7aa-608d3d64b6a1": [
      "node_23"
    ]
    }}, and then extract value for "cb4c2769-aa72-494c-9cc7-31229ced647d" from dic_value, the value is [
      "node_10",
      "node_1",
      "node_6"
    ], so the final answer is

    {{"{unique_key_name}node_25": ["node_10", "node_1", "node_6"]}}.
</example>
    """

    two_shots = one_shot +f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_3"-->"dcd05e47-0a75-4664-a0dd-2911ecd486d2", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_29": {{
    "36aa5761-aa6a-4254-8023-f1ed5dd69eb2": [
      "node_7",
      "node_19"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "node_8"
    ],
    "fdd52795-da9b-4576-8d7d-dc469c465d4c": [
      "node_1",
      "node_4"
    ]
  }},
  "{unique_key_name}node_3": {{
    "c7337a5d-e49b-4789-b338-b2111dbcf464": [
      "node_11",
      "node_2"
    ],
    "ca3e1dd6-28bb-435e-bdd8-1153efc9c381": [
      "node_20"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "node_26",
      "node_17"
    ]
  }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_3", dic_value={{
    "c7337a5d-e49b-4789-b338-b2111dbcf464": [
      "node_11",
      "node_2"
    ],
    "ca3e1dd6-28bb-435e-bdd8-1153efc9c381": [
      "node_20"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "node_26",
      "node_17"
    ]
  }}, and then extract value for "dcd05e47-0a75-4664-a0dd-2911ecd486d2" from dic_value, the value is [
      "node_26",
      "node_17"
    ],  so the final answer is

    {{"{unique_key_name}node_3": ["node_26","node_17"]}}.
</example>
    """

    if shot_num == 1:
        return one_shot
    return two_shots


def OneHopsCOTWithEdge3_1(shot_num=2, unique_key_name=""):
    one_shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}82c476c1-2c64"-->"cb4c2769-aa72-494c-9cc7-31229ced647d", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}82c476c1-2c64": {{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "9819b521-1535"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "e30592b1-e534"
    ],
    "fc87b456-230b-4f46-a7aa-608d3d64b6a1": [
      "5445ec80-e5dc"
    ]
  }},
  "{unique_key_name}ce429c92-1d73": {{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "7e8305bd-33c5"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "28c032ba-f363"
    ]
  }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}82c476c1-2c64", dic_value={{
    "ca29cff3-c1fe-4cf9-88b9-13974971ab23": [
      "9819b521-1535"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "e30592b1-e534"
    ],
    "fc87b456-230b-4f46-a7aa-608d3d64b6a1": [
      "5445ec80-e5dc"
    ]
    }}, and then extract value for "cb4c2769-aa72-494c-9cc7-31229ced647d" from dic_value, the value is ["e30592b1-e534"], so the final answer is

    {{"{unique_key_name}82c476c1-2c64": ["e30592b1-e534"]}}.
</example>
    """

    two_shots = one_shot +f"""
<example>
Q: Please extract the final value for "{unique_key_name}7de0b679-f3da"-->"dcd05e47-0a75-4664-a0dd-2911ecd486d2", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}3b596806-5cb6": {{
    "36aa5761-aa6a-4254-8023-f1ed5dd69eb2": [
      "6f35a9dc-663d"
    ],
    "cb4c2769-aa72-494c-9cc7-31229ced647d": [
      "e4ab9025-4932"
    ],
    "fdd52795-da9b-4576-8d7d-dc469c465d4c": [
      "51a9b5d5-bb58"
    ]
  }},
  "{unique_key_name}7de0b679-f3da": {{
    "c7337a5d-e49b-4789-b338-b2111dbcf464": [
      "c3d8ba37-766b"
    ],
    "ca3e1dd6-28bb-435e-bdd8-1153efc9c381": [
      "f6b8f5fd-2e46"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "e4ab9025-4932"
    ]
  }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}7de0b679-f3da", dic_value={{
    "c7337a5d-e49b-4789-b338-b2111dbcf464": [
      "c3d8ba37-766b"
    ],
    "ca3e1dd6-28bb-435e-bdd8-1153efc9c381": [
      "f6b8f5fd-2e46"
    ],
    "dcd05e47-0a75-4664-a0dd-2911ecd486d2": [
      "e4ab9025-4932"
    ]
  }}, and then extract value for "dcd05e47-0a75-4664-a0dd-2911ecd486d2" from dic_value, the value is ["e4ab9025-4932"],  so the final answer is

    {{"{unique_key_name}node_3": ["e4ab9025-4932"]}}.
</example>
    """

    if shot_num == 1:
        return one_shot
    return two_shots


def OneHopsCOTWithEdge3_1_abs(shot_num=2, unique_key_name=""):
    one_shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_40"-->"edge_13", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_44": {{
    "edge_13": [
      "node_46"
    ]
  }},
  "{unique_key_name}node_40": {{
    "edge_0": [
      "node_31"
    ],
    "edge_13": [
      "node_38"
    ]
  }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_40", dic_value={{
    "edge_0": [
      "node_31"
    ],
    "edge_13": [
      "node_38"
    ]
    }}, and then extract value for "edge_13" from dic_value, the value is ["node_38"], so the final answer is

    {{"{unique_key_name}node_40": ["node_38"]}}.
</example>
    """

    two_shots = one_shot +f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_34"-->"edge_12", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_34": {{
    "edge_2": [
      "node_5"
    ],
    "edge_12": [
      "node_12"
    ],
    "edge_8": [
      "node_41"
    ]
  }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_34", dic_value={{
    "edge_2": [
      "node_5"
    ],
    "edge_12": [
      "node_12"
    ],
    "edge_8": [
      "node_41"
    ]
  }}, and then extract value for "edge_12" from dic_value, the value is ["node_12"],  so the final answer is

    {{"{unique_key_name}node_34": ["node_12"]}}.
</example>
    """
    
    three_shots = two_shots +f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_12"-->"edge_3", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_11": {{
    "edge_13": [
      "node_23"
    ],
    "edge_3": [
      "node_0"
    ]
  }},
  "{unique_key_name}node_12": {{
    "edge_3": [
      "node_41"
    ],
    "edge_4": [
      "node_13"
    ]
  }},
  "{unique_key_name}node_13": {{
    "edge_10": [
      "node_35"
    ]
  }},

}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_12", dic_value={{
    "edge_3": [
      "node_41"
    ],
    "edge_4": [
      "node_13"
    ]
  }}, and then extract value for "edge_3" from dic_value, the value is ["node_41"],  so the final answer is

    {{"{unique_key_name}node_12": ["node_41"]}}.
</example>
    """

    if shot_num == 1:
        return one_shot
    elif shot_num == 2:
        return two_shots
    return three_shots


def OneHopsCOTWithEdge3_2_abs(shot_num=2, unique_key_name=""):
    one_shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_40"-->"edge_13", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_44": {{
    "edge_13": [
      "node_46",
      "node_8"
    ]
  }},
  "{unique_key_name}node_40": {{
    "edge_0": [
      "node_31",
      "node_9"
    ],
    "edge_13": [
      "node_38",
      "node_12"
    ]
  }}
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_40", dic_value={{
    "edge_0": [
      "node_31",
      "node_9"
    ],
    "edge_13": [
      "node_38",
      "node_12"
    ]
    }}, and then extract value for "edge_13" from dic_value, the value is ["node_38", "node_12"], so the final answer is

    {{"{unique_key_name}node_40": ["node_38", "node_12"]}}.
</example>
    """

    two_shots = one_shot +f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_34"-->"edge_12", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_34": {{
    "edge_2": [
      "node_5",
      "node_7"
    ],
    "edge_12": [
      "node_12",
      "node_3"
    ],
    "edge_8": [
      "node_41",
      "node_22"
    ]
  }},
}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_34", dic_value={{
    "edge_2": [
      "node_5",
      "node_7"
    ],
    "edge_12": [
      "node_12",
      "node_3"
    ],
    "edge_8": [
      "node_41",
      "node_22"
    ]
  }}, and then extract value for "edge_12" from dic_value, the value is ["node_12", "node_3"],  so the final answer is

    {{"{unique_key_name}node_34": ["node_12", "node_3"]}}.
</example>
    """
    
    three_shots = two_shots +f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_12"-->"edge_3", please put the final answer in JSON format.
DataSource:
{{
  "{unique_key_name}node_11": {{
    "edge_13": [
      "node_23",
      "node_0"
    ],
    "edge_3": [
      "node_0",
      "node_32"
    ]
  }},
  "{unique_key_name}node_12": {{
    "edge_3": [
      "node_41",
      "node_33"
    ],
    "edge_4": [
      "node_13",
      "node_25"
    ]
  }},
  "{unique_key_name}node_13": {{
    "edge_10": [
      "node_35",
      "node_4"
    ]
  }},

}}
A: In the given dictionary D, extract the value for "{unique_key_name}node_12", dic_value={{
    "edge_3": [
      "node_41",
      "node_33"
    ],
    "edge_4": [
      "node_13",
      "node_25"
    ]
  }}, and then extract value for "edge_3" from dic_value, the value is ["node_41", "node_33"],  so the final answer is

    {{"{unique_key_name}node_12": ["node_41", "node_33"]}}.
</example>
    """

    if shot_num == 1:
        return one_shot
    elif shot_num == 2:
        return two_shots
    return three_shots


def OneHopsCOT(unique_key_name="", shot_num=1):
    example_1shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf"-->"edge_27ccf", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": {{
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    }},
    "{unique_key_name}efbac909-9b45-4813-bdf7-2470f149bd48": {{
        "edge_1bd48": "187eea0b-b64a-49c3-9028-893e7f9eb4a8",
        "edge_2bd48": "e9dd7bce-f58d-4985-af1d-4e235ce18413",
        "edge_3bd48": "4b516667-6b10-46a3-9110-021299e67ccf"
    }}
}}
A: In the given dictionary, extract the value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf", dic_value={{
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    }}, and then extract value for "edge_27ccf" from dic_value, the value is "efbac909-9b45-4813-bdf7-2470f149bd48". So the final answer is

    {{"{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": "efbac909-9b45-4813-bdf7-2470f149bd48"}}.
</example>
    """

    example_2shot = example_1shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413"-->"edge_38413", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}a9b7bcd2-e6e9-4698-8b65-d613b49122e6": {{
        "edge_122e6": "3b26912d-e3d4-4f93-9460-b929b8776d3f",
        "edge_222e6": "69ce0cdc-670a-480f-8a8a-47d2e0e13f07"
    }},
    "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413": {{
        "edge_18413": "c834cd67-1c83-44da-8bc0-f45a0228477a",
        "edge_28413": "63bad5d6-41a9-458e-8fd5-e4b989312bd6",
        "edge_38413": "4384c53b-ce23-4266-84de-d5785a085872"
    }},
}}
A: In the given dictionary, extract the value for "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413", dic_value={{
        "edge_18413": "c834cd67-1c83-44da-8bc0-f45a0228477a",
        "edge_28413": "63bad5d6-41a9-458e-8fd5-e4b989312bd6",
        "edge_38413": "4384c53b-ce23-4266-84de-d5785a085872"
    }}, and then extract value for "edge_38413" from dic_value, the value is 4384c53b-ce23-4266-84de-d5785a085872. So the final answer is

    {{"{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413": "4384c53b-ce23-4266-84de-d5785a085872"}}.
</example>
"""
    example_3shot = example_2shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8"-->"edge_1cee8", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}ac86920f-639b-4d71-bc73-009e3becd5d9": {{
        "edge_1d5d9": "2847b39b-6ea8-4516-b5b1-4619f2f7cee8",
        "edge_2d5d9": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_3d5d9": "c8c7cbf7-b86f-4c16-afa4-bed2ab560bcf"
  }},
  "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8": {{
        "edge_1cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_2cee8": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_3cee8": "3fab130e-3d73-453b-843c-6fdc732d0233"
  }},
  "{unique_key_name}02188f17-2aa7-4df6-9db6-e687e06ccdf3": {{
        "edge_1cdf3": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_2cdf3": "960c798a-b893-426a-a9b6-b005be886f08",
        "edge_3cdf3": "78ce3bc8-d701-4328-a37c-a1eb77ee44d0"
  }},
}}
A: In the given dictionary, extract the value for "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8", dic_value={{
        "edge_1cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_2cee8": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_3cee8": "3fab130e-3d73-453b-843c-6fdc732d0233"
}}, and then extract value for "edge_1cee8" from dic_value, the value is "02188f17-2aa7-4df6-9db6-e687e06ccdf3". So the final answer is

    {{"{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3"}}.
</example>
"""
    if shot_num == 1:
        return example_1shot
    elif shot_num == 2:
        return example_2shot
    return example_3shot


def OneHopsCOTWrapper(unique_key_name="", shot_num=1):
    example_1shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf"-->"edge_27ccf", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": <4b516667-6b10-46a3-9110-021299e67ccf>
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    </4b516667-6b10-46a3-9110-021299e67ccf>,
    "{unique_key_name}efbac909-9b45-4813-bdf7-2470f149bd48": <efbac909-9b45-4813-bdf7-2470f149bd48>
        "edge_1bd48": "187eea0b-b64a-49c3-9028-893e7f9eb4a8",
        "edge_2bd48": "e9dd7bce-f58d-4985-af1d-4e235ce18413",
        "edge_3bd48": "4b516667-6b10-46a3-9110-021299e67ccf"
    </efbac909-9b45-4813-bdf7-2470f149bd48>
}}
A: In the given dictionary, extract the value for "{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf", dic_value={{
        "edge_17ccf": "cbb07ac8-c82f-42e3-af00-70e8f98a2150",
        "edge_27ccf": "efbac909-9b45-4813-bdf7-2470f149bd48",
        "edge_37ccf": "5ab1ae82-5896-440d-ad42-be679ee5fdcf"
    }}, and then extract value for "edge_27ccf" from dic_value, the value is "efbac909-9b45-4813-bdf7-2470f149bd48". So the final answer is

    {{"{unique_key_name}4b516667-6b10-46a3-9110-021299e67ccf": "efbac909-9b45-4813-bdf7-2470f149bd48"}}.
</example>
    """

    example_2shot = example_1shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413"-->"edge_38413", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}a9b7bcd2-e6e9-4698-8b65-d613b49122e6": <a9b7bcd2-e6e9-4698-8b65-d613b49122e6>
        "edge_122e6": "3b26912d-e3d4-4f93-9460-b929b8776d3f",
        "edge_222e6": "69ce0cdc-670a-480f-8a8a-47d2e0e13f07"
    </a9b7bcd2-e6e9-4698-8b65-d613b49122e6>,
    "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413": <e9dd7bce-f58d-4985-af1d-4e235ce18413>
        "edge_18413": "c834cd67-1c83-44da-8bc0-f45a0228477a",
        "edge_28413": "63bad5d6-41a9-458e-8fd5-e4b989312bd6",
        "edge_38413": "4384c53b-ce23-4266-84de-d5785a085872"
    </e9dd7bce-f58d-4985-af1d-4e235ce18413>,
}}
A: In the given dictionary, extract the value for "{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413", dic_value={{
        "edge_18413": "c834cd67-1c83-44da-8bc0-f45a0228477a",
        "edge_28413": "63bad5d6-41a9-458e-8fd5-e4b989312bd6",
        "edge_38413": "4384c53b-ce23-4266-84de-d5785a085872"
    }}, and then extract value for "edge_38413" from dic_value, the value is 4384c53b-ce23-4266-84de-d5785a085872. So the final answer is

    {{"{unique_key_name}e9dd7bce-f58d-4985-af1d-4e235ce18413": "4384c53b-ce23-4266-84de-d5785a085872"}}.
</example>
"""
    example_3shot = example_2shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8"-->"edge_1cee8", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}ac86920f-639b-4d71-bc73-009e3becd5d9": <ac86920f-639b-4d71-bc73-009e3becd5d9>
        "edge_1d5d9": "2847b39b-6ea8-4516-b5b1-4619f2f7cee8",
        "edge_2d5d9": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_3d5d9": "c8c7cbf7-b86f-4c16-afa4-bed2ab560bcf"
  </ac86920f-639b-4d71-bc73-009e3becd5d9>,
  "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8": <2847b39b-6ea8-4516-b5b1-4619f2f7cee8>
        "edge_1cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_2cee8": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_3cee8": "3fab130e-3d73-453b-843c-6fdc732d0233"
  </2847b39b-6ea8-4516-b5b1-4619f2f7cee8>,
  "{unique_key_name}02188f17-2aa7-4df6-9db6-e687e06ccdf3": <02188f17-2aa7-4df6-9db6-e687e06ccdf3>
        "edge_1cdf3": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_2cdf3": "960c798a-b893-426a-a9b6-b005be886f08",
        "edge_3cdf3": "78ce3bc8-d701-4328-a37c-a1eb77ee44d0"
  </02188f17-2aa7-4df6-9db6-e687e06ccdf3>,
}}
A: In the given dictionary, extract the value for "{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8", dic_value={{
        "edge_1cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3",
        "edge_2cee8": "f60c9ab6-1928-499e-b6d6-a16845ddf345",
        "edge_3cee8": "3fab130e-3d73-453b-843c-6fdc732d0233"
}}, and then extract value for "edge_1cee8" from dic_value, the value is "02188f17-2aa7-4df6-9db6-e687e06ccdf3". So the final answer is

    {{"{unique_key_name}2847b39b-6ea8-4516-b5b1-4619f2f7cee8": "02188f17-2aa7-4df6-9db6-e687e06ccdf3"}}.
</example>
"""
    if shot_num == 1:
        return example_1shot
    elif shot_num == 2:
        return example_2shot
    return example_3shot



def OneHopsCOT_abs(unique_key_name="", shot_num=1):
    example_1shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_3"-->"edge_2", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_3": {{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }},
    "{unique_key_name}node_1": {{
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    }},
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_3", dic_value={{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }}, and then extract value for "edge_2" from dic_value, the value is "node_15". So the final answer is

    {{"{unique_key_name}node_3": "node_15"}}.
</example>
    """

    example_2shot = example_1shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_6"-->"edge_4", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_8": {{
        "edge_4": "node_41",
        "edge_1": "node_76",
        "edge_2": "node_77",
    }},
    "{unique_key_name}node_6": {{
        "edge_4": "node_42",
        "edge_1": "node_17",
        "edge_2": "node_38",
        "edge_3": "node_95"
    }},
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_6", dic_value={{
        "edge_4": "node_42",
        "edge_1": "node_17",
        "edge_2": "node_38",
        "edge_3": "node_95"
    }}, and then extract value for "edge_4" from dic_value, the value is "node_42". So the final answer is

    {{"{unique_key_name}node_6": "node_42"}}.
</example>
"""
    example_3shot = example_2shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_2"-->"edge_3", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_2": {{
        "edge_1": "node_13",
        "edge_2": "node_48",
        "edge_3": "node_35"
  }},
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_2", dic_value={{
        "edge_1": "node_13",
        "edge_2": "node_48",
        "edge_3": "node_35"
}}, and then extract value for "edge_3" from dic_value, the value is "node_35". So the final answer is

    {{"{unique_key_name}node_2": "node_35"}}.
</example>
"""
    if shot_num == 1:
        return example_1shot
    elif shot_num == 2:
        return example_2shot
    return example_3shot


def OneHopsCOTWrapper_abs(unique_key_name="", shot_num=1):
    example_1shot = f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_3"-->"edge_2", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_3": <node_3>
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    </node_3>,
    "{unique_key_name}node_1": <node_1>
        "edge_1": "node_32",
        "edge_2": "node_3",
        "edge_3": "node_44"
    </node_1>,
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_3", dic_value={{
        "edge_1": "node_4",
        "edge_2": "node_15",
        "edge_3": "node_61"
    }}, and then extract value for "edge_2" from dic_value, the value is "node_15". So the final answer is

    {{"{unique_key_name}node_3": "node_15"}}.
</example>
    """

    example_2shot = example_1shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_6"-->"edge_4", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_8": <node_8>
        "edge_4": "node_41",
        "edge_1": "node_76",
        "edge_2": "node_77",
    </node_8>,
    "{unique_key_name}node_6": <node_6>
        "edge_4": "node_42",
        "edge_1": "node_17",
        "edge_2": "node_38",
        "edge_3": "node_95"
    </node_6>,
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_6", dic_value={{
        "edge_4": "node_42",
        "edge_1": "node_17",
        "edge_2": "node_38",
        "edge_3": "node_95"
    }}, and then extract value for "edge_4" from dic_value, the value is "node_42". So the final answer is

    {{"{unique_key_name}node_6": "node_42"}}.
</example>
"""
    example_3shot = example_2shot + f"""
<example>
Q: Please extract the final value for "{unique_key_name}node_2"-->"edge_3", please put the final answer in JSON format.
DataSource:
{{
    "{unique_key_name}node_2": <node_2>
        "edge_1": "node_13",
        "edge_2": "node_48",
        "edge_3": "node_35"
  </node_2>,
}}
A: In the given dictionary, extract the value for "{unique_key_name}node_2", dic_value={{
        "edge_1": "node_13",
        "edge_2": "node_48",
        "edge_3": "node_35"
}}, and then extract value for "edge_3" from dic_value, the value is "node_35". So the final answer is

    {{"{unique_key_name}node_2": "node_35"}}.
</example>
"""
    if shot_num == 1:
        return example_1shot
    elif shot_num == 2:
        return example_2shot
    return example_3shot


def create_prompt_1hop(json_str, source_node_name, predicate, unique_key_name="", shot_num=1, is_abs=True, wrapper=False):
    prompt_without_temp_extract_078 = f"""
Please extract the $FINAL_VALUE for "{source_node_name}" following edge "{predicate}" from the DataSource above. 

Please only return the results in JSON format and NO explanations. For example: {{"{source_node_name}": $FINAL_VALUE}}.
    """

    prompt_1hop= f"""
Q: Please extract the final value for "{source_node_name}"-->"{predicate}", please put the final answer in JSON format.
DataSource:
"""
    if shot_num ==0:
        return json_str + "\n" + prompt_without_temp_extract_078
    if is_abs:
        if wrapper:
            example = OneHopsCOTWrapper_abs(unique_key_name, shot_num)
        else:
            example = OneHopsCOT_abs(unique_key_name, shot_num)
    else:
        example = OneHopsCOT(unique_key_name, shot_num)

    return example + prompt_1hop + json_str
    

def create_prompt_2hop(json_str, source_node_name, predicate1, predicate2, shot_num=2, unique_key_name="", is_abs=False, wrapper=False, use_code=False):
    prompt_2hop= f"""
Q: Please extract the final value for key "{source_node_name}" --> edge "{predicate1}" --> edge "{predicate2}", please put the final answer in JSON format.
DataSource:
"""

    two_hop_code = """
You can execute the next function to get the final answer:
def FindNode(json, start_node, predicate1, predicate2):
    dic = json.loads(json) # Load json
    start_node_value = dic[start_node]
    predicate1_value = start_node_value[predicate1]
    second_node_value = dic[predicate1_value]
    predicate2_value = second_node_value[predicate2]
    return predicate2_value
    """
    if shot_num == 0:
        if use_code:
            return prompt_2hop + "\n" + json_str + "\n" + two_hop_code
        return prompt_2hop + "\n" + json_str
    if is_abs:
        if wrapper:
            example = TwoHopsCOTWrapper_abs(unique_key_name, shot_num)
        else:
            example = TwoHopsCOT_abs(unique_key_name, shot_num)
    else:
        example = TwoHopsCOT(unique_key_name, shot_num)
    
    return example + prompt_2hop + json_str

def create_prompt_1hop_1toN(json_str, source_node_name, predicate, shot_num=2, unique_key_name="<key>=", source_type="3_1", is_abs=False):
    prompt_1hop= f"""
Q: Please extract the final value for "{source_node_name}"-->"{predicate}", please put the final answer in JSON format.
DataSource:
"""
    if source_type == "3-1":
        if is_abs:
            return OneHopsCOTWithEdge3_2_abs(shot_num, unique_key_name=unique_key_name) + prompt_1hop + json_str
        return OneHopsCOTWithEdge3_1(shot_num, unique_key_name=unique_key_name) + prompt_1hop + json_str

    
    return OneHopsCOTWithEdge3_3(shot_num, unique_key_name=unique_key_name) + prompt_1hop + json_str