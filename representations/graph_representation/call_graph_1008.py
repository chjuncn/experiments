from graph_1008 import test_1hop, test_2hop, different_tokens_edge
from agents_lib import agent_util as agents


representation_names = {0: 'baseline',
                        1: 'node_id[-4:]+edge_id',
                        2: 'node_id+edge_id',
                        3: "randomStr+edge_id", 
                        4: "<edge_id>", 
                        5: "node_id[:4]+edge_id", 
                        6: "<key=>node_id AND node_id[:4]+edge_id", 
                        7: "node_id[:4]_edge_id",
                        8: "baseline_v2",
                        9: "node_id[:4]_edge_id_v2",
                        10: "node_id[:4]_[edge_id]_v2",
                        11: "[edge_id]_node_id[:4]_v2",
                        12: "node_id[:4]_(edge_id)_STR_v2",
                        13: "randomStr+edge_id_v2",
                        14: "[node_id[:8]]_edge_id",
                        15: "node_id[:8]-edge_id",
                        16: "node_id[:8]-edge_id_v2"} 
 # Replace with your actual list
model_list = ["mistralai/Mistral-7B-Instruct-v0.3", "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
              "google/gemma-2-9b-it", "google/gemma-2-27b-it", agents.Model.MIXTRAL, "meta-llama/Meta-Llama-3-70B-Instruct-Lite"]


def different_appendingtokens_performance(graph_file_name, shot_num=0, position="before", error_log_file=""):
    print("graph_file_name: ", graph_file_name)
    representation_list  = different_tokens_edge(graph_file_name, representation_names=representation_names, position=position)

    for model in model_list:
        if model in ["meta-llama/Meta-Llama-3-70B-Instruct-Lite" ]:
            continue
        for i, representation in enumerate(representation_list):
            if i not in [0,5]:
                continue
            if "v2" in representation_names[i]:
                baseline_graph = representation_list[8]
            else:
                baseline_graph = representation_list[0]
            test_1hop(model, representation_names[i], baseline_graph, representation, shot_num=shot_num, is_abs=True, error_log_file=error_log_file)


def two_hop_performance(graph_file_name, position="before", shot_num=1, error_log_file=""):
    print("graph_file_name: ", graph_file_name)
    representation_list  = different_tokens_edge(graph_file_name, representation_names=representation_names, position=position)

    for i, representation in enumerate(representation_list):
        if i != 7:
            continue
        for model in model_list:
            test_2hop(model, representation_names[i], representation_list[0], representation, shot_num=shot_num, error_log_file=error_log_file)



# file_name = "experiments/res_log/gnp_n10_p20.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)
file_name = "graph_representation/res_log/gnp_n15_p20.txt"
different_appendingtokens_performance(file_name, error_log_file=file_name)
# file_name = "experiments/res_log/gnp_n20_p20.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)

# file_name = "experiments/res_log/gnp_n10_p50.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)
# file_name = "experiments/res_log/gnp_n15_p50.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)
# file_name = "experiments/res_log/gnp_n20_p50.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)


