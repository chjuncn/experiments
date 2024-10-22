
import json
import os
import pandas as pd
# assign directory


def rename_graph_file(directory):
    dir = "" #"/Users/chjun/Documents/GitHub/code/palimpzest/"
    for filename in os.listdir(directory):
        if len(filename) < 20:
            continue
        if not filename.startswith("gnp"):
            continue
        if filename.endswith(".log"):
            continue
        print(filename)

        cleaned_filename = filename.replace("-", "")
        labels = cleaned_filename.split(".txt")
        graph_file = labels[0]

        if labels[1].startswith("_2hop"):
            shot_num = 2
            labels[1] = labels[1][5:]
        else:
            shot_num = 1

        if "_2hop" in labels[1]:
            query_hop_num = 2
            labels[1] = labels[1].replace("_2hop", "")
        else:
            query_hop_num = 1
            shot_num = 0

        labels[1] = labels[1].replace("_error", "")
        model_name = labels[1]
        new_name = graph_file + "-" + str(query_hop_num) + "-" + str(shot_num) + "-" + model_name + ".log"
        print(new_name)
        print("\n")
        os.rename(dir+filename, dir+new_name)

def LoadJsonGraphFromFile(file_name):
    with open(file_name) as f:
        json_data = json.load(f)
    return json_data

def parse_token_usage(line):
    usage_str = line.split(':', 1)[1].strip()
    return json.loads(usage_str.replace("'", '"'))


def same_entry(graph, expected_node, real_node):    
    for key in graph:
        values = set(graph[key].values())
        if expected_node in values and real_node in values:
            return True
    return False


# iterate over files in
# that directory
# for filename in os.listdir(directory):
#     f = os.path.join(directory, filename)
representation_names = ['baseline', 'node_id[-4:]+edge_id', 'node_id+edge_id', "randomStr+edge_id", "<edge_id>", "node_id[:4]+edge_id", "<key=>node_id AND node_id[:4]+edge_id"]  # Replace with your actual list
def parse_file(unnormal_files, f):
    # checking if it is a file
    if not os.path.isfile(f):
        print("Not a file: "+f)
        return []
    labels = f.split("-")
    if len(labels) != 4:
        print("Not enough labels: "+ str(labels))
        return []

    summary_json = []
    print("Analyzing: "+f)
    graph_file = labels[0]
    graph = LoadJsonGraphFromFile("experiments/res_log/"+graph_file+".txt")
    query_hop_num = int(labels[1])
    shot_num = int(labels[2])
    model_name = labels[3]
    json_res = {}
    json_res["model_name"] = model_name
    json_res["graph_file"] = graph_file.split("/")[-1]
    json_res["query_hop_num"] = query_hop_num
    json_res["representation"] = ""
    json_res["shot_num"] = shot_num
    json_res["failed_num"] = 0
    json_res["wrong_edge_problem"] = 0
    json_res["possibly_not_found"] = 0
    json_res["total_score"] = 0
    json_res["full_score"] = 0
    json_res["token_usage"] = {}
    json_res["prompt_token_utilization"] = 0.0
    json_res["completion_token_utilization"] = 0.0
    json_res["accuracy"] = 0.0

    i = 0
    this_json_res = json_res.copy()
    with open(f, 'r') as file:
        expected_node = ""
        real_node = ""
        token_usage = {}
        multiple_token_usage = False
        full_score = 0
        wrong_edge_problem = 0
        possibly_not_found = 0
        found_representation = False

        for line in file:
            if i >= 7:
                i %= 7

            if not found_representation:
                this_json_res["representation"] = representation_names[i]
            if line.startswith("++++++ Expected: "):
                score_index = line.find(", Score: ")
                if score_index == -1:
                    continue
                score = line[score_index+9:].strip()
                if score == "1":
                    continue
                
                expected_index = line.find("Expected: ")
                expected_node = line[expected_index+10: expected_index+10+36].strip()
                real_index = line.find("Real: ")
                real_node = line[real_index+5: score_index].strip()
                if same_entry(graph, expected_node, real_node):
                    wrong_edge_problem += 1
                elif real_node == "[]":
                    possibly_not_found += 1
                    
            elif line.startswith("Token Usage:{'prompt_tokens':") or line.startswith("Usage: {'prompt_tokens':"):
                token_usage_tmp = parse_token_usage(line)
                if len(token_usage_tmp) > 0:
                    if token_usage == {}:
                        token_usage = token_usage_tmp
                    else:
                        multiple_token_usage = True
                        token_usage["prompt_tokens"] += token_usage_tmp["prompt_tokens"]
                        token_usage["completion_tokens"] += token_usage_tmp["completion_tokens"]
                        token_usage["total_tokens"] += token_usage_tmp["total_tokens"]
            elif line.startswith("Representation: "):
                found_representation = True
                representation = line.split(": ")[1].strip()
                this_json_res["representation"] = representation
            elif line.startswith("Total_score:") or line.startswith("total_score:"):
                line = line.lower()
                total_score = int(line.split(":")[1].split(",")[0].strip())
                full_score = int(line.split(", full_score:")[1].split(",")[0].strip())
                
                message = "\n     Basic info: " + model_name + ", " + graph_file.split("/")[-1] + ", " + representation + ", shot_num=" + str(shot_num) + ", query_hop_num=" + str(query_hop_num)
                message += "\nTotal failed_num=" + str(full_score-total_score) + ", wrong_edge_problem=" + str(wrong_edge_problem) + ", possibly_not_found=" + str(possibly_not_found) + ", total_score=" + str(total_score) + ", full_score=" + str(full_score) + "\n"

                if multiple_token_usage:
                    for key in token_usage.keys():
                        token_usage[key] //= full_score
                message += "Summary Token Usage: " + str(token_usage) + "\n"
                print(message)


                this_json_res["token_usage"] = token_usage
                if "prompt_tokens" in token_usage and "completion_tokens" in token_usage:
                    this_json_res["prompt_token_utilization"] = token_usage["prompt_tokens"] / 8193.0
                    this_json_res["completion_token_utilization"] = token_usage["completion_tokens"] / 1000.0
                this_json_res["total_score"] = total_score
                this_json_res["full_score"] = full_score
                this_json_res["wrong_edge_problem"] = wrong_edge_problem
                this_json_res["possibly_not_found"] = possibly_not_found
                this_json_res["failed_num"] = full_score-total_score
                this_json_res["accuracy"] = total_score / full_score
                summary_json.append(this_json_res.copy())
                
                this_json_res = json_res.copy() 

                # next representation begins:
                i  += 1
                expected_node = ""
                real_node = ""
                token_usage = {}
                multiple_token_usage = False
                full_score = 0
                wrong_edge_problem = 0
                possibly_not_found = 0
                found_representation = False
                this_json_res = json_res.copy()

    if len(summary_json) == 6:
        unnormal_files["less_res"] += 1
        unnormal_files["less_res_files"].append(f)
        for i in range(len(summary_json)):
            if summary_json[i]["representation"] == "node_id+edge_id":
                summary_json[i]["representation"] = "randomStr+edge_id"
            if summary_json[-1]["representation"] == "randomStr+edge_id":
                summary_json[-1]["representation"] = "<edge_id>"
            if summary_json[-1]["representation"] == "<edge_id>":
                summary_json[-1]["representation"] = "node_id[:4]+edge_id"
            if summary_json[-1]["representation"] == "node_id[:4]+edge_id":
                summary_json[-1]["representation"] = "<key=>node_id AND node_id[:4]+edge_id"
    if len(summary_json)>7:
        unnormal_files["more_res"] += 1
        unnormal_files["more_res_files"].append(f)
        summary_json = summary_json[7:]

    return summary_json


def analyze_log_files(directory, output_file):
    res_json = []
    total_files = 0
    unnormal_files = {"less_res": 0, "more_res": 0, "less_res_files": [], "more_res_files": []}
    for filename in os.listdir(directory):
        if not filename.endswith(".log"):
            continue
        if not filename.startswith("gnp"):
            continue
        total_files += 1
        summary_json = parse_file(unnormal_files, directory+"/"+filename)
        res_json.extend(summary_json)   
        print("Done: "+filename)
        print("\n")

    with open(output_file, "w") as f:
        json.dump(res_json, f, indent=2)

    print(unnormal_files)
    print("Total files: "+str(total_files))

analyze_log_files(".", "test_summary.json")

# def summarize_error_reason(less_res, more_res, file):
#     if not os.path.isfile(file):
#         print("Not a file: "+file)
#         return
#     labels = file.split("-")
#     if len(labels) != 4:
#         print("Not enough labels: "+ str(labels))
#         return

#     json_res = {}
#     print("Analyzing: "+file)
#     graph_file = labels[0]
#     graph = LoadJsonGraphFromFile(graph_file+".txt")
#     query_hop_num = int(labels[1])
#     shot_num = int(labels[2])
#     model_name = labels[3]
#     json_res["model_name"] = model_name
#     json_res["graph_file"] = graph_file.split("/")[-1]
#     json_res["query_hop_num"] = query_hop_num
#     json_res["representation"] = ""
#     json_res["shot_num"] = shot_num
#     json_res["wrong_edge_problem"] = 0
#     json_res["possibly_not_found"] = 0
#     json_res["total_score"] = 0
#     json_res["full_score"] = 0
#     json_res["token_usage"] = {}
    
#     summary_json = []
#     with open(file, 'r') as file:
#         new_json = json_res.copy()
#         for line in file:
#             if line.startswith("     Basic info:"):
#                 new_json["representation"] = line.split(", ")[2].strip()
#             if line.startswith("Total failed_num="):
#                 new_json["total_score"] = int(line.split(", total_score=")[1].split(",")[0].strip())
#                 new_json["full_score"] = int(line.split(", full_score=")[1].split(",")[0].strip())
#                 new_json["wrong_edge_problem"] = int(line.split(", wrong_edge_problem=")[1].split(",")[0].strip())
#                 new_json["possibly_not_found"] = int(line.split(", possibly_not_found=")[1].split(",")[0].strip())
#             elif line.startswith("Summary Token Usage:"):
#                 new_json["token_usage"] = parse_token_usage(line)
#                 summary_json.append(new_json.copy())
#                 new_json = json_res.copy()

#     if len(summary_json) == 6:
#         less_res += 1
#         for i in range(len(summary_json)):
#             if summary_json[i]["representation"] == "node_id+edge_id":
#                 summary_json[i]["representation"] = "randomStr+edge_id"
#             if summary_json[-1]["representation"] == "randomStr+edge_id":
#                 summary_json[-1]["representation"] = "<edge_id>"
#             if summary_json[-1]["representation"] == "<edge_id>":
#                 summary_json[-1]["representation"] = "node_id[:4]+edge_id"
#             if summary_json[-1]["representation"] == "node_id[:4]+edge_id":
#                 summary_json[-1]["representation"] = "<key=>node_id AND node_id[:4]+edge_id"
#     if len(summary_json)>7:
#         more_res += 1
#         summary_json = summary_json[7:]
#     return less_res, more_res, summary_json


# def analyze_all_logs_error_reason(directory):
#     summary_json = []
#     less_res = 0
#     more_res = 0
#     total_files = 0
#     for filename in os.listdir(directory):
#         if not filename.endswith(".log"):
#             continue
#         if not filename.startswith("gnp"):
#             continue
#         total_files += 1
#         less_res, more_res, json_res = summarize_error_reason(less_res, more_res, directory+"/"+filename)
        
#         summary_json.extend(json_res)
#         print("Done: "+filename)
#         print("\n")

#     with open("experiments/res_log/summary_error_reason.json", "w") as f:
#         json.dump(summary_json, f, indent=2)
#     print("Less res: "+str(less_res))
#     print("More res: "+str(more_res))
#     print("Total files: "+str(total_files))



    

# analyze_log_files("experiments/res_log")


