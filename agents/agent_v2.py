# ENUMS

from enum import Enum
from dspy_utils import TogetherHFAdaptor
import random
from typing import Optional
import os

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


PRPOSER_PROMPT = """Imagine you're a helpful assistant, you need to answer user questions {question}. Please explore multiple possibilities and generate diverse perspectives. And please don't repeat yourself."""
AGGREGATOR_PROMPT = """You have been provided with a set of responses from various open-source models to the latest user query: {question}. Your
task is to synthesize these responses into a single, high-quality response. It is crucial to critically evaluate the
information provided in these responses, recognizing that some of it may be biased or incorrect. Your response
should not simply replicate the given answers but should offer a refined, accurate, and comprehensive reply
to the instruction. Ensure your response is well-structured, coherent, and adheres to the highest standards of
accuracy and reliability.

Responses from models:
{context}"""


# The goal of an agent is not about the Model, but the objective of this agent, so model can be configured, and
# the instruction prompt should be learned values.
class Agent:
    default_temperature = 0.7
    def __init__(self, proposers: list[str], aggregator: str, temperature_list: list[float] = None):
        self.proposer_models = []
        for i, proposer in enumerate(proposers):
            temperature = self.default_temperature
            if temperature_list is not None and i < len(temperature_list):
                temperature = temperature_list[i]
            param = {"temperature": temperature}
            model = TogetherHFAdaptor(proposer, apiKey=api_key, **param)
            self.proposer_models.append(model)

        self.aggregator = TogetherHFAdaptor(aggregator, apiKey=api_key)

    def answer(self, question, context: str):
        params = {"question": question}
        prompt = PRPOSER_PROMPT.format(**params)
        if context != "":
            prompt += f"\n Below is previous answers for the same question: " + context + "\n"
            prompt += "Please based on the all available information and provide answer for this same question again. Please be concise. The response limitation is 300 words.\n"

        final = []
        for model in self.proposer_models:
            response = model.request(prompt=prompt)
            answer_str = response["choices"][0]["text"]
            print(model.model, answer_str)
            final.append(answer_str)
        return final

    def aggregate_answers(self, question, context: str):
        if context == "":
            raise Exception("No answers to aggregate!!!")

        params = {"question": question, "context": context}
        prompt = AGGREGATOR_PROMPT.format(**params)
        response = self.aggregator.request(prompt=prompt)
        return response["choices"][0]["text"]


def test():
    modelFactory = ModelFactory()
    agent = Agent(modelFactory.getProposers(), modelFactory.getAggregators()[0], [0.7, 3, 1])
    context = ""
    question1 = "what's the answer of this equation: (4+5)*2*(9-1)?"
    question2 = "What is the capital of the country where the Taj Mahal is located?"
    question3 = "Calculate (3/5)*(4/7)"
    # right answer for question4 is 7/15 = 0.4667
    # Using
    question4 = """There are 6 identical balls, each marked with a number from 1 to 6. 
    Three balls are randomly drawn without replacement from these 6 balls, one at a time. 
    Let m denote the average of the numbers on the first two balls drawn, and n denote the average of the numbers on all
    three balls drawn. What is the probability that the absolute difference between  m  and n does not exceed 1/2?"""

    question5="""In a cage, there are chickens and rabbits with a total of 35 heads and 94 feet. 
    How many chickens and how many rabbits are there?"""
    for i in range(3):
        answers = agent.answer(question5, context)
        joined = [f"{i}. {answer}\n" for i, answer in enumerate(answers)]  # Feed all answers to each model.
        context += "".join(joined)

    print(context)
    final = agent.aggregate_answers(question5, context)
    print("The final answer >>>>>>>>>>>>>>>>>>>\n", final)


test()
