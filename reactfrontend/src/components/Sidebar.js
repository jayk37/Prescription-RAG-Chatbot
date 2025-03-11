// reactfrontend/src/components/Sidebar.js
import React, { useState, useEffect } from 'react';
import './Sidebar.css';

function Sidebar({ onNewChat, activeSessionId, onSelectSession, refreshKey }) {
  const [sessions, setSessions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSessions();
  }, [refreshKey]); // Re-run fetchSessions when refreshKey changes

  const fetchSessions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/sessions');
      const data = await response.json();
      if (data.sessions) {
        setSessions(data.sessions);
      }
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  };

  const handleSearch = (e) => {
    setSearchTerm(e.target.value);
  };

  const filteredSessions = sessions.filter((session_id) =>
    session_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleNewChat = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/session', {
        method: 'POST',
      });
      const data = await response.json();
      onNewChat(data.session_id);
      fetchSessions();
    } catch (error) {
      console.error('Error creating new chat session:', error);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">PI ASSISTANT</div>

      <div className="search-container">
        <input
          className="search-input"
          type="text"
          placeholder="Search sessions..."
          value={searchTerm}
          onChange={handleSearch}
        />
      </div>

      <div className="sidebar-nav">
        <ul className="session-list">
          {filteredSessions.map((session_id) => (
            <li
              key={session_id}
              className={
                activeSessionId === session_id
                  ? 'session-item active'
                  : 'session-item'
              }
              onClick={() => onSelectSession(session_id)}
            >
              <div className="session-avatar"></div>
              <div className="session-text">{session_id}</div>
            </li>
          ))}
        </ul>
      </div>

      <div className="sidebar-footer">
        <button className="add-chat-button" onClick={handleNewChat}>
          +
        </button>
      </div>
    </div>
  );
}

export default Sidebar;
