import React, { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';
import './ChatInterface.css';

function ChatInterface({sessionId}) 
{
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [storedPdfs, setStoredPdfs] = useState(null);
  const [drugName, setDrugName] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);


  useEffect(() => 
  {
    if (sessionId) {
      fetch(`http://localhost:8000/api/session/${sessionId}`)
        .then((res) => res.json())
        .then((data) => 
        {
          console.log(data)
          if (data.messages) {
            setMessages(data.messages);
          }
          if (data.drug_name) 
          {  // Set the drug name from session
            setDrugName(data.drug_name);
            
          }
        })
        .catch((error) => console.error("Error fetching session messages:", error));
    } else {
      // If no sessionId, clear messages
      setMessages([]);
    }
  }, [sessionId]);


  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    // Immediately add the user message and clear the input field
    const userMessage = { role: 'user', content: inputValue };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    try {
      await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userMessage),
      });
      // In a real app, you might also wait for an assistant response
      // and then store that in messages as well.
    } catch (error) {
      console.error("Error sending message:", error);
    }
    await processInput(inputValue);
  };

  // New function in ChatInterface.js to handle query search:
  const handleQuerySearch = async (queryText) => 
  {
    addMessage({ role: 'assistant', content: "Retrieving relevant chunks from ChromaDB..." });
    try {
      const response = await fetch('http://localhost:8000/api/retrieve-chunks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drug_name: drugName, query: queryText })
      });
      if (!response.ok) {
        const errorData = await response.json();
        addMessage({ role: 'assistant', content: errorData.detail });
        return;
      }
      const data = await response.json();
      const reply = `Relevant chunks:<br/><br/>${JSON.stringify(data.relevant_chunks)}<br/><br/>Logs:<br/><br/>${data.logs}`;
      addMessage({ role: 'assistant', content: reply });
    } catch (error) {
      addMessage({ role: 'assistant', content: "Error retrieving relevant chunks." });
    }
  };


  const processInput = async (input) => {
    const lowerInput = input.toLowerCase();

    // Fetch Documents functionality
    if (lowerInput.includes('fetch the relevant document') || lowerInput.includes('fetch documents')) 
    {
      const fetchingMessage = { role: 'assistant', content: "Fetching the relevant documents..." };
      addMessage(fetchingMessage);
      try {
        await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(fetchingMessage),
        });
      } catch (error) {
        console.error("Error sending assistant message:", error);
      }
      try 
      {
        
        
        const response = await fetch('http://localhost:8000/api/fetch-pdfs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: input, session_id: sessionId })
        });


        if (!response.ok) 
        {
          const errorData = await response.json();
          const errorinfetch = { role: 'assistant', content: errorData.detail }
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(errorinfetch),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
          addMessage(errorinfetch);
          return;
        }
        const data = await response.json();
        let reply = `Here are the documents for the drug: **${data.drug_name}**\n\n`;
        data.pdf_list.forEach((pdf, index) => {
          reply += `${index + 1}. ${pdf.pdf_name}\n\n`;
        });


        const fetchedpdf = { role: 'assistant', content: reply }
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(fetchedpdf),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }

        addMessage(fetchedpdf);
        setStoredPdfs(data.pdf_list);
        setDrugName(data.drug_name);

        
      } catch (error) 
      {
        const errorinfetch = { role: 'assistant', content: "Error fetching documents." }
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(errorinfetch),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
        addMessage(errorinfetch);
      }
    }
    // PDF Selection functionality

    else if (lowerInput.includes('choose pdf') || lowerInput.includes('select pdf')) 
    {
      if (!storedPdfs) 
      {
        const nopdf_fetch = { role: 'assistant', content: "No PDFs have been fetched yet. Please fetch documents first." }
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(nopdf_fetch),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }
        addMessage(nopdf_fetch);
        return;
      }
      try 
      {
        // Step 1: Convert PDF to Markdown
        const pdf_to_markdown = { role: 'assistant', content: "Converting PDF to markdown..." }
        addMessage(pdf_to_markdown);
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(pdf_to_markdown),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }



        const responseSelect = await fetch('http://localhost:8000/api/select-pdf', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: input,
            storedPdfs: storedPdfs
          })
        });
        if (!responseSelect.ok) 
        {
          const errorData = await responseSelect.json();
          const errorpdf_to_markdown = { role: 'assistant', content: errorData.detail }

          addMessage(errorpdf_to_markdown);
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(errorpdf_to_markdown),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
          return;
        }



        const dataSelect = await responseSelect.json();
        const markdown = dataSelect.markdown;
        const markdown_to_chunks = { role: 'assistant', content: "PDF converted to markdown. Converting markdown to chunks..." }
        addMessage(markdown_to_chunks);
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(markdown_to_chunks),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }




        // Step 2: Convert Markdown to Chunks
        const responseChunks = await fetch('http://localhost:8000/api/markdown-to-chunks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ markdown: markdown })
        });
        if (!responseChunks.ok) 
        {
          const errorData = await responseChunks.json();
          const error_markdown_to_chunks = { role: 'assistant', content: errorData.detail }
          addMessage(error_markdown_to_chunks);
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(error_markdown_to_chunks),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
          return;
        }



        const dataChunks = await responseChunks.json();
        const header_list = dataChunks.header_list;
        const chunks_to_chromadb = { role: 'assistant', content: "Markdown converted to chunks. Storing chunks to ChromaDB..." }
        addMessage(chunks_to_chromadb);
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(chunks_to_chromadb),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }
        
        // Step 3: Store Chunks to ChromaDB
        const responseStore = await fetch('http://localhost:8000/api/store-chunks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ drug_name: drugName, header_list: header_list })
        });


        if (!responseStore.ok) 
        {
          const errorData = await responseStore.json();
          const error_chunks_to_chromadb = { role: 'assistant', content: errorData.detail }
          addMessage(error_chunks_to_chromadb);
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(error_chunks_to_chromadb),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
          return;
        }


        const dataStore = await responseStore.json();
        const enterquery = { role: 'assistant', content: "Chunks stored to ChromaDB successfully. Enter your query" }
        addMessage(enterquery);
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(enterquery),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }
      
      
      } catch (error) 
      {
        const error_process_select_pdf = { role: 'assistant', content: "Error processing PDF selection." }
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(error_process_select_pdf),
          });
        } catch (error) {
          console.error("Error sending assistant message:", error);
        }
        addMessage(error_process_select_pdf);
      }
    }
    // Default response if input doesn't match any condition

    else if (lowerInput.includes('here is the query')) 
    {
      input = lowerInput.split("here is the query:")[1].trim();
      console.log("Query Input: ", input)
      // For example, if drugName is not empty and user input does not match previous commands:
      const searchrelevantchunks = { role: 'assistant', content: "Searching for relevant chunks..." }
      addMessage(searchrelevantchunks);
      try {
        await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(searchrelevantchunks),
        });
      } catch (error) {
        console.error("Error sending assistant message:", error);
      }



        try 
        {
          const responseSearch = await fetch('http://localhost:8000/api/retrieve-chunks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ drug_name: drugName, query: input })
          });
          if (!responseSearch.ok) 
          {
            const errorData = await responseSearch.json();
            const errmess = { role: 'assistant', content: errorData.detail }
            addMessage(errmess);
            try {
              await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(errmess),
              });
            } catch (error) {
              console.error("Error sending assistant message:", error);
            }
            return;
          }
          const dataSearch = await responseSearch.json();
          // const reply = `Relevant chunks:<br/><br/>${JSON.stringify(dataSearch)}<br/><br/>`;
          const reply = dataSearch.response;
          const relevant_chunks = { role: 'assistant', content: reply }
          addMessage(relevant_chunks);
          try {
            await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(relevant_chunks),
            });
          } catch (error) {
            console.error("Error sending assistant message:", error);
          }
        } catch (error) 
      {
        const error_retrieving_relevant_chunks = { role: 'assistant', content: "Error retrieving relevant chunks." }
        addMessage(error_retrieving_relevant_chunks);
        try {
          await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(error_retrieving_relevant_chunks),
          });
        } catch (error) 
        {
          console.error("Error sending assistant message:", error);
        }
      }
    }
    else 
    {
      const could_not_understand = { role: 'assistant', content: "I'm sorry, I didn't understand that. Could you please clarify?" }
      addMessage(could_not_understand);
      try {
        await fetch(`http://localhost:8000/api/session/${sessionId}/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(could_not_understand),
        });
      } catch (error) {
        console.error("Error sending assistant message:", error);
      }
    }
  };

  const addMessage = (msg) => {
    setMessages((prev) => [...prev, msg]);
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.role}`}>
            <div
              className="message-content"
              dangerouslySetInnerHTML={{
                __html: msg.role === 'assistant'
                  ? marked.parse(msg.content)
                  : msg.content
              }}
            />
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          className="chat-input"
          placeholder="Type your message here..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <button type="submit" className="send-button">Send</button>
      </form>
      {/* <div className="chat-footer">
        © 2024 PwC. All rights reserved.
      </div> */}
    </div>
  );
}

export default ChatInterface;
