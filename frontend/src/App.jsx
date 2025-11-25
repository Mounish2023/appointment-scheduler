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
  const [drafts, setDrafts] = useState({}); // New: Store unsent input drafts per chat (including 'new' for new mode)
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

  // Load all sessions in the chat interface
  const loadAllSessions = async () => {
    setIsLoadingSessions(true);
    try {
      const response = await fetch(API_ENDPOINTS.GET_ALL_SESSIONS(API_CONFIG.USER_ID));

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const sessions = await response.json();
      console.log('Loaded sessions:', sessions);

      // Transform sessions into the format we need
      const transformedSessions = sessions.map(session => ({
        id: session.sessionid,
        title: session.title || `Chat ${session.sessionid.substring(0, 8)}...`,
        messages: [], // Messages will be loaded when user clicks on the session
        created_at: session.created_at
      }));

      console.log('Transformed sessions:', transformedSessions);
      setConversations(transformedSessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
      alert(`Failed to load sessions: ${error.message}`);
    } finally {
      setIsLoadingSessions(false);
    }
  };

  // Load messages for a specific session
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

  // Scroll to the bottom of the chat window
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversations, currentChatId]);

  // Get the current chat (handle null as new chat mode)
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

  // Handle selecting "new chat" mode (renamed from handleNewChat)
  const handleSelectNew = () => {
    if (currentChatId === null) {
      return; // Already in new mode; do nothing to "remain same"
    }

    // Save draft of current chat
    setDrafts(prev => ({ ...prev, [currentChatId]: input }));

    // Switch to new mode
    setCurrentChatId(null);
    setInput(drafts['new'] || '');
  };

  // Handle sending a message
  const handleSendMessage = async () => {
    const query = input.trim();
    if (!query) {
      alert('Please enter a message');
      return;
    }

    setIsLoading(true);
    const currentChat = getCurrentChat();
    const isNewChat = currentChat.messages.length === 0; // Simplified: new if no messages (covers null ID)
    const originalInput = input;

    // Add user message to the chat
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toISOString()
    };

    // Create a temporary ID for new chats
    const tempId = isNewChat ? `temp-${Date.now()}` : currentChatId;

    // Update the chat with the user's message (local only for now)
    const updatedChat = {
      ...currentChat,
      id: tempId,
      messages: [...currentChat.messages, userMessage],
      title: isNewChat ? (query.substring(0, 30) + (query.length > 30 ? '...' : '')) : currentChat.title
    };

    // Update conversations immediately (for optimism)
    setConversations(prev => {
      if (isNewChat) {
        // For new chats, add to the beginning of the list
        return [updatedChat, ...prev];
      } else {
        // For existing chats, update in place
        return prev.map(chat => chat.id === currentChatId ? updatedChat : chat);
      }
    });

    // If this is a new chat, update the current chat ID
    if (isNewChat) {
      setCurrentChatId(tempId);
    }
    setInput('');

    try {
      // Call the appropriate API endpoint based on whether it's a new chat or not
      const response = await fetch(
        isNewChat
          ? API_ENDPOINTS.START_SESSION(API_CONFIG.USER_ID)
          : API_ENDPOINTS.SEND_MESSAGE(API_CONFIG.USER_ID, currentChatId),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query,
            ...(isNewChat ? {} : { sessionid: currentChatId })
          })
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();

      // Add assistant's response to the chat
      const assistantMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: isNewChat ? responseData.conversations[0].response : responseData.response,
        timestamp: new Date().toISOString()
      };

      // Update the chat with the assistant's response
      const finalChat = {
        ...(isNewChat ? { ...updatedChat, id: responseData.sessionid } : updatedChat),
        messages: [...updatedChat.messages, assistantMessage]
      };

      // Update conversations with the final chat state
      setConversations(prev =>
        isNewChat
          ? [finalChat, ...prev.filter(chat => chat.id !== tempId)]
          : prev.map(chat => chat.id === currentChatId ? finalChat : chat)
      );

      // Update currentChatId if this was a new chat
      if (isNewChat) {
        setCurrentChatId(responseData.sessionid);
      }

      // Clear draft after successful send
      setDrafts(prev => {
        const newDrafts = { ...prev };
        delete newDrafts[isNewChat ? 'new' : currentChatId];
        return newDrafts;
      });
    } catch (error) {
      console.error('Error sending message:', error);
      alert(`Failed to send message: ${error.message}`);
      setInput(originalInput); // Restore input on error
    } finally {
      setIsLoading(false);
    }
  };

  // Handle switching to an existing chat
  const handleSwitchChat = async (chatId) => {
    // Save draft of previous (handle 'new' if current is null)
    const prevId = currentChatId || 'new';
    setDrafts(prev => ({ ...prev, [prevId]: input }));

    setCurrentChatId(chatId);
    setInput(drafts[chatId] || '');

    // Load messages for this session if not already loaded
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
        <button
          className="new-chat-btn"
          onClick={handleSelectNew}
          disabled={isLoading}
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
          <h1>Appointment Scheduler</h1>
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
            {currentChatId ? 'Send' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;