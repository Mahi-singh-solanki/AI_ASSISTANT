from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from embeddings.vector import retriever
import json,re
from .voice import get_audio,audio_to_text,text_to_audio,wake_up
from embeddings.memory_vector import memory_retriever

def save_memory(q,a,dt):
    if dt=="fact":
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","r") as f:
            data=json.load(f);
        a=a.lower()
        fact=re.sub(r"^.*stored the information*$\n?", "", a, flags=re.MULTILINE)
        fact="FACT: "+fact.lower()
        data.append({"fact":fact,"data_type":dt})
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\memory.json","w") as f:
            json.dump(data,f,indent=4)
    else:
        with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\rag\history.json","r") as f:
            data=json.load(f);
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
while True:
    wake=wake_up()
    if wake:
        print("\n-------------------")
        get_audio()
        question=audio_to_text()
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
        else:
            data_type="question"
        print(result)
        text_to_audio(result)
        save_memory(question,result,data_type)


