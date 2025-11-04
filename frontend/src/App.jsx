import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import { API_CONFIG, API_ENDPOINTS } from './config';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingSessions, setIsLoadingSessions] = useState(true);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const messagesEndRef = useRef(null);

  // Function to convert markdown-style formatting to HTML
  const formatMessageContent = (content) => {
    if (!content) return '';
    
    // Convert **text** to <strong>text</strong>
    let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *text* to <em>text</em>
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert line breaks to <br>
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
  };

  // Load all sessions on component mount
  useEffect(() => {
    loadAllSessions();
  }, []);

  const loadAllSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await fetch(API_ENDPOINTS.GET_ALL_SESSIONS(API_CONFIG.USER_ID));
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const sessions = await response.json();
      
      // Transform sessions into the format we need
      const transformedSessions = sessions.map(session => ({
        id: session.sessionid,
        title: session.title || `Chat ${session.sessionid.substring(0, 8)}...`,
        messages: [], // Messages will be loaded when user clicks on the session
        created_at: session.created_at
      }));

      setConversations(transformedSessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
      // Don't alert on initial load, just log the error
    } finally {
      setIsLoadingSessions(false);
    }
  };

  const loadSessionMessages = async (sessionId) => {
    setIsLoadingMessages(true);
    try {
      const response = await fetch(
        API_ENDPOINTS.GET_SESSION_MESSAGES(API_CONFIG.USER_ID, sessionId)
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const messages = await response.json();
      
      // Transform messages into our format
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

      // Update the conversation with loaded messages
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
    return conversations.find(chat => chat.id === currentChatId);
  };

  const handleNewChat = async () => {
    const query = input.trim();
    if (!query) {
      alert('Please enter a message to start a new chat');
      return;
    }

    setIsLoading(true);
    const originalInput = input;

    try {
      // Call the start session endpoint
      const response = await fetch(API_ENDPOINTS.START_SESSION(API_CONFIG.USER_ID), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const sessionData = await response.json();
      
      // Create new chat with the session data
      const newChat = {
        id: sessionData.sessionid,
        title: sessionData.title || query.substring(0, 30) + (query.length > 30 ? '...' : ''),
        messages: sessionData.conversations.map(conv => [
          {
            id: `${conv.conversationid}-user`,
            role: 'user',
            content: conv.query,
            timestamp: conv.created_at
          },
          {
            id: `${conv.conversationid}-assistant`,
            role: 'assistant',
            content: conv.response,
            timestamp: conv.updated_at
          }
        ]).flat(),
        created_at: sessionData.created_at
      };

      setConversations([...conversations, newChat]);
      setCurrentChatId(newChat.id);
      setInput(''); // Clear input only after success
    } catch (error) {
      console.error('Error starting new session:', error);
      alert(`Failed to start new chat: ${error.message}`);
      setInput(originalInput); // Restore input on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleSwitchChat = async (chatId) => {
    setCurrentChatId(chatId);
    
    // Load messages for this session if not already loaded
    const chat = conversations.find(c => c.id === chatId);
    if (chat && chat.messages.length === 0) {
      await loadSessionMessages(chatId);
    }
  };

  const handleSendMessage = async () => {
    const query = input.trim();
    if (!query) return;

    const originalInput = input;

    // If no chat is selected, create a new one
    if (!currentChatId) {
      await handleNewChat();
      return;
    }
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setConversations(prevConvos => 
      prevConvos.map(chat => 
        chat.id === currentChatId 
          ? { ...chat, messages: [...chat.messages, userMessage] }
          : chat
      )
    );

    setIsLoading(true);

    try {
      // Call the send message endpoint
      const response = await fetch(
        API_ENDPOINTS.SEND_MESSAGE(API_CONFIG.USER_ID, currentChatId),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query
          })
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const conversationData = await response.json();

      // Replace temporary user message and add assistant response
      setConversations(prevConvos => 
        prevConvos.map(chat => {
          if (chat.id === currentChatId) {
            // Remove the temporary message and add the real ones
            const messagesWithoutTemp = chat.messages.filter(
              msg => msg.id !== userMessage.id
            );
            
            return {
              ...chat,
              messages: [
                ...messagesWithoutTemp,
                {
                  id: `${conversationData.conversationid}-user`,
                  role: 'user',
                  content: conversationData.query,
                  timestamp: conversationData.created_at
                },
                {
                  id: `${conversationData.conversationid}-assistant`,
                  role: 'assistant',
                  content: conversationData.response,
                  timestamp: conversationData.updated_at
                }
              ]
            };
          }
          return chat;
        })
      );
      setInput(''); // Clear input only after success
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Remove the temporary message and show error
      setConversations(prevConvos => 
        prevConvos.map(chat => {
          if (chat.id === currentChatId) {
            const messagesWithoutTemp = chat.messages.filter(
              msg => msg.id !== userMessage.id
            );
            
            return {
              ...chat,
              messages: [
                ...messagesWithoutTemp,
                {
                  id: `error-${Date.now()}`,
                  role: 'assistant',
                  content: `Error: Failed to send message. ${error.message}`,
                  timestamp: new Date().toISOString()
                }
              ]
            };
          }
          return chat;
        })
      );
      setInput(originalInput); // Restore input on error
    } finally {
      setIsLoading(false);
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
        <button 
          className="new-chat-btn" 
          onClick={handleNewChat} 
          disabled={isLoading || !input.trim()}
          title={!input.trim() ? "Type a message first" : "Start a new chat"}
        >
          + New Chat
        </button>
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
          <h1>Grok Chat</h1>
        </div>

        <div className="chat-window">
          {isLoadingMessages && (
            <div className="loading-container">
              <p>Loading messages...</p>
            </div>
          )}
          {!isLoadingMessages && (!currentChat || currentChat.messages.length === 0) && !isLoading && (
            <div className="empty-state">
              <p>Start a conversation by typing a message below and clicking "New Chat" or "Send".</p>
            </div>
          )}
          {!isLoadingMessages && currentChat && currentChat.messages.map(message => (
            <div
              key={message.id}
              className={`message-container ${message.role}`}
            >
              <div className={`message ${message.role}`}>
                {message.role === 'assistant' ? (
                  <div 
                    className="message-html-content"
                    dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                  />
                ) : (
                  <div 
                    className="message-html-content"
                    dangerouslySetInnerHTML={{ __html: formatMessageContent(message.content) }}
                  />
                )}
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
            {currentChatId ? 'Send' : 'Start Chat'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;