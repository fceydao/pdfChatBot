import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from langchain_community.llms import HuggingFaceHub
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers import AutoModel
import logging

# Hata mesajlarını detaylı görebilmek için logları DEBUG seviyesine ayarlar
logging.basicConfig(level=logging.DEBUG)

# HuggingFace modellerini yükler
tokenizer = AutoTokenizer.from_pretrained("hkunlp/instructor-base")
model = AutoModel.from_pretrained("hkunlp/instructor-base")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

# Flask uygulamasını başlatır ve .env dosyasından çevresel değişkenleri yükler
app = Flask(__name__)
app.secret_key = os.urandom(24)
load_dotenv()

# Konuşma zincirini, sohbet geçmişini ve yüklenen PDF dosyalarını saklamak için listeler oluşturur
conversation_chain = None
chat_history = []
uploaded_pdfs = []

# PDF dosyalarından metin çıkarmak için fonksiyon
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    logging.debug(f"Extracted text length: {len(text)}")
    return text

# Metni parçalara ayırmak için fonksiyon
def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    logging.debug(f"Number of chunks: {len(chunks)}")
    return chunks

# Metin parçalarını vektörler ve FAISS ile saklamak için fonksiyon
def get_vectorstore(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-base")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

# Konuşma zincirini oluşturmak için fonksiyon
def get_conversation_chain(vectorstore):
    llm = HuggingFaceHub(repo_id="google/flan-t5-base", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    logging.debug("Conversation chain created")
    return conversation_chain

# Ana sayfayı render eden route
@app.route('/')
def index():
    return render_template('index.html', chat_history=chat_history, uploaded_pdfs=uploaded_pdfs)

# Kullanıcının mesajını işleyen ve cevabı döndüren route
@app.route('/send_message', methods=['POST'])
def send_message():
    user_question = request.form['user_question']
    logging.debug(f"User question: {user_question}")
    if conversation_chain:
        response = conversation_chain({'question': user_question})
        logging.debug(f"Bot response: {response}")
        chat_history.append({'sender': 'user', 'message': user_question})
        chat_history.append({'sender': 'bot', 'message': response['answer']})
        return jsonify({'status': 'success', 'chat_history': chat_history})
    return jsonify({'status': 'error', 'message': 'Conversation chain not initialized'})

# PDF dosyalarını yükleyen ve işleyen route
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'pdf_docs' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})
 
    files = request.files.getlist('pdf_docs')
    if not files:
        return jsonify({'status': 'error', 'message': 'No selected file'})

    raw_text = get_pdf_text(files)
    text_chunks = get_text_chunks(raw_text)
    vectorstore = get_vectorstore(text_chunks)

    global conversation_chain
    conversation_chain = get_conversation_chain(vectorstore)

    global uploaded_pdfs
    uploaded_pdfs = [file.filename for file in files]

    flash('Files successfully uploaded and processed', 'success')
    return redirect(url_for('index'))

# Uygulamayı DEBUG modunda başlatır
if __name__ == '__main__':
    app.run(debug=True)
