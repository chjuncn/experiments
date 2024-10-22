from graph_1008 import test_1hop, test_2hop, different_tokens_edge
from agents_lib import agent_util as agents


def different_appendingtokens_performance(graph_file_name, position="before", error_log_file=""):
    print("graph_file_name: ", graph_file_name)
    json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json = different_tokens_edge(graph_file_name, position)

    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,json_graph, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,substring_key_json, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, full_key_json, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, random_token_json, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph,wrapper_token_json, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, substring_keyhead_json, error_log_file=error_log_file)
    # test_1hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, primary_key_substring_key_json, error_log_file=error_log_file)

    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, json_graph, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_key_json, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, full_key_json, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, random_token_json, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, wrapper_token_json, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_keyhead_json, error_log_file=error_log_file)
    test_1hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, primary_key_substring_key_json, error_log_file=error_log_file)

    test_1hop("google/gemma-2-9b-it", json_graph, json_graph, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, substring_key_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, full_key_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, random_token_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, wrapper_token_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, substring_keyhead_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-9b-it", json_graph, primary_key_substring_key_json, error_log_file=error_log_file)

    test_1hop("google/gemma-2-27b-it", json_graph, json_graph, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, substring_key_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, full_key_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, random_token_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, wrapper_token_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, substring_keyhead_json, error_log_file=error_log_file)
    test_1hop("google/gemma-2-27b-it", json_graph, primary_key_substring_key_json, error_log_file=error_log_file)

    if graph_file_name != "gnp_n30_p20.txt":
        test_1hop(agents.Model.MIXTRAL, json_graph, json_graph, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, substring_key_json, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, full_key_json, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, random_token_json, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, wrapper_token_json, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, substring_keyhead_json, error_log_file=error_log_file)
        test_1hop(agents.Model.MIXTRAL, json_graph, primary_key_substring_key_json, error_log_file=error_log_file)

        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, json_graph, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_key_json, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, full_key_json, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, random_token_json, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, wrapper_token_json, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_keyhead_json, error_log_file=error_log_file)
        test_1hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, primary_key_substring_key_json, error_log_file=error_log_file)


def two_hop_performance(graph_file_name, position="before", shot_num=1, error_log_file=""):
    json_graph, substring_key_json, full_key_json, random_token_json, wrapper_token_json, substring_keyhead_json, primary_key_substring_key_json = different_tokens_edge(graph_file_name, position)

    if graph_file_name != "gnp_n10_p20.txt":
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("mistralai/Mistral-7B-Instruct-v0.3", json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
        
        test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
        test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)

    test_2hop("google/gemma-2-9b-it", json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-9b-it", json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)

    test_2hop("google/gemma-2-27b-it", json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("google/gemma-2-27b-it", json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)

    test_2hop(agents.Model.MIXTRAL, json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop(agents.Model.MIXTRAL, json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)

    # print("\\\\\\\\\\\\\\\\n\n\n\n")
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, json_graph, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, full_key_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, random_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, wrapper_token_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, substring_keyhead_json, shot_num=shot_num, error_log_file=error_log_file)
    test_2hop("meta-llama/Meta-Llama-3-70B-Instruct-Lite", json_graph, primary_key_substring_key_json, shot_num=shot_num, error_log_file=error_log_file)

    # test_2hop("Qwen/Qwen2-72B-Instruct", json_graph)
    # test_2hop("Qwen/Qwen2-72B-Instruct", substring_key_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", full_key_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", random_token_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", wrapper_token_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", substring_keyhead_json)
    # test_2hop("Qwen/Qwen2-72B-Instruct", primary_key_substring_key_json)



# two_hop_performance("node_num_20_b6.txt", shot_num=0)

# file_name = "gnp_n5_p50.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)
# file_name = "gnp_n15_p20.txt"
# different_appendingtokens_performance(file_name, error_log_file=file_name)
# file_name = "gnp_n5_p20.txt"
# two_hop_performance(file_name, shot_num=2,  error_log_file=file_name+"_2hop")
# file_name = "gnp_n10_p20.txt"
# two_hop_performance(file_name, shot_num=2, error_log_file=file_name+"_2hop")
# file_name = "gnp_n15_p20.txt"
# two_hop_performance(file_name, shot_num=2, error_log_file=file_name+"_2hop")
# file_name = "gnp_n20_p20.txt"
# two_hop_performance(file_name, shot_num=2, error_log_file=file_name+"_2hop")
file_name = "gnp_n25_p20.txt"
two_hop_performance(file_name, shot_num=2, error_log_file=file_name+"_2hop")

