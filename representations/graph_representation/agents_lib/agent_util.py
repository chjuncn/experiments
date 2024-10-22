from enum import Enum
from agents_lib import dspy_utils
import random
from typing import Optional
import os
import pandas as pd
import regex as re # Use regex instead of re to used variable length lookbehind
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from together import Together


from typing import Any, Dict

# Get a specific environment variable
api_key = os.environ.get('TOGETHER_API_KEY')
if api_key is None:
    print("NO API IS PROVIDED!")


class Model(str, Enum):
    LLAMA2 = "meta-llama/Llama-2-7b-hf"  # "togethercomputer/Llama-2-7B-32K-Instruct"
    LLAMA3 = "meta-llama/Meta-Llama-3-70B-Instruct-Turbo"
    LLAMA3_1 = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
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
                temp = 0.0
            param = {"temperature": temp}
            model = dspy_utils.TogetherHFAdaptor(proposer, apiKey=api_key, **param)
            self.proposer_models.append(model)

        self.aggregator = dspy_utils.TogetherHFAdaptor(aggregator, apiKey=api_key)

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
    
    def simple_ask(self, question):
        try:
            response = self.proposer_models[0].request(prompt=question)
            answer_str = response["choices"][0]["text"]
            return answer_str, response["usage"]
        except Exception as e:
            print("Error in simple_ask", e)
            if isinstance(e, ValueError) and "max_new_tokens" in str(e):
                return "TOO LONG CONTEXT!", {}
            return "", {}
    
    def aggregate_answer(self, question, context:str):
        return self._aggregate_answers(question, context)
    
    def callback(self, topic, msg):
        raise NotImplementedError("Callback method should be implemented in the subclass.")


def print_table(output):
    for table in output:
        print("FINAL OUTPUT TABLE", table)
        header = table.header
        subset_rows = table.rows[:3]

        print("Table name:", table.name)
        print(" | ".join(header)[:100], "...")
        for row in subset_rows:
            print(" | ".join(row)[:100], "...")
        print()


def print_records(records):
    for record in records:
        fields = record._getFields()
        print("New Record: ")
        for field in fields:
            if field == "contents":
                continue
            print("  ", field, " = ", record.__dict__[field])


def is_json(source:str) -> bool:
  try:
    json.loads(source)
  except ValueError as e:
    return False
  return True

def getJsonFromAnswer(answer: str) -> Dict[str, Any]:
    """
    This function parses an LLM response which is supposed to output a JSON object
    and optimistically searches for the substring containing the JSON object.
    """
    if answer.find("{") == -1:
        if answer.find("`") != -1:
            answer = answer.replace("`", "")
        if answer.find("json") != -1:
            answer = answer.replace("json", "")
        answer = "{" + answer +"}"
    if not answer.strip().startswith("{"):
        # Find the start index of the actual JSON string
        # assuming the prefix is followed by the JSON object/array
        start_index = answer.find("{") if "{" in answer else answer.find("[")
        if start_index != -1:
            # Remove the prefix and any leading characters before the JSON starts
            answer = answer[start_index:]

    if not answer.strip().endswith("}"):
        # Find the end index of the actual JSON string
        # assuming the suffix is preceded by the JSON object/array
        end_index = answer.rfind("}") if "}" in answer else answer.rfind("]")
        if end_index != -1:
            # Remove the suffix and any trailing characters after the JSON ends
            answer = answer[: end_index + 1]

    # Handle weird escaped values. I am not sure why the model
    # is returning these, but the JSON parser can't take them
    answer = answer.replace(r"\_", "_")

    # Remove https and http prefixes to not conflict with comment detection
    # Handle comments in the JSON response. Use regex from // until end of line
    answer = re.sub(r"(?<!https:)\/\/.*$", "", answer, flags=re.MULTILINE)
    if not is_json(answer):
        # Find the last bracket index
        answer = findLastBracketIndex(answer)
    return json.loads(answer)


def findLastBracketIndex(source:str) -> str:
    end_index = source.rfind("}")
    if end_index == -1:
        return ""
    
    final = ""
    i = end_index - 1
    stack = ["}"]
    while i >= 0 and len(stack) > 0:
        if source[i] == "}":
            stack.append("}")
        elif source[i] == "{":
            stack.pop()
        i -= 1
    if len(stack) == 0:
        final = source[i+1:end_index+1]
    return final


def draw_graph():
    input = ""


    json_input = json.loads(input)
    pz = ""
    for i, key in enumerate(json_input):
        value = json_input[key]
        int_value = 0
        for j in value:
            if j:
                int_value += 1
            else:
                int_value -= 1
        pz += str(i) + "," + str(int_value) + "\n"
    print(pz)



# source = """A: In the given dictionary "<key>=274c8f2d-b776-4f5c-a0b5-1554daa5e1ba" has the d\_value={ "edge\_1e1ba": "382e7282-27ec-4c4b-bcff-7f4b43065e61", "edge\_2e1ba": "801af878-3279-468c-a993-a6a0d46cf1c9" }, and then extract value for "edge\_2e1ba" from d\_value, the final answer is

# {"<key>=274c8f2d-b776-4f5c-a0b5-1554daa5e1ba": "801af878-3279-468c-a993-a6a0d46cf1c9"}. """
# print(getJsonFromAnswer(source))


class TogetherCall:
    def __init__(self, model, stop_words=["<eos>","<end_of_turn>"], api_key=api_key, **kwargs):
        self.api_base = "https://api.together.xyz/inference"
        self.token = api_key
        self.model = model
        self.stop_words = stop_words
        self.client = Together(api_key=api_key)

    @retry(
        wait=wait_exponential(multiplier=2, max=10),
        stop=stop_after_attempt(2),
    )
    def exe_my_request(self, question, data_source, **kwargs):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": question}], #, {"role": "system", "content": "You are a helpful assistant, you will follow user's instruction to extract data from the given data source. Data Source:\n" + data_source}],
            max_tokens=512,
            temperature=0,
            top_p=1,
            top_k=20,
            repetition_penalty=1,
            # stop=self.stop_words,
            stream=False
        )

        # for attr in dir(response):
        #     print("obj.%s = %r\n" % (attr, getattr(response, attr)))
        return response.choices[0].message.content
        # for chunk in response:
            # print(chunk.choices[0].delta.content or "", end="", flush=True)
            

        # print("+++++++++++++", type(response))