import transformers
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import faiss 
import numpy as np
import pickle
import os
import streamlit as st
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import google.generativeai as genai

print('before class')
class semanticEmbedding:
    def __init__(self, model_name='sentence-transformers/all-mpnet-base-v2'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    def get_embedding(self, sentences):
    # Tokenize sentences
        encoded_input = self.tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        # Perform pooling
        sentence_embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        sentence_embeddings = F.normalize(sentence_embeddings, p=2, dim=1)
        return sentence_embeddings.detach().numpy()
    

class FaissIdx:

    def __init__(self, model, dim=768):
        self.index = faiss.IndexFlatIP(dim) # need to load the pickle model in the final file
        # self.index = faiss
        # Maintaining the document data
        self.doc_map = dict()
        self.model = model
        self.ctr = 0

    def add_doc(self, document_text):
        self.index.add(self.model.get_embedding(document_text))
        self.doc_map[self.ctr] = document_text # store the original document text
        self.ctr += 1

    def search_doc(self, query, k=3):
        D, I = self.index.search(self.model.get_embedding(query), 5)
        return [{self.doc_map[idx]: score} for idx, score in zip(I[0], D[0]) if idx in self.doc_map]
    def save_index(self, index_filename, doc_map_filename):
        # Save Faiss index to file
        faiss.write_index(self.index, index_filename)

        # Save document map to file using pickle
        with open(doc_map_filename, 'wb') as f:
            pickle.dump(self.doc_map, f)

    def load_index(self, index_filename, doc_map_filename):
        # Load Faiss index from file
        self.index = faiss.read_index(index_filename)

        # Load document map from file using pickle
        with open(doc_map_filename, 'rb') as f:
            self.doc_map = pickle.load(f)

# creating an instance of the class
model = semanticEmbedding()

index = FaissIdx(model)
# /mount/src/nlp-project/MLmodel/main.py
index.load_index('MLmodel/index.bin', 'MLmodel/doc_map.pkl')
# MLmodel\index.bin
print('loaded index')
model = genai.GenerativeModel('gemini-pro')

# genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
genai.configure(api_key="AIzaSyAwQWWxSuY_6YlBF-UaGNnnIt3AyGFvA6o")

# query = "Iam kishan from uttarpradesh, and I want subsidy"

user_name = 'Kishan'

website = 'https://www.india.gov.in/my-government/schemes'
# print('before rag')
# query_result = index.search_doc(query)
# print('after rag')
# context = ""
# for i in range(5):
#     for key, value in query_result[i].items():
#         if(value>0.23):
#             context += key + " "
# content = ""
# print('before llm')
# if context == '':
#     print('Is there anything else I can help you with?')
# else:
#     formatted_response = f''' Give response in this format, dont change the format or the links given-: 
# Hello {user_name},

# Thank you for reaching out! 🌟 Based on the information you provided, here are some government schemes that might be relevant to your situation:

# 1. Scheme Name 1:
#    - Information like eligibility, benefit.

# 2. Scheme Name 2:
#    - Information like eligibility, benefit.

# 3. Scheme Name 3:
#    - Information like eligibility, benefit.

# 4. Scheme Name 4:
#    - Information like eligibility, benefit.

# 5. Scheme Name 5:
#    - Information like eligibility, benefit.


# For more detailed information or to apply, you can visit the official [Government Department/Agency] website: {website}.


# If you have any more questions or need further assistance, feel free to ask!

# Best regards,
# GovSevak.

# *This message is generated by GENAI, GENAI can make mistakes. Consider checking important information.*

# QUERY:${query}$ CONTEXT:${context}$'''

#     response = model.generate_content(formatted_response)
#     print(response.text)

if 'messages' not in st.session_state:
    st.session_state.messages=[
        {
            "role":"assistant",
            "content":"Ask me anything"
        }
    ]
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
def llm_function(query):
    query_result = index.search_doc(query)
    context = ""
    for i in range(5):
        for key, value in query_result[i].items():
            if(value>0.23):
                context += key + " "
    if context == '':
        print('Is there anything else I can help you with?')
        return 
    else:
        formatted_response = f''' Give response in this format, dont change the format or the links given-: 
        Hello {user_name},

        Thank you for reaching out! 🌟 Based on the information you provided, here are some government schemes that might be relevant to your situation:

        1. Scheme Name 1:
        - Information like eligibility, benefit.

        2. Scheme Name 2:
        - Information like eligibility, benefit.

        3. Scheme Name 3:
        - Information like eligibility, benefit.

        4. Scheme Name 4:
        - Information like eligibility, benefit.

        5. Scheme Name 5:
        - Information like eligibility, benefit.


        For more detailed information or to apply, you can visit the official [Government Department/Agency] website: {website}.


        If you have any more questions or need further assistance, feel free to ask!

        Best regards,
        GovSevak.

        *This message is generated by GENAI, GENAI can make mistakes. Consider checking important information.*

        QUERY:${query}$ CONTEXT:${context}$'''

        response = model.generate_content(formatted_response)
        print(response.text)
        with st.chat_message('user'):
            st.markdown(query)
        with st.chat_message('assistant'):
            st.markdown(response.text)
        st.session_state.messages.append(
            {
                'role':'user',
                'content':query
            }
        )
        st.session_state.messages.append(
            {
                'role':'assitant',
                'content':response.text
            }
        )
query = st.chat_input("hey hey what's up big boi")
if query:
    llm_function(query)
    