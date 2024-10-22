from agents_lib import AgentABC


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