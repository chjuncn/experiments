# ENUMS

from enum import Enum
from dspy_utils import TogetherHFAdaptor
import random
from typing import Optional
import os
import pandas as pd

import hashlib
import json
import openpyxl

# Get a specific environment variable
api_key = os.environ.get('TOGETHER_API_KEY')
if api_key is None:
    print("NO API IS PROVIDED!")


class Model(str, Enum):
    LLAMA2 = "meta-llama/Llama-2-7b-hf"  # "togethercomputer/Llama-2-7B-32K-Instruct"
    LLAMA3 = "meta-llama/Llama-3-8b-chat-hf"
    MIXTRAL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    GPT_3_5 = "gpt-3.5-turbo-0125"
    GPT_4 = "gpt-4-0125-preview"
    GPT_4V = "gpt-4-vision-preview"
    GEMINI_1 = "gemini-1.0-pro-001"
    GEMINI_1V = "gemini-1.0-pro-vision-latest"
    QWEN = "Qwen/Qwen2-72B-Instruct"

    def __repr__(self):
        return f'{self.name}'


class ModelFactory:

    def __init__(self):
        self.all_models = [model.value for model in Model]
        self.proposers = [model for model in self.all_models if self._is_proposer(model)]
        self.aggregators = [model for model in self.all_models if self._is_aggregator(model)]

    def _is_proposer(self, model):
        # How to choose models from models pool
        return False

    def _is_aggregator(self, model):
        # How to choose models from models pool
        return True

    def getProposers(self):
        return [Model.QWEN, Model.MIXTRAL, Model.LLAMA3]

    def getAggregators(self):
        return [Model.MIXTRAL]


PROPOSER_PROMPT = """You're a helpful data scientist, you need to answer user questions: {question} based on the information provided to you. 
Please try to think this problem in different perspectives. Please don't explain and don't repeat yourself."""

AGGREGATOR_PROMPT = """You have been provided with a set of responses from various open-source models to the latest user query: {question}. Your
task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the
information provided in these responses, recognizing that some of it may be biased or incorrect. Your response
should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply
to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of
accuracy and reliability.

Responses from models:
{context}"""



# Data collection、
# Memory、
# Reflection: collect what you've done, and the feedback from the system/human, and reflect on it.
# Task planning: plan the task, and the sub-tasks, and the order of the tasks.
### action planning: based on the task, plan the actions, and the order of the actions.
# Tool management: when to use pre-defined tools, and when to use the LLMs.


# 1. reflect on the past logs
# 2. understand the current situation
# 3. plan the next steps


# NOTE: Change proposers from 1 to 2, the agent has higher chance to get the right answer for the simpl flow.
# NOTE: When the question is simple, we shouldn't use the complex flow, it will mess up the information pool.
# NOTE: When the question is simple, we shouldn't use too many proposers, as it will waste the resources.


# The goal of an agent is not about the Model, but the objective of this agent, so model can be configured, and
# the instruction prompt could be learned values.
class AgentABC:
    def __init__(self, proposers, aggregator, temperature_list: list[float] = None):
        self.proposer_models = []
        for i, proposer in enumerate(proposers):
            if temperature_list is not None:
                temp = temperature_list[i % len(temperature_list)]
            else:
                temp = 0.1
            param = {"temperature": temp}
            model = TogetherHFAdaptor(proposer, apiKey=api_key, **param)
            self.proposer_models.append(model)

        self.aggregator = TogetherHFAdaptor(aggregator, apiKey=api_key)

    def _answer(self, question, context: str, data_memory:str="", verbose:bool=False):
        params = {"question": question}
        prompt = PROPOSER_PROMPT.format(**params)
        if context != "":
            prompt += f"\n Below is previous answers for the same question: " + context + "\n"
            prompt += "Please based on all the available information and provide answer for this same question again. Please be concise. The response limitation is 300 words.\n"

        # When we use API, this model just don't remember anything about this agent.
        if data_memory != "":
            prompt += "\n\n Below is the data memory for this agent:\n" \
                      f"{data_memory}"

        final = []
        for model in self.proposer_models:
            response = model.request(prompt=prompt)
            answer_str = response["choices"][0]["text"]
            if verbose:
                print(self.__class__.__name__, model.model, answer_str)
            final.append(answer_str)
        return final

    def _aggregate_answers(self, question, context: str):
        if context == "":
            raise Exception("No answers to aggregate!!!")

        params = {"question": question, "context": context}
        prompt = AGGREGATOR_PROMPT.format(**params)
        response = self.aggregator.request(prompt=prompt)
        return response["choices"][0]["text"]

    def ask(self, question, context: str = "", rethink:int=1, data_memory: str=""):
        for i in range(rethink):
            answers = self._answer(question, context=context, data_memory=data_memory)
            joined = [f"{i}. {answer}\n" for i, answer in enumerate(answers)]  # Feed all answers to each model.
            context += "".join(joined)
        if len(self.proposer_models) > 1:
            return self._aggregate_answers(question, context)
        return answers[0]
    
    def aggregate_answer(self, question, context:str):
        return self._aggregate_answers(question, context)


# Finetuning model looks like a better approach when we need an agent for a specific dataset.
#      1. Finetuning LLMs with its data for a DataAgent might make more sense, small models should be good enough.
#      2. Memory for LLMs is important for this case.
class DataAgent(AgentABC):
    def __init__(self, proposers, aggregator, data):
        super().__init__(proposers, aggregator)
        self.data_base = data
        hashed = hashlib.sha256(str(data).encode()).hexdigest()[:5]
        self.agent_name = f"{self.__class__.__name__}_{hashed}"

    # incrementally add new data
    def _stream_in_data(self, new_data):
        prompt = "Please summarize the new data you just see: " + new_data
        prompt += "\nCombining what you've learned from previous data and the new data, what are the new insight you get?"
        prompt += " If yes, please update your knowledge base."
        response = self.ask(prompt)

    def get_data_summary(self):
        sampled_data = self.data_base
        prompt = "You're a helpful data analysts. Please summarize the data you see below: " + str(
            sampled_data) + ". \n\nPlease just summarize and don't make any suggestions."
        return self.ask(prompt)

    def query_data(self):
        return self.data_base

    def suggestion_to_action(self, suggestion):
        methods = dir(self.__class__)
        prompt = f"You have suggestion from the coordinator: {suggestion}. And you have {methods}, please return the " \
                 f"method function name only."
        response = self.ask(prompt)

        # assume the response is query_data
        return self.query_data
    
    def predict_future_data(self):
        prompt = "Please predict the future data based on the current data you have.\n The current data is: " + self.data_base
        return self.ask(prompt)
    
    def exam_data(self):
        prompt = "Please exam the data you have, and find the possible corrupted data in the dataset, and provide the exam result and explanation.\n The current data is: " + self.data_base
        return self.ask(prompt)


# ConductorAgent also could be mixed hardcoded+LLM, the goal of
# Conductor is like the previous orchestration module in the system.
# Each agent needs to know
#       1. its goal clearly.
#       2. hardcoded tools + LLM
#       3. recommend actions based on logs/metrics.
#       4. predict events based on logs/metrics.
class ConductorAgent(AgentABC):

    def __init__(self, proposers, aggregator):
        super().__init__(proposers, aggregator)

    def get_related_data_agent(self, avaliable_data_agents: list[DataAgent], question: str, rethink:int=1, verbose:bool=False):
        prompt = """You're a helpful data scientist. You're given a question and available information summary from multiple data agents to solve the question. Please
        use all the available information to decide which data agents might be useful for us to solve the question. 
        You should think step by step, and you can check if there're useful informaiton from different data agents. Please only return the data
        agent name in JSON format, example agent_name:NAME, reason:REASON"""
        prompt += "\nThe question is: " + question + "\n"

        for agent in avaliable_data_agents:
            summary = agent.get_data_summary()
            prompt += "\n\nAGENT_NAME: " + agent.agent_name + "\nSUMMARY:" + summary

        if verbose: 
            print(self.__class__.__name__, prompt)
        return self.ask(question, rethink=rethink)

    def data_integration(self, question, agents_result: list[str] = None, rethink:int=1):
        # Could be hardcoded function or LLM based question.
        prompt = f"""You're a helpful data scientist. You'll be given few datasets and a question, please join the data 
        reasonably to answer the question, please note:
        1. There is no repeated information. 
        2. You need to understand all the dataset to solve the question.
        3. You should naturally merge the data instead of just appending the the data together. 
        4. Please provide a new insight based on the integrated data. 
        5. Please return the final answer, no code is needed.
        The question is {question}
        
        The data is below:"""
        for i, res in enumerate(agents_result):
            prompt += "\n" + "The dataset " + str(i) + ": " + str(res)

        return self.ask(prompt,rethink=rethink)

    def if_accept_answer(self, question, answer, rethink:int=1):
        prompt = "Do you think the answer is correct to answer the question? " \
                 "Please return the result in the JSON format: good_enough:\"YES/NO\", reason:\"\""


        prompt += "\nQuestion: " + question + "\nAnswer: " + answer
        ans = self.ask(prompt, rethink=rethink)
        print("if_accept_answer ", ans)
        return ans

    def assign_tasks_to_data_agents(self, global_question, suggestion, available_agents: list[DataAgent], rethink:int=1):
        agents = [agent.agent_name for agent in available_agents]
        data_summaries = [ agent.agent_name +": " + agent.get_data_summary() + "\n" for i, agent in
                          enumerate(available_agents)]


        goal = "Please solve the question: " + global_question
        prompt = f"You have data agents {agents}, their data summaries are\n {data_summaries}.\n" \
                 f"You have goal: {goal}, and suggestion: {suggestion}. Please generate prompts for all the related data agents." \
                 f"Please return in JSON format, example: agent_name:NAME,prompt:PROMPT."
        response = self.ask(prompt,rethink=rethink)

        # This is hardcoded, ideally this should come from the response
        dic = {}
        for agent in available_agents:
            dic[agent.agent_name] = "please think it again."

        return dic


def read_xlsx(file_path):
    with open(file_path, "rb") as f:
        contents = f.read()
    return str(contents)


def parse_advice(msg):
    return {"good_enough": False, "msg": "The answer cannot be accepted. Please try again."}


# No summary needed, just query data, put them in a list and answer the question.
def test1_simple_flow(file1, file2, question):

    conductor = ConductorAgent([Model.MIXTRAL], Model.QWEN)
    dataAgent1 = DataAgent([Model.MIXTRAL], Model.QWEN, file1)
    dataAgent2 = DataAgent([Model.MIXTRAL], Model.QWEN, file2)
    name_map = {dataAgent1.agent_name: dataAgent1, dataAgent2.agent_name: dataAgent2}

     # all_agents = conductor.get_related_data_agent([dataAgent1, dataAgent2], question)
    all_agents = [dataAgent1.agent_name, dataAgent2.agent_name]
    data = []
    for agent_name in all_agents:
        agent = name_map[agent_name]
        data.append(agent.query_data())
    final = conductor.data_integration(question, data)

    print("##############final (0) #########: ", final)



def test2_complex_flow(file1, file2, question):
    conductor = ConductorAgent([Model.MIXTRAL], Model.QWEN)
    dataAgent1 = DataAgent([Model.MIXTRAL], Model.QWEN, file1)
    dataAgent2 = DataAgent([Model.MIXTRAL], Model.QWEN, file2)
    name_map = {dataAgent1.agent_name: dataAgent1, dataAgent2.agent_name: dataAgent2}
    context = ""

    ############## !!!!!!!get_related_data_agent never succeed.
    ############# Gemini can return the right answer.
    # related_agents = conductor.get_related_data_agent([dataAgent1, dataAgent2], question)
    all_agents = [dataAgent1.agent_name, dataAgent2.agent_name]
    ans = []
    for agent_name in all_agents:
        agent = name_map[agent_name]
        ans.append(agent.ask(question, data_memory=agent.query_data()))
    final = conductor.data_integration(question, ans)
    print("##############final (1) #########: ", final)


    print("\n\n\n")
    ####### Another Round #############################
    ######### Then agent decides if it should continue to discuss the problem and return possible better results.
    #########  1. The agent can learn from previous failed experiences.
    advice = conductor.if_accept_answer(question, final)
    result = parse_advice(advice) # hardcoded results

    if not result["good_enough"]:
        actions_for_agents = conductor.assign_tasks_to_data_agents(question, result["msg"], [dataAgent1, dataAgent2])
        responses = []
        for key in actions_for_agents:
            agent_name = key
            responses.append(name_map[agent_name].ask(actions_for_agents.get(key), data_memory=name_map[agent_name].query_data()))
        final = conductor.data_integration(question, responses)

    print("##############final (2) #########: ", final)




def data_agent_test():
    data1 = read_xlsx("data/num_game_1.txt")
    data3 = read_xlsx("data/num_game_3.txt")
    dataAgent1 = DataAgent([Model.MIXTRAL], Model.QWEN, data1)
    dataAgent3 = DataAgent([Model.MIXTRAL], Model.QWEN, data3)
    print("######### predict_future_data #########", dataAgent1.predict_future_data())
    print("######### exam_data #########", dataAgent3.exam_data())


data_agent_test()



## successed case
## works for simple dataset case.
## we cannot use get_summary.
#  1. read data from all agents
#  2.


# test1_simple_flow(read_xlsx("data/data1.txt"), read_xlsx("data/data2.txt"), "How does the person in room A to get out?")

######## Failed Case
##### I used simple dataset, but complex workflows.
# 1. get summary of the datasets, and let conductor decide which agents should work on this.
# 2. ask the question for each agent.
#     Comments: since the information is not enough to answer the question, LLM will fake some information,
#               which will pollute the information poll for next step.
# 3. conductor integrates the data from different data agents (previous step), and answer the question as the final answer.
# test2_complex_flow(read_xlsx("data/data1.txt"), read_xlsx("data/data2.txt"),
#                    "How does the person in room A to get out?")



## average (0,,99) = 49.5
## average (100, 199) = 149.5
## overall average = 99.5
## Failed case
## It's hard for the system to get right. Sometimes it will just mess up the simple calculations.
## we don't know where is wrong, and no fixing mechanism.
test1_simple_flow(read_xlsx("data/num_game_1.txt"), read_xlsx("data/num_game_2.txt"),
                  "what is the average number of all the numbers from all of the data agents?")



# Most of the time, successed case
### Conductor gives suggestions for what questions to ask to the data agents to answer the final questions.
### finally it can get it right (kind-of).

## self-correction mechanism
test2_complex_flow(read_xlsx("data/num_game_1.txt"), read_xlsx("data/num_game_2.txt"),
                  "what is the average number of all the numbers from all of the data agents?")



