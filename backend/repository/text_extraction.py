import fitz,pymupdf
from fastapi import File,UploadFile
import os
import json
import re

def clean_text(text):
    text=text.replace("\r","") #remove 
    text=text.replace("\n","")  #remove line breaks and just create space
    text = re.sub(r"\s+", " ", text)  #collapse multiple spaces 
    text = re.sub(r"[^\S\r\n]+", " ", text)  #normalize the whitespace
    text=text.strip()
    text = re.sub(r"\b[A-F0-9]{20,}\b", "", text) #remove words with 20+text length
    #remove page no.s
    text = re.sub(r"\bPage\s*\d+\b", "", text) 
    text = re.sub(r"\b\d+\s*/\s*\d+\b", "", text) # "3/12" patterns
    text = re.sub(r'[\u200b\u200c\u200d\u2060\uFEFF]', '', text)
    text = re.sub(r'[\u2022\u25CF\u25CB\u25A0\u25AA\u25AB]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return text

def text_extraction_upload(uploadfile):
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","r") as f:
            loaded=json.load(f)
    data=loaded
    file_bytes = uploadfile.file.read()
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text=page.get_text()
        text=clean_text(text)
        for i in range(0,len(text),500):
            chunk={"id":len(data)+1,"source":uploadfile.filename,"text":text[i:i+500]}
            if not any(d["text"] == chunk["text"] for d in data):
                data.append(chunk)
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","w") as f:
        json.dump(data,f,indent=4)
    return {"message":"File uploaded and text extracted"}

def extract_native():
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","r") as f:
            loaded=json.load(f)
    data=loaded
    for root,dirs,files in os.walk(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data"):
        for file in files:
            if file:              
                if(file=="chunks.json"):
                    continue
                doc=pymupdf.open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\{file}")
                for page in doc:
                    text=page.get_text()
                    text=clean_text(text)
                    for i in range(0,len(text),500):
                        chunk={"id":len(data)+1,"source":file,"text":text[i:i+500]}
                        if not any(d["text"] == chunk["text"] for d in data):
                            data.append(chunk)
            else:
                print("No file found\n")
    with open(rf"C:\Users\Mahipal\ML_PROJECTS\ML\AI_ASSISTANT\data\chunks.json","w") as f:
        json.dump(data,f,indent=4)
    return {"message":"saved chunks from data folder"}
