import threading
from agent_utils import AgentABC, Model
import hashlib
import asyncio
import time
from datetime import datetime, timezone

from dataclasses import dataclass
import json


@dataclass
class Animal:
    name: str
    breed:str
    food: str
    owner: str
    phone: str

@dataclass
class Plant:
    name: str
    color: str
    height: float

# Finetuning model looks like a better approach when we need an agent for a specific dataset.
#      1. Finetuning LLMs with its data for a DataAgent might make more sense, small models should be good enough.
#      2. Memory for LLMs is important for this case.
class DatabaseAdministrator(AgentABC):
    def __init__(self, proposers, aggregator, admin_name):
        super().__init__(proposers, aggregator)
        self.admin_name = f"{self.__class__.__name__}_{admin_name}"
        self.data_state = {"schema_new": None, "schema_old": None, "message_id": -1}
        self.data_base = []
        self.short_memory = ""
        self.subscribers = set()

        # self.owner = owner

    def register_subscriber(self, subscriber):
        self.subscribers.add(subscriber)
    
    def unregister_subscriber(self, subscriber: AgentABC=None):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    def _notify_subscribers(self, topic, msg):
        for subscriber in self.subscribers:
            subscriber.callback(topic, msg)

    def callback(self, topic, msg):
        if topic == "SCHEMA_CHANGED":
            info  = msg.split(":")
            self.data_state["schema_old"] = self.data_state["schema_new"]
            self.data_state["schema_new"] = info[0]
            self.data_state["message_id"] = info[1]
            print(self.admin_name, ": Schema changed to: ", msg)
        else:
            raise Exception("Unknown topic")

    def _data_schema(self, data):
        prompt = "Please provide the schema for the data you see below: " + str(data) + ".\n\nPlease let me know if it's Animal schema or Plant schema. Don't explain and just return the answer."
        response = self.ask(prompt)
        return response

    def process_data(self, index, other_data, self_identify:bool=False):
        current = index
        try:
            if current < len(other_data):
                self._process_input_data_impl(current, other_data, self_identify)
        except Exception as e:
            print(f"Error: {e}")
        current += 1
        return current
    

    def _process_input_data_impl(self, index, other_data, self_identify):
        schema = ""
        if self_identify:
            schema = self._data_schema(other_data[index])
        else:
            message_id = int(self.data_state["message_id"])
            if index < message_id:
                schema = self.data_state["schema_old"]
            else:
                schema = self.data_state["schema_new"]

        this_data = other_data[index]
        if schema == "Animal":
            print(self.admin_name, "Processing Animal data: ", this_data.name, this_data.owner, this_data.food, this_data.phone)
        elif schema == "Plant":
            print(self.admin_name, "Processing Plant data: ", this_data.name, this_data.color, this_data.height)
        else:
            print(self.admin_name, "Unknown schema: ", schema)


        

    #  prompt = "You're a database administrator. Please notice that new data is coming: " + str(new_data)
    #     if len(self.short_memory) > 0:
    #         prompt += ".\nAnd this is your memory with logs:\n" +  self.short_memory + "\nCombining what you've learned from previous data, "
    #     else:
    #         prompt += ".\nAnd you don't have any data yet."
    #     prompt += """\nDoes the schema changed for the new data record? Please answer in JSON format: changed:\"true or false\", old:\"\", new:\"\", 
        
    #     If there is previous data in current database, use "None" for old, and changed=true.
    #     If the data is Animal, the schema should be: {"name": "", "food": "", "owner": ""},
    #     If the data is Plant, the schema should be: {"name": "", "color": "", "height": }.

    #     When old and new schema are different, then changed=true. 
    #     example 1:
    #         {
    #             "changed": "true",
    #             "old": "None",
    #             "new": ["name", "color", "height"]
    #         }
    #     Please don't explain and just return the answer in JSON format.
    #     """

    # incrementally add new data
    def receive_new_data_and_update_state(self, new_data):
        prompt = "You're a database administrator. Please notice that new data is coming: " + str(new_data) + """
        Please extract the schema for the new data record to JSON format, For example:  {"Plant":["name", "color", "height"]}
        Please just return in JSON format and don't explain. 
"""
        response = self.ask(prompt).strip()
        # print(self.admin_name, "received new data: ", response)
        try:
            res_json = json.loads(response)
        except Exception as e:
            print(f"Error: {e}", response)
            return
        
        schema_name, attributes = list(res_json.items())[0]
        if schema_name != self.data_state["schema_new"]:
            self.data_state["schema_old"] = self.data_state["schema_new"]
            self.data_state["schema_new"] = schema_name
            self.data_state["message_id"] = len(self.data_base)
            
            # notify subscribers that the schema changed.
            msg = schema_name +":"+ str(len(self.data_base))
            self._notify_subscribers("SCHEMA_CHANGED", msg)

        self.data_base.append(new_data)

        # We don't need to update the data memory every time when we have new data, maybe per day.
        # updating memory shouldn't block other operations.
        if str(datetime.now(timezone.utc).timestamp()).endswith("08135.000000"):
            self.short_memory = self.get_data_summary()

#     # async 
#     # def _update_memory(self):
#     #     self.short_memory = self.get_data_summary()

    def get_data_summary(self):
        sampled_data = self.data_base
        prompt = "You're a helpful data analysts. Please summarize the data you see below: " + str(
            sampled_data) + "\n\nHere is your previous memory about this dataset: " + self.short_memory + ". \n\nPlease just summarize and don't make any suggestions."
        response = self.ask(prompt)
        
        return response
    
    def predict_future_data(self):
        prompt = "Please predict the future data based on the current data you have.\n The current data is: " + self.data_base + "\nThis is your shortterm memory: " + self.short_memory
        return self.ask(prompt)
    
    def exam_data(self):
        prompt = "Please exam the data you have, and find the possible corrupted data in the dataset, and provide the exam result and explanation.\n The current data is: " + str(self.data_base)
        return self.ask(prompt)



def feed_new_data_to_data1(data_admin: DatabaseAdministrator=None):
    if data_admin is None:
        raise Exception("Data source is required")

    for i in range(20):
        if i % 20 < 10:
            data_admin.receive_new_data_and_update_state(Animal(name=f"Animal_{i}", breed="husky", food="Grass", owner=f"John_{i}", phone=f"{i}"))
        else:
            data_admin.receive_new_data_and_update_state(Plant(name=f"Plant_{i}", color="Green", height=10.0))

    data_admin.receive_new_data_and_update_state(Animal(name=f"Animal_{21}", breed="huskysdfasf", food="sldfjlasjd;", owner="Joasdfsdfhn", phone="1234"))



def admin2_read_data_from_data1(reader: DatabaseAdministrator=None, data_source: DatabaseAdministrator=None):
    if reader is None:
        reader = DatabaseAdministrator(proposers=[Model.QWEN], aggregator=Model.QWEN)
    if data_source is None:
        raise Exception("Data source is required")
    
    # read data
    current_index = 0
    time.sleep(2)
    while current_index < 20:
        current_index = reader.process_data(current_index, data_source.data_base)
        time.sleep(2)
    
    print(data_source.get_data_summary())
    print(data_source.exam_data())



def test1():
    data_admin1 = DatabaseAdministrator(proposers=[Model.MIXTRAL], aggregator=Model.MIXTRAL, admin_name="Admin1")
    data_admin2 = DatabaseAdministrator(proposers=[Model.QWEN], aggregator=Model.QWEN, admin_name="Admin2")

    # dataAdmin2 wants to get notified by events happened in dataAdmin1.
    data_admin1.register_subscriber(data_admin2)
    thread1 = threading.Thread(target= feed_new_data_to_data1, args=(data_admin1,))
    thread2 =  threading.Thread(target= admin2_read_data_from_data1, args=(data_admin2, data_admin1))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    data_admin1.ask("What is the summary of the data?", data_admin1.get_data_summary())





test1()