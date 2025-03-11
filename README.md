# 💊 Prescription Drug Chatbot (RAG-Based GPT Clone)

🚀 A **Retrieval-Augmented Generation (RAG)** application designed to **intelligently fetch and process prescription drug data** from the **FDA website**. This application combines **state-of-the-art LLM embeddings, vector databases, and an interactive real-time UI** to provide **ChatGPT-like experiences** while ensuring reliable, up-to-date drug information.

---

## 🎥 Demo



https://github.com/user-attachments/assets/50be6ef9-5f33-4864-9adf-b0742fc0a809



---

## **🌟 Features**
📄 **Real-time FDA Drug Retrieval:** Uses `BeautifulSoup` to **scrape official FDA prescription PDFs** dynamically based on user queries.  
📌 **Structured Knowledge Extraction:** Converts PDFs into **Markdown format** using `PyMuPDF`, ensuring **better readability** and efficient processing.  
🔍 **Semantic Search with Vector Embeddings:**  
   - **ChromaDB** stores **chunked** drug information as embeddings.  
   - **OpenAI Llama Instruct Models** generate **query embeddings** for **fuzzy & semantic similarity search**.  
🤖 **LLM-Enhanced Responses:**  
   - Top matched document chunks are **retrieved and injected** into an **LLM prompt** for **high-quality response generation**.  
💬 **Full-Stack Real-Time Chat Interface (ChatGPT-Style):**  
   - **React.js frontend** with **reusable components, hooks, async requests, and UI state management.**  
   - **FastAPI backend** for **efficient data processing and API calls**.  
💾 **Permanent Chat Sessions:**  
   - **MongoDB stores chat history**, enabling **persistent** user conversations.  


---

## **🛠️ Tech Stack**
| Component          | Technology Used |
|--------------------|----------------|
| **Frontend**      | React.js ⚛️, React DOM 🚀, CSS 🎨 |
| **Backend**       | FastAPI ⚡, Pydantic 📜, Async HTTP Requests 🌍 |
| **Database**      | MongoDB 🍃 (Chat Storage), ChromaDB 🧠 (Vector Search) |
| **Embeddings**    | OpenAI Llama Instruct 🦙, BERT, OpenAI APIs |
| **Scraping**      | BeautifulSoup 🕸️ |
| **Parsing**       | PyMuPDF 📄 |

---

## **🔧 How It Works**
1️⃣ **User enters a drug name in the ChatGPT-like interface.**  
2️⃣ **BeautifulSoup scrapes** the **FDA official website** to find the relevant **prescription drug PDF.**  
3️⃣ **PyMuPDF extracts** and **formats** the PDF into **Markdown structure.**  
4️⃣ The **text is chunked** and **stored as vector embeddings in ChromaDB.**  
5️⃣ When a user **asks a question**, it is first **converted to an LLM embedding.**  
6️⃣ A **semantic search** is performed to **find top-matching chunks** in **ChromaDB.**  
7️⃣ The **best results are fed into an LLM (Llama Instruct API)** to **generate a contextual response.**  
8️⃣ The **chat session is saved in MongoDB**, making it **persistent across sessions.**  

---

## **💡 Key Concepts**
This project aligns with **high-performance, scalable software** requirements, including:

🔹 **Information Retrieval:** Efficiently indexes and retrieves FDA drug documents using **vector embeddings & LLM-based search**.  
🔹 **Database & Storage Optimization:** Uses **ChromaDB** for **vector similarity searches** and **MongoDB** for **persisting structured chat history**.  
🔹 **Low-Latency API Design:** Built using **FastAPI** for **high-speed processing** and **async execution**.  
🔹 **Cloud-Ready Architecture:** Supports **distributed scaling** by allowing **embedding storage in cloud databases** (MongoDB Atlas, AWS, etc.).  
🔹 **Scalable Frontend with React.js:** Implements **reusable components, hooks, state management**, and **real-time UI updates**.  
🔹 **Optimized Web Scraping & Parsing:** Uses **BeautifulSoup** and **PyMuPDF** to **extract structured knowledge** from unstructured PDFs.  
🔹 **LLM Orchestration:** Integrates **OpenAI APIs (Llama Instruct Models)** to **generate context-aware, conversational responses**.  

---

## **📌 Future Enhancements Coming Soon!**
🔹 **Multi-document RAG:** Fetch multiple FDA documents for enhanced accuracy.  
🔹 **Fine-tuned Model:** Replace OpenAI API with a **custom fine-tuned LLM** on **prescription datasets**.

---

## **👨‍💻 Contributing**
We welcome contributions! To get started:  
1️⃣ Fork the repo 🍴  
2️⃣ Create a branch 🏗️  
3️⃣ Make changes & push 🚀  
4️⃣ Open a PR 🔥  

---

## **📜 License**
MIT License © 2025
