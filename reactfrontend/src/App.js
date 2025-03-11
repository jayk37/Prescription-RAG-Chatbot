import React from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { useState, useEffect, useRef } from 'react';

function App() {
  const [sessionId, setSessionId] = useState(null);
  
  
  const handleNewChat = (newSessionId) => {
    setSessionId(newSessionId);
  };


  const handleSelectSession = (selectedSessionId) => {
    setSessionId(selectedSessionId);
  };


  return (
    <div className="app-container">
      <Sidebar
        onNewChat={handleNewChat}
        activeSessionId={sessionId}
        onSelectSession={handleSelectSession}
      />
      <ChatInterface sessionId={sessionId}/>
    </div>
  );
}

export default App;
