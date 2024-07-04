# ENUMS

from enum import Enum
from dspy_utils import TogetherHFAdaptor
import random
from typing import Optional
import os

# Get a specific environment variable
api_key = os.environ.get('TOGETHER_API_KEY')
api_key = "bacc34a6ef17118ebba27682e5bc71f484a409b54d30f7eb500134622239e0bb"
if api_key is None:
    print("NO API IS PROVIDED!")

class Model(str, Enum):
    LLAMA2 = "meta-llama/Llama-2-7b-hf" # "togethercomputer/Llama-2-7B-32K-Instruct"
    LLAMA3 = "meta-llama/Llama-3-8b-chat-hf"
    MIXTRAL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    GPT_3_5 = "gpt-3.5-turbo-0125"
    GPT_4 = "gpt-4-0125-preview"
    GPT_4V = "gpt-4-vision-preview"
    GEMINI_1 = "gemini-1.0-pro-001"
    GEMINI_1V = "gemini-1.0-pro-vision-latest"
    YI_MODEL = "Qwen/Qwen2-72B-Instruct"

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
        return [Model.YI_MODEL, Model.MIXTRAL]

    def getAggregators(self):
        return [Model.MIXTRAL]

PRPOSER_PROMPT="""Imagine you're a helpful assistant, you need to answer user questions {question}. Please explore multiple possibilities and generate diverse perspectives. And please don't repeat yourself."""
AGGREGATOR_PROMPT="""You have been provided with a set of responses from various open-source models to the latest user query: {question}. Your
task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the
information provided in these responses, recognizing that some of it may be biased or incorrect. Your response
should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply
to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of
accuracy and reliability.

Responses from models:
{context}"""


# The goal of an agent is not about the Model, but the objective of this agent, so model can be configured, and
# the instruction prompt should be learned values.
class Agents:

    def __init__(self, proposers:list[str], aggregator:str):
        # params = {"temperature": temperature+random(0, 0.01)}
        self.proposer_models = [TogetherHFAdaptor(model, apiKey=api_key) for model in proposers]
        self.aggregator = TogetherHFAdaptor(aggregator, apiKey=api_key)

    def answer(self, question, context: str):
        params = {"question": question}
        prompt = PRPOSER_PROMPT.format(**params)
        if context != "":
            prompt += f"\n Below is previous answers for the same question: " + context + "\n"
            prompt += "Please based on the all available information and provide answer for this same question again.\n"

        final = []
        for model in self.proposer_models:
            response = model.request(prompt=prompt)
            answer_str = response["choices"][0]["text"]
            print(model.model, answer_str)
            final.append(answer_str)
        return final

    def aggregate_answers(self, question, context: str):
        if context =="":
            raise Exception("No answers to aggregate!!!")

        params = {"question": question, "context":context}
        prompt = AGGREGATOR_PROMPT.format(**params)
        response = self.aggregator.request(prompt=prompt)
        return response["choices"][0]["text"]



def test():
    modelFactory = ModelFactory()
    agents = Agents(modelFactory.getProposers(), modelFactory.getAggregators()[0])
    context = ""
    question1 = "what's the answer of this equation: (4+5)*2*(9-1)?"
    question2 = "What is the capital of the country where the Taj Mahal is located?"
    for i in range(3):
        answers = agents.answer(question1, context)
        joined = [f"{i}. {answer}\n" for i, answer in enumerate(answers)] # Feed all answers to each model.
        context += "".join(joined)

    print(context)
    final = agents.aggregate_answers(question1, context)
    print("The final answer >>>>>>>>>>>>>>>>>>>\n", final)


test()



