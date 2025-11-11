from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from embeddings.vector import retriever
import json,re
from .voice import get_audio,audio_to_text,text_to_audio,wake_up
from embeddings.memory_vector import sync_memory_embeddings
from rag.globals import input_queue,output_queue,wake_event
from log.log import get_logger
from rag.tasks import play_music,stop_music,open_vscode,open_yt,play_last_video


logger=get_logger()



def save_memory(q,a,dt):
    tasks={ "play music": play_music,
            "stop music": stop_music,
            "open vs code": open_vscode,
            "open youtube":open_yt,
            "play last video":play_last_video
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
    elif dt=="task":
        task=q.lower()
        for key in tasks:
            if key in task.lower():
                try:
                    result = re.sub(re.escape(key), "", task, flags=re.IGNORECASE)
                    tasks[key](result)
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

**If the user input is a QUESTION (contains “?” or is asking something):**
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
4. If nothing relevant is found anywhere, respond exactly with:
   I don't have enough information.

---

**If the user input start with TASK check if its really a task or not if it is just respond with "Task Detected: " + exact task
example:
    user:open chrome
    assistant:Task Detected: open chrome
Do not explain or add your suggestion just respond with what told to respond
---


**If the user input is NOT a question (a fact, statement, or command):**
- Treat it as new information to be stored.
- Extract the key and value pair.
- Respond exactly like this:
  "Stored the information" key = value
Do not explain, reword, or guess what it means.

---


# RULES FOR OUTPUT
- Use only the text given in Context, History, or Memory.
- Never create new facts or assumptions.
- Never use symbols like @, #, $, %, *.
- Respond cleanly and directly in one or two sentences.

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

prompt=ChatPromptTemplate.from_template(template)

chain=prompt | model


def processor():
    try:
        memory_retriever=sync_memory_embeddings()
        while True:
            print("\n-------------------")
            question=input_queue.get()
            if question:
                keywords=["open", "run", "start", "play", "search", "stop", "create"]
                if any(keyword in question.lower() for keyword in keywords):
                    save_memory(question,"","task")
                else:
                    logger.info("Answering the query...")
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
                    elif "task" in result.lower():
                        data_type="task"
                    else:
                        data_type="question"
                    logger.info(f"Answered the query result-{result}")
                    output_queue.put(result)
                    save_memory(question,result,data_type)
                    memory_retriever=sync_memory_embeddings()
                
    except Exception as e:
        logger.exception(e)   


