#!/usr/bin/env python3
"""This scripts is a demo for the biofabric data integration.
Make sure to run:
python src/cli/cli_main.py reg --path testdata/biofabric-urls/ --name biofabric-urls

"""

import context
# from palimpzest.constants import Model
# import palimpzest as pz
from agents_lib import agent_util as agents
import pdb
import gradio as gr

import numpy as np
import pandas as pd

import argparse
import requests
import json
import time
import os

OP_PROMPT = """
1. There are only 6 operators avaiable in the whole system: READ_SOURCE(source_id), CONVERT(source_schema, target_schema), EXTRACT(source, target_schema), FILTER(source, condition), MERGE(left, right, key), APPEND(source, others) Please analyze carefully which operate you might need for each step.
    1.1 READ_SOURCE(source_id) can read the data from the source_id, for example, a file, a database, etc.
    1.2 CONVERT(target_schema) can convert any kind of files to target_schema data records and just drop unuseful information.
    1.3 EXTRACT(source, target_schema) can extract data to target_schema data records and just drop unuseful information. for example, we can use EXTRACT() to extract a document to a list of records with targe_schema.
    1.4 FILTER(source, condition) can filter out the records that meet the condition from the source. The condition could be a semantic condition, e.g. a natural language sentence.
    1.5 MERGE(left, right, key) can merge the records from left to right data sources based on the key, e.g fullfill each other's values.
    1.6 APPEND(source, target) can append the records from source to target. 

2. Please decompose the tasks to the minimal automic steps and each step calls one operator.
2. You need to think about how to populate the output schema from different data sources.
3. You need to let executor know which part of information they should focus on to get the information they need.
4. Please be clear your recommendation is for which data source.
5. You need to think about how to join data from different data sources when necessary.
6. Please make sure to scan and analysze all the information, report the information for highly relevant items.
7. Please output by record, and each record is in the output schema.
8. Please note that you don't have to use all the operators, just use the operators you need.
"""


# class Movie(pz.Schema):
#     """Represents a movie."""

#     name = pz.Field(
#         desc="The name of a movie. This is a natural language title, not a number or letter.",
#         required=True,
#     )
#     genre = pz.Field(
#         desc="The genre of a movie. This is a natural language title, not a number or letter.",
#         required=False,
#     )
#     releaseYear = pz.Field(
#         desc="The year a movie was released. This is a number.", required=False
#     )
#     score = pz.Field(
#         desc="The score from users' rating. This is a number.", required=False
#     )
#     budget = pz.Field(desc="The budget of a movie.", required=False)
#     global_gross = pz.Field(desc="The worldwide gross of a moive.", required=False)
#     user_reviews = pz.Field(
#         desc="The summary of all the user reviews, please put your insight about the summary in it. Generally this should align with movie score.",
#         required=False,
#     )


class Tester(agents.AgentABC):
    def __init__(self, proposers, aggregator):
        super().__init__(proposers, aggregator)

    def verify_prompt(
        self, suggestion: str, data_sources: list[str] = None, rethink: int = 1
    ):
        prompt = """You're a helpful data scientist. You're given suggestions to execute a plan. Can you generate a plan to evaluate the results from different perspectives?

        1. Completeness.
        2. Correctness.
        3. Relevance.

        """

        prompt += "\nThe suggestion is: " + suggestion + "\n"
        prompt += "\nThe data sources are:"
        for i, source in enumerate(data_sources):
            prompt += f"\n\Source {i} : " + str(source.contents)

        return self.ask(prompt, rethink=rethink)

    def verify(
        self,
        goal,
        data_sources: list[str] = None,
        result: str = None,
        verify_prompt: str = None,
        rethink: int = 1,
    ):
        prompt = verify_prompt

        prompt += "\nThe data sources are: "
        for i, source in enumerate(data_sources):
            prompt += f"\n\Source {i} : " + str(source.contents)
        prompt += "\nThe request is " + goal + "\n"

        prompt += "\nThe result is: " + result + "\n"

        return self.ask(prompt, rethink=rethink)


class Executor(agents.AgentABC):
    def __init__(self, proposers, aggregator):
        super().__init__(proposers, aggregator)

    def suggestion_to_action(
        self,
        goal: str,
        suggestion: str,
        data_sources: list[str] = None,
        rethink: int = 1,
    ):
        prompt = """You're a helpful data scientist. You're given suggestions to execute a plan. Please think about the suggestion and execute the plan step by step.
        Please return the result in JSON format.
        """

        prompt += "\nThe final goal is: " + goal + "\n"
        prompt += "\nThe suggested plan is: " + suggestion + "\n"

        if isinstance(data_sources, list):
            for i, source in enumerate(data_sources):
                prompt += f"\n\Source {i} : " + str(source.contents)
        else:
            prompt += "\n\Data Source : " + str(data_sources)

        return self.ask(prompt, rethink=rethink)


class Planner(agents.AgentABC):
    def __init__(self, proposers, aggregator, temperature_list: list[float] = None):
        super().__init__(proposers, aggregator, temperature_list)

    def gather_information(
        self,
        goal: str,
        avaliable_data_sources: list[str],
        rethink: int = 1,
    ):
        self.goal = goal
        self.sources = avaliable_data_sources

    def analyze_goal_and_make_pz_plan(self, rethink: int = 1):
        prompt = ""
        sources = ""
        if isinstance(self.sources, list):
            for i, source in enumerate(self.sources):
                sources += f"\n\Data Source {i} : " + str(source.contents)
        else:
            sources = "\n\Data Source : " + self.sources

        prompt += (
            f"""You're a helpful data scientist. You're given a request: {self.goal}.
                    Please analyze the request and try to make a plan, including a sequence of actions to fullfill the request.
                    """
            + OP_PROMPT
        )
        if sources != "":
            prompt += f"The input data sources are: \n{sources}"

        return self.ask(prompt, rethink=rethink)

    def analyze_goal_and_make_plan(self, rethink: int = 1):
        prompt = """You're a helpful data scientist. You're given a request to integrate data from different data sources.
        Please analyze the request and try to make a plan. This plan should include a sequence of actions to achieve the request.
        
        1. You need to think about how to populate the output schema from different data sources.
        2. You need to think about how to join data from different data sources.
        2. Please be clear your recommendation is for which data source.
        3. Please make sure to analysze all the information, report the information for highly relevant items.
        4. Please output by record, and each record is in the output schema.
        """

        prompt += "\nThe request is: " + self.goal + "\n"

        for i, source in enumerate(self.sources):
            prompt += f"\n\Source {i} : " + str(source.contents)

        # if verbose:
        #     print(self.__class__.__name__, prompt)
        return self.ask(prompt, rethink=rethink)

    def reflection(self, result: str, rethink: int = 1):
        prompt = "The question is: " + self.goal + "\n\n"
        prompt += "\nThe data is:\n"

        for i, source in enumerate(self.sources):
            prompt += f"\n\Source {i}: " + str(source.contents)

        prompt += "\nThe result is: " + result + "\n"

        prompt += """Please reflect on the result, and tell us know if the result is correct and complete, and returen in JSON format, e.g. result='correct'or'wrong', suggestion=''."""
        return self.ask(prompt, rethink=rethink)
    
    def should_split_datasource(self, sourceSchema:str, outputSchema:str):
        ## TODO Only demo for Convert for now.
        prompt = f"""Given a data source with input schema:" + {str(sourceSchema)} + ", and we need to extract data from the source to the output schema: " + {str(outputSchema)} + ", in order to do this, should we split the source content so that the executor can process the source one by one?

You need to consider that the input data granlurity should match the output granlurity.

Please return return the decision in JSON format, e.g. result='split'or'not_split', on="one attribute from the input schema:{str(sourceSchema)}", how_to="one of the following methods: to_list or split by '\n' ", reason='because ...'
           """
        
        print("should_split_datasource", prompt)
        response = self.ask(prompt, rethink=1)
        print(response)


################################### 1. naive_pz ###################################
# def naive_pz():
#     # final goal: populate the movie schema from the report, review and insert the new records to DB.
#     report = pz.Dataset("m-report", schema=pz.File)
#     report_out = report.convert(
#         Movie,
#         desc="Polulate the movie schema from the report source",
#         cardinality="oneToMany",
#     )
#     mreview = pz.Dataset("m-review", schema=pz.File)
#     mreview_out = mreview.convert(
#         Movie,
#         desc="Polulate the movie schema from the review source",
#         cardinality="oneToMany",
#     )

#     report_records, plan, stats = pz.Execute(
#         report_out,
#         policy=pz.MaxQuality(),
#         nocache=True,
#         allow_code_synth=False,
#         allow_token_reduction=False,
#         available_models=[Model.LLAMA3_70B, Model.LLAMA3_1_70B, Model.MIXTRAL],
#         execution_engine=engine,
#     )

#     mreview_records, plan, stats = pz.Execute(
#         mreview_out,
#         policy=pz.MaxQuality(),
#         nocache=True,
#         allow_code_synth=False,
#         allow_token_reduction=False,
#         available_models=[Model.LLAMA3_70B, Model.LLAMA3_1_70B, Model.MIXTRAL],
#         execution_engine=engine,
#     )

#     agents.print_records(report_records)
#     print("=====================================")
#     agents.print_records(mreview_records)

# #     print("""=====================================
# # If the schema is predefined and deterministic, the data is strucutred data, we should just use the traditional ways to join/merge the data.
# # =====================================""")
#     endTime = time.time()
#     print("Elapsed time:", endTime - startTime)


################################### 2. planner_with_pz ###################################
def planner_with_pz():
    planner, executor, tester, data_sources, sources_str = setup()

    final_goal = f"""Please populate the output schema {str(Movie)} for all the movies mentioned in thedata sources, the returned records' key is movie name. Attributes values is null if the source data is not present."""

    planner.gather_information(final_goal, data_sources)
    suggestion = planner.analyze_goal_and_make_pz_plan()
    print("\n\n1================\n", suggestion)

    result = executor.suggestion_to_action(final_goal, suggestion, data_sources)
    print("\n\n2================\n", result)

    verified_res = tester.verify(final_goal, data_sources, result, tester.verify_prompt(suggestion, data_sources))
    print("\n\n3================\n", verified_res)
    # output = coordinator.reflection(output)

    # print("\n\n4================\n", verified_res)

    """
    {
    'The Godfather',
    'The Godfather: Part II',
    'The Shawshank Redemption',
    'The Lord of the Rings: The Return of the King',
    'Paranormal Activity',
    'The Blair Witch Project',
    'Mad Max',
    'Avatar (2009)',
    'Titanic (1997)',
    'The Dark Knight',
    'Jurassic Park'
    }
    """


################################### 3. planner_with_pz_key_info ###################################
def planner_with_pz_key_info():
    planner, executor, tester, data_sources, sources_str = setup()

    # (1) Let model figure out the topic.
    # question2 = """Please read all the data sources, and let me know what is the one topic of these data sources about, and who might be most farmiliar with this topic.
    # Please give me a short answer in one sentence, you should just choose one topic for all the data. Please return the position in JSON format."""
    # question2 += "\nThe data sources are: " + sources
    # topics = planner.ask(question2)
    # print("\n\n1================\n",topics)

    # (2) Topic + data scientist to figure out the movie set.
    question1 = (
        """You're a film industry professional and a data scientist, please help me extract all the movie names from all the data sources, and return the result in a set. 
    
    Please scan the data sources carefully, the data might present in different format.

    Please think step by step, don't explain and just return the final set.
    The data sources are: """
        + sources_str
    )
    movie_names = planner.ask(question1)
    print("\n\n2================\n", movie_names)

    # (3) Ask the final question, filled with key information from previous steps.
    final_goal = f"""Please populate the output schema {str(Movie)} for all the movies mentioned in the
      data sources, {movie_names}, the returned records' key is movie name."""
    planner.gather_information(final_goal, data_sources)
    suggestion = planner.analyze_goal_and_make_pz_plan()
    print("\n\n3================\n", suggestion)

    result = executor.suggestion_to_action(final_goal, suggestion, data_sources)
    print("\n\n4================\n", result)


################################### 4. planner_with_pz_inference ###################################
def planner_with_pz_inference():
    planner, executor, tester, data_sources, sources_str = setup()

    final_goal = f"""Please populate the output schema {str(Movie)} for all the movies mentioned in the data sources, the returned records' key is movie name."""
    question1 = f"In order to answer the question: {final_goal}, and the data sources: {sources_str}. \nwhat is the most important information I need? Please list just 1 item and extract information for them."
    key_info = planner.ask(question1)
    print("\n\n1================\n", key_info)

    question2 = final_goal + "\n\n" + key_info
    planner.gather_information(question2, data_sources)
    suggestion = planner.analyze_goal_and_make_pz_plan()
    print("\n\n2================\n", suggestion)
    result = executor.suggestion_to_action(final_goal, suggestion, data_sources)
    print("\n\n3================\n", result)


################################### 5. planner_ask_random_question ###################################
def planner_ask_random_question():
    planner, executor, tester, data_sources, sources_str = setup()

    final_goal = """can you recommend a moive for a 10 years old?"""
    question1 = f"In order to answer the question: {final_goal}, and the data sources: {sources_str}. \nwhat is the most important information I need? Please list just 1 item and extract information for them."
    key_info = planner.ask(question1)
    print("\n\n1================\n", key_info)

    question2 = final_goal + "\n\n" + key_info
    planner.gather_information(question2, data_sources)
    suggestion = planner.analyze_goal_and_make_pz_plan()
    print("\n\n2================\n", suggestion)
    result = executor.suggestion_to_action(final_goal, suggestion, data_sources)
    print("\n\n3================\n", result)


################################### 6. Legal Discovery workload ###################################
def legal_discovery_with_planner():
    planner = Planner([agents.Model.LLAMA3], agents.Model.QWEN)
    executor = Executor([agents.Model.LLAMA3], agents.Model.QWEN)

    class Email(pz.Schema):
        sender = pz.Field(desc="The sender of the email", required=True)
        subject = pz.Field(desc="The subject of the email", required=True)

    final_goal = f"""Find out emails that are related to corporate fraud (e.g., by mentioning a specific fraudulent investment vehicle, by discussing how to do fraud, by hint any kind of fraud and so on). 

    Please return the the schema in {str(Email)} if the email fits the conditions, otherwise return nothing.
    """

    files = pz.TextFileDirectorySource(
        path="testdata/enron-eval-tiny", dataset_id="enron-eval-tiny"
    )
    num_files = len(files)
    for i in range(num_files):
        sources_str = f"\n Data Srouce {i}: \n" + files.getItem(i).contents
        question1 = f"Please list if the email is related to corporate fraud and why for all the emails. The email is : \n\n{sources_str}, please also return the sender and subject of this email."
        key_info = planner.ask(question1)
        print("\n\n================\n", key_info)




    # question1 = f"In order to answer the question: {final_goal} with the data sources: {sources_str}. \nhow should we define the condition to do filter?"
    # question1 = f"Please list if the email is related to corporate fraud and why for all the emails. The emails are: \n\n{sources_str}"
    # key_info = planner.ask(question1)
    # print("\n\n================\n", key_info)


################################### 7. Real Estate Search ###################################
def real_estate_with_planner():
    planner = Planner([agents.Model.LLAMA3], agents.Model.QWEN)
    executor = Executor([agents.Model.LLAMA3], agents.Model.QWEN)

    class House(pz.Schema):
        home_id = pz.Field(desc="The id of the house", required=True)

    final_goal = f"""Find out houses meeting the following conditions: (1) modern and attractive (2) within two miles of work.

    Imagine you are be given a set of houses with images and text descriptions. You need to analyze the sources and make a plan to find the houses that meet the conditions. 
    
    Please return the output in schema: {str(House)} for emails that are related to corporate fraud.
    """

    # question1 = f"In order to answer the question: {final_goal}. \n. What is the most information you might need to understand? Please list just 1 item."
    # key_info = planner.ask(question1)
    # print("\n\n1================\n", key_info)

    question2 = final_goal ##+ "\n" + key_info
    planner.gather_information(question2, "")
    suggestion = planner.analyze_goal_and_make_pz_plan()
    print("\n\n========suggestion========\n", suggestion)


################################### Main ###################################


def setup():
    planner = Planner([agents.Model.LLAMA3_1], agents.Model.QWEN)
    executor = Executor([agents.Model.LLAMA3_1], agents.Model.QWEN)
    tester = Tester([agents.Model.LLAMA3_1], agents.Model.QWEN)

    data_sources = [
        pz.FileSource(
            dataset_id="m-report", path="experiments/testdata/movie_business_report.txt"
        ).getItem(0),
        pz.FileSource(
            dataset_id="m-review", path="experiments/testdata/movie_reviews.txt"
        ).getItem(0),
        pz.FileSource(dataset_id="m-db", path="experiments/testdata/db.txt").getItem(0),
    ]

    sources_str = ""
    for i, source in enumerate(data_sources):
        sources_str += f"\n\Source {i} : " + str(source.contents)

    return planner, executor, tester, data_sources, sources_str


if __name__ == "__main__":
    startTime = time.time()
    parser = argparse.ArgumentParser(description="Run a simple demo")
    parser.add_argument(
        "--no-cache", action="store_true", help="Do not use cached results"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Do not use cached results", default=True
    )
    parser.add_argument(
        "--from_xls",
        action="store_true",
        help="Start from pre-downloaded excel files",
        default=False,
    )
    parser.add_argument(
        "--policy", type=str, help="The policy to use", default="quality"
    )
    parser.add_argument(
        "--engine", type=str, help="The engine to use", default="sequential"
    )

    args = parser.parse_args()
    no_cache = args.no_cache
    verbose = args.verbose
    from_xls = args.from_xls
    policy = args.policy
    engine = args.engine
    if engine == "sequential":
        engine = pz.SequentialSingleThreadExecution
    elif engine == "parallel":
        engine = pz.PipelinedParallelExecution

    if no_cache:
        pz.DataDirectory().clearCache(keep_registry=True)

    if policy == "cost":
        policy = pz.MinCost()
    elif policy == "quality":
        policy = pz.MaxQuality()
    else:
        policy = pz.UserChoice()

    # naive_pz() # 1
    # planner_with_pz()  # 2
    # planner_with_pz_key_info()  # 3 key information should be solved by expensive models, then it will be easier for the latter part to get right.
    # planner_with_pz_inference()  # 4
    # planner_ask_random_question() # 5 It's interesting to see how the model find the "most important information" for the question.
    legal_discovery_with_planner() # 6
    # real_estate_with_planner() # 7