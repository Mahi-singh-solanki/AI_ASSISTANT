from langchain_ollama import ChatOllama
from typing import TypedDict
from typing_extensions import Annotated
from langchain_core.prompts import ChatPromptTemplate
from embeddings.vector import retriever
import json
from embeddings.memory_vector import sync_memory_embeddings
from rag.globals import output_queue,input_queue
from log.log import get_logger
from rag.tasks import play_music,stop_music,open_vscode,open_yt,play_last_video,open_note,create_file,del_file,get_all_files,web_search,my_data,get_my_all_reminders,cancel_all_reminders,set_schedule,start_gesture,close_gesture,play_music_without_name,resume_music,reminder_create
from datetime import datetime
from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode,tools_condition
# from IPython.display import Image,display
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage


logger=get_logger()

class ChatLLM:
    def __init__(self):
        self.model=None
        self.model_with_tools=None
        self.memory_retriever=None
    def load(self):
        if self.model is None:
            logger.info("Started llm's")
            self.model=ChatOllama(model="mistral:instruct",temperature=0)
            self.model_with_tools=ChatOllama(model="qwen2.5:7b-instruct").bind_tools(tools)
        self.memory_retriever=sync_memory_embeddings()

class AgentState(TypedDict):
    memory:list[str]
    context:list[str]
    history:list[str]
    input:str
    tools:list[str]
    inputtype:str
    mode:str
    messages:Annotated[list,add_messages]

tools=[     play_music,
            stop_music,
            open_vscode,
            open_yt,
            play_last_video,
            open_note,
            create_file,
            del_file,
            get_all_files,
            web_search,
            my_data,
            get_my_all_reminders,
            cancel_all_reminders,
            set_schedule,
            start_gesture,
            close_gesture,
            play_music_without_name,
            resume_music,
            reminder_create
]

obj=ChatLLM()

class BuildGraph:
    def __init__(self):
        self.graph=None
    def load(self):
        if not self.graph:
            logger.info("Started graph")
            graph_builder=StateGraph(AgentState)
            graph_builder.add_node("classifier",self.classifier_llm)
            graph_builder.add_node("Tool selection",ToolNode(tools))
            graph_builder.add_node("Reply Mode",self.reply_llm)
            graph_builder.add_node("Task mode",self.task_llm)
            graph_builder.add_node("fact mode",self.fact_llm)
            graph_builder.add_edge(START,"classifier")
            graph_builder.add_conditional_edges("classifier",self.decision,{
                "reply_mode":"Reply Mode",
                "task_mode":"Task mode",
                "fact_mode":"fact mode"
            })
            graph_builder.add_conditional_edges("Task mode",tools_condition,{"tools":"Tool selection","__end__":END})
            graph_builder.add_edge("Tool selection","Task mode")
            graph_builder.add_edge("Reply Mode",END)
            graph_builder.add_edge("fact mode",END)
            self.graph=graph_builder.compile()

    def decision(self,state:AgentState):
        mode=state["mode"].lower().strip()
        if "fact_mode" in mode:
            print("working in fact mode")
            return "fact_mode"
        elif "task_mode" in mode:
            print("working in task mode")
            return "task_mode"
        else:
            print("working in reply mode")
            return "reply_mode"


    def classifier_llm(self,state:AgentState):
        template="""
        You are a routing agent for an AI desktop assistant.

        Your only responsibility is to classify the user's latest message into exactly ONE category.

        Categories:

        1. reply_mode

        Choose this if the user is:
        - asking a question
        - requesting an explanation
        - chatting casually
        - greeting
        - asking for advice
        - asking for code
        - asking about programming
        - asking about the weather
        - asking about science
        - asking about history
        - asking anything that only requires a conversational response.

        Examples:
        - Hi
        - How are you?
        - What is LangGraph?
        - Explain transformers.
        - Why is the sky blue?
        - Tell me a joke.
        - Help me debug this code.

        2. task_mode

        Choose this if the user wants the assistant to perform an action.

        Examples:
        - Open VS Code.
        - Play music.
        - Search the web for Python.
        - Create a file.
        - Delete notes.txt.
        - Show my reminders.
        - Set today's schedule.
        - Start gesture control.

        3. fact_mode

        Choose this if the user is providing personal information that should be remembered for future conversations.

        Examples:
        - My name is Mahipal.
        - I like horror movies.
        - My favourite color is blue.
        - I study IT.
        - I work at Google.
        - I am allergic to peanuts.
        - I usually wake up at 6 AM.
        - I prefer dark mode.
        - Remember that my birthday is 15 August.
        - My hometown is Pune.

        Rules:
        - Return ONLY one of:
        reply_mode
        task_mode
        fact_mode

        - Never answer the user.
        - Never explain your reasoning.
        - Output only the category.

        User:
        {input}

        """
        prompt=ChatPromptTemplate.from_template(template)
        chain=prompt | obj.model
        result=chain.invoke({"input":state["input"]})
        logger.info(f"Classified as {result.content}")
        return {"mode":result.content}

    def task_llm(self,state:AgentState):
        response=obj.model_with_tools.invoke(state["messages"])
        logger.info(f"Implemented task {response.content}")
        output_queue.put(response.content)
        return {"messages":[response]}
    
    def fact_llm(self,state:AgentState):
        template="""
        You are a memory formatter.

        Convert the user's fact into structured JSON.

        Return ONLY valid JSON in this format:

        {{
            "key": "...",
            "value": "...",
            "fact": "..."
        }}

        Rules:
        - Generate a concise, descriptive key in snake_case.
        - Extract the value accurately.
        - Keep the fact exactly as the user stated it.
        - Return only JSON.

        User Fact:
        {input}

        """
        prompt=ChatPromptTemplate.from_template(template)
        chain=prompt | obj.model
        result=chain.invoke({"input":state["input"]})
        print(result.content)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","r") as f:
            data=json.load(f);
        fact=json.loads(result.content)
        data.append(fact)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","w") as f:
            json.dump(data,f,indent=4)
        logger.info(f"Stored the information-{result.content}")
        output_queue.put("Stored the information")
        return {"messages":[result]}
    def reply_llm(self,state:AgentState):
        template = """
        You are a helpful AI desktop assistant.

        The user's message requires a conversational reply.

        Use the following sources in order:

        1. Memory
        - Memory contains structured facts in the form:
        key = value
        - If the user's question can be answered using Memory, use it.
        - Resolve simple references such as "he", "she", "it", "they", "this", or "that" using the most recent relevant Memory or History.

        2. Context
        - If Memory is insufficient, use Context.
        - Context contains retrieved information or knowledge relevant to the user's question.

        3. History
        - If the answer depends on previous conversation, use History.

        Rules:
        - Prefer Memory over Context.
        - Prefer Context over History.
        - If multiple sources conflict, trust Memory first.
        - Answer naturally in paragraphs.
        - Do not mention where the information came from.
        - If the answer cannot be determined from Memory, Context, or History, reply exactly:
        I don't have enough information.

        Memory:
        {memory}

        Context:
        {context}

        History:
        {history}

        User:
        {input}
        """
        prompt=ChatPromptTemplate.from_template(template)
        chain=prompt | obj.model
        result=chain.invoke({"input":state["input"],"memory":state["memory"],"context":state["context"],"history":state["history"]})
        print(result.content)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
            data=json.load(f);
        if len(data)>50:
            data.pop(0)
        data.append({"query":state["input"],"response":result.content,"data_type":"question"})
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","w") as f:
            json.dump(data,f,indent=4)
        logger.info(f"Answered the query result-{result.content}")
        output_queue.put(result.content)
        return {"messages":[result]}
        

    

graph_obj=BuildGraph()
def processor():
    try:
        obj.load()
        graph_obj.load()
    # png=graph_obj.graph.get_graph().draw_mermaid_png()
    # with open("graph_photo.png","wb") as f:
    #     f.write(png)
        while(True):
            input=input_queue.get()
            with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
                data=json.load(f);
            history=[f"user:{d["query"]}\nAssistant:{d["response"]}" for d in data[-3:]]
            answers=retriever.invoke(input)
            memory_data=obj.memory_retriever.invoke(input)
            memory_data=[doc.page_content for doc in memory_data]
            logger.info(f"Memory data is : {memory_data}")
            context=[doc.page_content for doc in answers]
            graph_obj.graph.invoke({"input":input,"context":context,"memory":memory_data,"history":history,"messages":[HumanMessage (content=input)]})
    except Exception as e:
        logger.exception(e)   
