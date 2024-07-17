from enum import Enum
from dspy_utils import TogetherHFAdaptor
import random
from typing import Optional
import os
import pandas as pd


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
    
    def callback(self, topic, msg):
        raise NotImplementedError("Callback method should be implemented in the subclass.")

