import React, { useState, useRef, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import './App.css';
import { API_CONFIG } from './config';
import * as api from './services/api';
import { AuthProvider, useAuth } from './features/auth/AuthContext';
import Login from './features/auth/Login';
import Register from './features/auth/Register';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// Chat Interface Component (The original App logic)
function ChatInterface() {
  const [conversations, setConversations] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [drafts, setDrafts] = useState({});
  const messagesEndRef = useRef(null);
  const { user, logout } = useAuth(); // Get user info from context

  // Function to convert markdown-style formatting to HTML
  const formatMessageContent = (content) => {
    if (!content) return '';
    let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/\n/g, '<br>');
    return formatted;
  };

  // Load all sessions on component mount
  useEffect(() => {
    if (user) {
      loadAllSessions();
    }
  }, [user]);

  // Load all sessions in the chat interface
  const loadAllSessions = async () => {
    setIsLoadingSessions(true);
    try {
      // API call now uses token, userId param is effectively ignored by backend but kept for compatibility if needed
      const sessions = await api.getSessions(user?.userid || 'current');

      console.log('Loaded sessions:', sessions);

      const transformedSessions = sessions.map(session => ({
        id: session.sessionid,
        title: session.title || `Chat ${session.sessionid.substring(0, 8)}...`,
        messages: [],
        created_at: session.created_at
      }));

      setConversations(transformedSessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
      // alert(`Failed to load sessions: ${error.message}`); 
      // silent fail or specific UI error state better
    } finally {
      setIsLoadingSessions(false);
    }
  };

  // Load messages for a specific session
  const loadSessionMessages = async (sessionId) => {
    setIsLoadingMessages(true);
    try {
      const messages = await api.getSessionMessages(user?.userid || 'current', sessionId);

      const transformedMessages = messages.flatMap(msg => [
        {
          id: `${msg.conversationid}-user`,
          role: 'user',
          content: msg.query,
          timestamp: msg.created_at
        },
        {
          id: `${msg.conversationid}-assistant`,
          role: 'assistant',
          content: msg.response,
          timestamp: msg.updated_at
        }
      ]);

      setConversations(prevConvos =>
        prevConvos.map(chat =>
          chat.id === sessionId
            ? { ...chat, messages: transformedMessages }
            : chat
        )
      );
    } catch (error) {
      console.error('Error loading messages:', error);
      alert(`Failed to load messages: ${error.message}`);
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentChatId]);

  const getCurrentChat = () => {
    if (currentChatId === null) {
      return {
        id: null,
        title: 'New Chat',
        messages: []
      };
    }
    return conversations.find(chat => chat.id === currentChatId);
  };

  const handleSelectNew = () => {
    if (currentChatId === null) return;
    setDrafts(prev => ({ ...prev, [currentChatId]: input }));
    setCurrentChatId(null);
    setInput(drafts['new'] || '');
  };

  const handleSendMessage = async () => {
    const query = input.trim();
    if (!query) {
      alert('Please enter a message');
      return;
    }

    setIsLoading(true);
    const currentChat = getCurrentChat();
    const isNewChat = currentChat.messages.length === 0;
    const originalInput = input;

    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    const tempId = isNewChat ? `temp-${Date.now()}` : currentChatId;

    const updatedChat = {
      ...currentChat,
      id: tempId,
      messages: [...currentChat.messages, userMessage],
      title: isNewChat ? (query.substring(0, 30) + (query.length > 30 ? '...' : '')) : currentChat.title
    };

    setConversations(prev => {
      if (isNewChat) {
        return [updatedChat, ...prev];
      } else {
        return prev.map(chat => chat.id === currentChatId ? updatedChat : chat);
      }
    });

    if (isNewChat) {
      setCurrentChatId(tempId);
    }
    setInput('');

    try {
      let responseData;
      if (isNewChat) {
        responseData = await api.startSession(user?.userid || 'current', query);
      } else {
        responseData = await api.sendMessage(currentChatId, user?.userid || 'current', query);
      }

      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: isNewChat ? responseData.conversations[0].response : responseData.response,
        timestamp: new Date().toISOString()
      };

      const finalChat = {
        ...(isNewChat ? { ...updatedChat, id: responseData.sessionid } : updatedChat),
        messages: [...updatedChat.messages, assistantMessage]
      };

      setConversations(prev =>
        isNewChat
          ? [finalChat, ...prev.filter(chat => chat.id !== tempId)]
          : prev.map(chat => chat.id === currentChatId ? finalChat : chat)
      );

      if (isNewChat) {
        setCurrentChatId(responseData.sessionid);
      }

      setDrafts(prev => {
        const newDrafts = { ...prev };
        delete newDrafts[isNewChat ? 'new' : currentChatId];
        return newDrafts;
      });
    } catch (error) {
      console.error('Error sending message:', error);
      alert(`Failed to send message: ${error.message}`); // Could be 401 if token expired
      setInput(originalInput);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwitchChat = async (chatId) => {
    const prevId = currentChatId || 'new';
    setDrafts(prev => ({ ...prev, [prevId]: input }));

    setCurrentChatId(chatId);
    setInput(drafts[chatId] || '');

    const chat = conversations.find(c => c.id === chatId);
    if (chat && chat.messages.length === 0) {
      await loadSessionMessages(chatId);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const currentChat = getCurrentChat();

  return (
    <div className="app-container">
      <div className="sidebar">
        <div style={{ padding: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            className="new-chat-btn"
            onClick={handleSelectNew}
            disabled={isLoading}
            title={!input.trim() ? "Type a message first" : "Start a new chat"}
            style={{ flex: 1, marginRight: '10px' }}
          >
            + New Chat
          </button>
          <button onClick={logout} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '0.8rem' }}>
            Logout
          </button>
        </div>

        <div className="chat-list">
          {isLoadingSessions ? (
            <div className="loading-sessions">
              <p>Loading sessions...</p>
            </div>
          ) : conversations.length === 0 ? (
            <div className="no-sessions">
              <p>No chats yet. Start a new one!</p>
            </div>
          ) : (
            conversations.map(chat => (
              <div
                key={chat.id}
                className={`chat-item ${chat.id === currentChatId ? 'active' : ''}`}
                onClick={() => handleSwitchChat(chat.id)}
              >
                {chat.title}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="chat-header">
          <h1>Appointment Scheduler</h1>
          <div className="user-info" style={{ fontSize: '0.9rem', color: '#666' }}>
            {user?.email}
          </div>
        </div>

        <div className="chat-window">
          {isLoadingMessages && (
            <div className="loading-container">
              <p>Loading messages...</p>
            </div>
          )}
          {!isLoadingMessages && (!currentChat || currentChat.messages.length === 0) && !isLoading && (
            <div className="empty-state">
              <p>Hello! Start a conversation by typing a message below and clicking "Send".</p>
            </div>
          )}
          {!isLoadingMessages && currentChat && currentChat.messages.map(message => (
            <div
              key={message.id}
              className={`message-container ${message.role}`}
            >
              <div className={`message ${message.role}`}>
                <div
                  className="message-html-content"
                  dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                />
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-container assistant">
              <div className="message assistant loading">
                <div className="message-html-content">Thinking...</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <input
            type="text"
            className="message-input"
            placeholder={currentChatId ? "Type your message here..." : "Type a message and click 'New Chat' or 'Send' to start..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button
            className="send-btn"
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
          >
            {currentChatId ? 'Send' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <ChatInterface />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;