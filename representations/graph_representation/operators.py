import context
from palimpzest.constants import Model
import palimpzest as pz
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
import data_integration_demo as did
from typing import Any, Dict, List


class Rows(pz.Schema):
    ages = pz.ListField(
        element_type=pz.StringField, desc="The patient age of all rows.", required=True
    )
    # gender = pz.StringField(desc="the gender of the patient of all rows.", required=True)
    # id = pz.StringField(desc="case id or sample id or index of all rows.", required=True)
    # others = pz.StringField(desc="other attributes that might be important in this dataset of all rows.", required=True)
    def asJSONStr(self, record_dict: Dict[str, Any], *args, **kwargs) -> str:
        """Return a JSON representation of an instantiated object of this Schema"""
        # Take the rows in the record_dict and turn them into comma separated strings
        rows = []
        # only sample the first MAX_ROWS
        if "rows" in record_dict:
            for i, row in enumerate(record_dict["rows"][:3]): # TODO how to divide rows automatically.
                rows += [",".join(map(str, row)) + "\n"]
            record_dict["rows"] = rows
            header = ",".join(record_dict["header"])
            record_dict["header"] = header

        return super(Rows, self).asJSONStr(record_dict, *args, **kwargs)

def print_table(output, fields:set=None):
    if fields is None:
        fields = set(["rows"], ["header"], ["name"])
    
    for table in output:
        fields = set(table._getFields())
        if "name" in fields:
            print("Table name: ", table.name)
        if "header" in fields:
            print("Header: ", table.header)
        if "age" in fields:
            print("Age: ", table.age)
        if "rows" in fields:
            for row in table.rows[:2]:
                print(" | ".join(row))
        print()


def setup():
    planner = did.Planner([agents.Model.MIXTRAL], agents.Model.MIXTRAL)
    executor = did.Executor([agents.Model.MIXTRAL], agents.Model.MIXTRAL)

    data_source = pz.Dataset("biofabric-tiny", schema=pz.XLSFile)
    patient_tables = data_source.convert(pz.Table, desc="All tables in the file", cardinality="oneToMany")
    patient_tables = patient_tables.filter("The table contains the patient age.", depends_on="rows")
    patient_tables = patient_tables.convert(Rows, desc="Rows in the file", depends_on="rows", cardinality="oneToMany")

    tables, plan, stats  =  pz.Execute(patient_tables,
                                supervisor=planner,
                                policy = policy,
                                nocache=True,
                                allow_code_synth=False,
                                allow_token_reduction=False,
                                available_models=[Model.MIXTRAL],
                                execution_engine=engine)

    print_table(tables, (["name"], ["header"], ["age"]))

    print(plan)
    print(stats)

    return planner, executor, data_source



def planner_with_pz_key_info():
    planner, executor, data_sources = setup()

    question1 = (
        """You're a helpful data scientist who has been asked to analyze the data sources. Please return the row with patient age?

    The data sources are: 
SampleID	Clinical	Mutation	CNV	miRNA-seq	mRNA-seq	Label-free Proteome	TMT Proteome	TMT Proteome (Normal)	TMT Phosphoproteome	TMT Phosphoproteome (Normal)	Age	Gender	Mucinous	Subsite	PT	PN	Stage	CEA	Vascular_Invasion	Lymphatic_Invasion	Perineural_Invasion	Synchronous_Tumors	Polyps_History	Polyps_Present	Vital.Status	Tumor.Status	POLE_mutation	MSH2_mutation	MSH6_mutation	PMS2_mutation	KRAS_mutation	NRAS_mutation	BRAF_mutation	mutation_rate	Hypermutation_status	MSI_PCR_Result	MSmutectFishercall	CMS	ProS	UMS	StromalScore	ImmuneScore	ESTIMATEScore	TumorPurity
Type	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	CON	BIN	BIN	CAT	ORD	ORD	ORD	CON	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	BIN	CON	BIN	BIN	BIN	CAT	CAT	CAT	CON	CON	CON	CON
01CO001	1	1	1	1	1	1	NA	1	NA	1	729	Male	Mucinous	Sigmoid Colon	T4a	N2b	Stage III	4.9	Yes	Yes	No	No	No	No	Living	Tumor free	0	0	0	0	0	0	0	3.333333333	nonhyper	NA	MSS	CMS3	C	NA	-368.880599	573.3158586	204.4352597	0.805074113
01CO005	1	1	nan nan 1	1	1	1	1	1	nan	Female	Not Mucinous	Sigmoid Colon	T3	N0	Stage II	1	No	No	No	No	Yes	Yes	Deceased	Tumor free	0	0	0	0	0	0	0	5.9	nonhyper	NA	MSS	CMS2	E	CIN	-1102.297876	-427.026762	-1529.324638	0.928479028
01CO006	1	1	1	1	1	1	1	1	1	1	904	Female	Mucinous	Ascending Colon	T4a	N2b	Stage III	NA	Yes	Yes	Yes	Yes	No	No	Living	With tumor	0	0	0	0	0	0	0	3.166666667	nonhyper	NA	MSS	CMS3	C	NA	466.174616	1542.023347	2008.197963	0.621792179    

    """
    )
    # extracted = planner.ask(question1)
    # print("\n\n2================\n", extracted)


    # (3) Ask the final question, filled with key information from previous steps.
    # final_goal = f"""Please populate the output schema {str(Movie)} for all the movies mentioned in the
    #   data sources, {movie_names}, the returned records' key is movie name."""
    # planner.gather_information(final_goal, data_sources)
    # suggestion = planner.analyze_goal_and_make_pz_plan()
    # print("\n\n3================\n", suggestion)

    # result = executor.suggestion_to_action(final_goal, suggestion, data_sources)
    # print("\n\n4================\n", result)


        

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

    planner_with_pz_key_info() 
    # draw_graph()
