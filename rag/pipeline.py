from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from embeddings.vector import retriever
import json,re
from .voice import get_audio,audio_to_text,text_to_audio,wake_up
from embeddings.memory_vector import sync_memory_embeddings
from rag.globals import input_queue,output_queue,wake_event
from log.log import get_logger
from rag.tasks import play_music,stop_music,open_vscode,open_yt,play_last_video,open_note,create_file,del_file,get_all_files,web_search,my_data,get_my_all_reminders,cancel_all_reminders,set_schedule
from datetime import datetime


logger=get_logger()



def save_memory(q,a,dt):
    tasks={ "play music": play_music,
            "stop music": stop_music,
            "open vs code": open_vscode,
            "open youtube":open_yt,
            "play last video":play_last_video,
            "open notepad and write ":open_note,
            "create file":create_file,
            "delete file":del_file,
            "get all files":get_all_files,
            "search":web_search,
            "system info":my_data,
            "get all my reminders":get_my_all_reminders,
            "delete all my reminders":cancel_all_reminders,
            "set schedule":set_schedule
            }

    if dt=="fact":
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
            data=json.load(f);
        if len(data)>50:
            data.pop(0)
        data.append({"query":q,"response":a,"data_type":dt})
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","w") as f:
            json.dump(data,f,indent=4)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","r") as f:
            data=json.load(f);
        a=a.lower()
        fact=re.sub(r"^.*stored the information*$\n?", "", a, flags=re.MULTILINE)
        fact="FACT: "+fact.lower()
        data.append({"fact":fact,"data_type":dt})
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","w") as f:
            json.dump(data,f,indent=4)
    elif dt=="reminder":
        data=json.loads(a)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","r") as f:
            prev=json.load(f)
        prev.append(data)
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\reminders.json","w") as f:
            json.dump(prev,f,indent=4)
    elif dt=="task":
        task=q.lower()
        for key in tasks:
            if key in task.lower():
                try:
                    result = re.sub(re.escape(key), "", task, flags=re.IGNORECASE)
                    feedback=tasks[key](result)
                    output_queue.put(feedback)
                    break
                except Exception as e:
                    logger.exception(e)
        else:
            logger.info("I am not allowed to do that")    
    else:
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
            data=json.load(f);
        if len(data)>50:
            data.pop(0)
        data.append({"query":q,"response":a,"data_type":dt})
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","w") as f:
            json.dump(data,f,indent=4)



model=OllamaLLM(model="mistral:instruct")

template="""
You are a personal AI assistant.
You must answer ONLY using the information below. 
You cannot use outside knowledge or invent information.

---

# MODE SELECTION RULES

**If the user input is a QUESTION (contains “?” or is asking something) Then strictly return answer in paragraph NOT JSON OBJECT:**
If the user's question includes a pronoun like "he", "she", "it", "they", or vague terms like "that" or "this":
- Try to identify who or what it refers to by reviewing the most recent entries in the "History" or "Memory".
- Assume the pronoun refers to the most recently mentioned person, thing, or topic that logically fits.
- Replace the pronoun mentally with the identified name or topic before answering.
- Example:
    History: User said, "My sister is Anjali."
    Question: "What's her name?"
    Response: "Your sister's name is Anjali."
1. FIRST, look into the **Memory** section.
   - Memory contains facts in this format:
       key = value
   - If the question refers to any key (even indirectly), return its value clearly.
     Example:
       Memory:
         favourite_game = Clash of Clans
       Question: What is my favourite game?
       Answer: Your favourite game is Clash of Clans.
2. If nothing matches in Memory, then check the **Context** section for related information.
3. If still not found, check the **History** section for any related past answers.
4.Return answer in paragraphs
5. If nothing relevant is found anywhere, return exactly with:
   I don't have enough information.

---


**If the user input is NOT a question (a fact, statement):**
- Treat it as new information to be stored.
- Extract the key and value pair.
- Return exactly like this:
  "Stored the information" key = value
Do not explain, reword, or guess what it means.

---

**If it start with "remind" then only check this section, extract and return the reminder as a JSON object:
{{
  "text": string,          # what to remind about (clean, no time words)
  "time": string,          # an absolute timestamp using the provided current time
  "repeat": string,        # one of: none, daily, weekly
  "status": "pending"
}}

1. STRICT RULES FOR TIME HANDLING:
   - The user may specify time in forms like:
       "at 2:30 pm"
       "in 15 minutes"
       "after 1 hour"
       "tonight"
       "tomorrow at 9"
       "next monday 5 pm"
   - You MUST convert all of these into a **precise absolute timestamp** using the provided CURRENT TIME.
   - The timestamp MUST ALWAYS be in format:
       YYYY-MM-DD HH:MM:SS
   - NEVER guess a time. If unclear, take the most reasonable interpretation.

2. STRICT RULES FOR REPEATING REMINDERS:
   - If user says things like:
       "every day", "daily", "each morning"
         → repeat = "daily"
       "every week", "weekly", "each monday"
         → repeat = "weekly"
   - Otherwise:
         repeat = "none"

3. STRICT RULE FOR REMINDER TEXT:
   - Remove all time references from the text.
   - Remove "remind me", "to", "at", "in", "after", "on", "tomorrow", "today", "next", weekdays, etc.
   - The text must ONLY contain the actual task.

4. DO NOT modify or adjust the time slightly.
   Use the exact CURRENT TIME provided in the input.
   Apply addition cleanly for "in X minutes/hours".

5. OUTPUT MUST BE VALID JSON. NO extra text.

You will be given:
- user_input: the raw sentence from the user
- current_time: timestamp in format YYYY-MM-DD HH:MM:SS

---



# RULES FOR OUTPUT
- Use only the text given in Context, History, or Memory.
- Never create new facts or assumptions.
- Never use symbols like @, #, $, %, *.
- Return cleanly and directly in one or two sentences.

---

# PROVIDED DATA

## Memory (stored user facts)
{memory}

## Context (document information)
{context}

## History (recent conversation)
{history}

## User Input
{question}

---

# Final Answer:



"""

template2="""
you are summariser who summarise and provide clear concise summary for the given raw paragraphs
summary should be in paragraphs
## summarise task
{raw}
"""
prompt2=ChatPromptTemplate.from_template(template2)
chain2=prompt2 | model
prompt=ChatPromptTemplate.from_template(template)

chain=prompt | model


def processor():
    try:
        memory_retriever=sync_memory_embeddings()
        while True:
            print("\n-------------------")
            question=input_queue.get()
            if question:
                keywords=["open", "run", "start", "play", "search", "stop", "create","get","delete","system info","set"]
                if any(keyword in question[:10].lower() for keyword in keywords):
                    save_memory(question,"","task")
                elif "summarise" in question:
                    result=chain2.invoke({"raw":question})
                    logger.info(f"Answered the query result-{result}")
                    output_queue.put(result)
                    save_memory(question,result,"question")
                else:
                    logger.info("Answering the query...")
                    if "remind" in question.lower():
                        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        question=question+f" current time:{current_time}"
                    print("\n")
                    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
                        data=json.load(f);
                    history="\n".join([f"user:{d["query"]}\nAssistant:{d["response"]}" for d in data[-3:]])
                    answers=retriever.invoke(question)
                    memory_data=memory_retriever.invoke(question)
                    memory_data="\n".join([doc.page_content for doc in memory_data])
                    context="\n".join([doc.page_content for doc in answers])
                    result=chain.invoke({"context":context,"question":question,"history":history,"memory":memory_data})
                    if "stored" in result.lower():
                        data_type="fact"
                        output_queue.put(result)
                    elif "task" in result.lower():
                        data_type="task"
                    elif "remind" in question.lower():
                        data_type="reminder"
                        output_queue.put("ok! sir i will remind you")
                    else:
                        data_type="question"
                        output_queue.put(result)
                    logger.info(f"Answered the query result-{result}")
                    save_memory(question,result,data_type)
                    memory_retriever=sync_memory_embeddings()
                
    except Exception as e:
        logger.exception(e)   


