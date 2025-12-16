// import React, { useState, useRef, useEffect } from 'react';
// import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
// import './App.css';
// import { API_CONFIG } from './config';
// import * as api from './services/api';
// import { AuthProvider, useAuth } from './features/auth/AuthContext';
// import Login from './features/auth/Login';
// import Register from './features/auth/Register';
// import Sidebar from "./components/Sidebar/Sidebar";
// import ChatHeader from "./components/Header/ChatHeader";
// import ChatWindow from "./components/ChatWindow/ChatWindow";
// import InputBar from "./components/InputBar/InputBar";


// // Protected Route Component
// const ProtectedRoute = ({ children }) => {
//     const { isAuthenticated } = useAuth();
//     const location = useLocation();

//     if (!isAuthenticated) {
//         return <Navigate to="/login" state={{ from: location }} replace />;
//     }

//     return children;
// };

// // Chat Interface Component (The original App logic)
// function ChatInterface() {
//     const [conversations, setConversations] = useState([]);
//     const [currentChatId, setCurrentChatId] = useState(null);
//     const [input, setInput] = useState('');
//     const [isLoading, setIsLoading] = useState(false);
//     const [isLoadingSessions, setIsLoadingSessions] = useState(true);
//     const [isLoadingMessages, setIsLoadingMessages] = useState(false);
//     const [drafts, setDrafts] = useState({});
//     const [documents, setDocuments] = useState([]);
//     const [selectedDocIds, setSelectedDocIds] = useState([]);
//     const [isUploading, setIsUploading] = useState(false);
//     const fileInputRef = useRef(null);
//     const messagesEndRef = useRef(null);
//     const { user, logout } = useAuth(); // Get user info from context

//     // Function to convert markdown-style formatting to HTML
//     const formatMessageContent = (content) => {
//         if (!content) return '';
//         let formatted = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
//         formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
//         formatted = formatted.replace(/\n/g, '<br>');
//         return formatted;
//     };

//     // Load all sessions on component mount
//     // Load all sessions and documents on component mount
//     useEffect(() => {
//         if (user) {
//             loadAllSessions();
//             loadDocuments();
//         }
//     }, [user]);

//     const loadDocuments = async () => {
//         try {
//             const docs = await api.getDocuments();
//             setDocuments(docs);
//         } catch (error) {
//             console.error('Error loading documents:', error);
//         }
//     };

//     const handleFileUpload = async (event) => {
//         const file = event.target.files[0];
//         if (!file) return;

//         setIsUploading(true);
//         try {
//             await api.uploadDocument(file);
//             await loadDocuments(); // Refresh list
//         } catch (error) {
//             console.error('Error uploading document:', error);
//             alert('Failed to upload document');
//         } finally {
//             setIsUploading(false);
//         }
//     };

//     const toggleDocumentSelection = (docId) => {
//         setSelectedDocIds(prev =>
//             prev.includes(docId)
//                 ? prev.filter(id => id !== docId)
//                 : [...prev, docId]
//         );
//     };

//     // Load all sessions in the chat interface
//     const loadAllSessions = async () => {
//         setIsLoadingSessions(true);
//         try {
//             // API call now uses token, userId param is effectively ignored by backend but kept for compatibility if needed
//             const sessions = await api.getSessions(user?.userid || 'current');

//             console.log('Loaded sessions:', sessions);

//             const transformedSessions = sessions.map(session => ({
//                 id: session.sessionid,
//                 title: session.title || `Chat ${session.sessionid.substring(0, 8)}...`,
//                 messages: [],
//                 created_at: session.created_at
//             }));

//             setConversations(transformedSessions);
//         } catch (error) {
//             console.error('Error loading sessions:', error);
//             // alert(`Failed to load sessions: ${error.message}`);
//             // silent fail or specific UI error state better
//         } finally {
//             setIsLoadingSessions(false);
//         }
//     };

//     // Load messages for a specific session
//     const loadSessionMessages = async (sessionId) => {
//         setIsLoadingMessages(true);
//         try {
//             const messages = await api.getSessionMessages(user?.userid || 'current', sessionId);

//             const transformedMessages = messages.flatMap(msg => [
//                 {
//                     id: `${msg.conversationid}-user`,
//                     role: 'user',
//                     content: msg.query,
//                     timestamp: msg.created_at
//                 },
//                 {
//                     id: `${msg.conversationid}-assistant`,
//                     role: 'assistant',
//                     content: msg.response,
//                     timestamp: msg.updated_at
//                 }
//             ]);

//             setConversations(prevConvos =>
//                 prevConvos.map(chat =>
//                     chat.id === sessionId
//                         ? { ...chat, messages: transformedMessages }
//                         : chat
//                 )
//             );
//         } catch (error) {
//             console.error('Error loading messages:', error);
//             alert(`Failed to load messages: ${error.message}`);
//         } finally {
//             setIsLoadingMessages(false);
//         }
//     };

//     const scrollToBottom = () => {
//         messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     };

//     useEffect(() => {
//         scrollToBottom();
//     }, [conversations, currentChatId]);

//     const getCurrentChat = () => {
//         if (currentChatId === null) {
//             return {
//                 id: null,
//                 title: 'New Chat',
//                 messages: []
//             };
//         }
//         return conversations.find(chat => chat.id === currentChatId);
//     };

//     const handleSelectNew = () => {
//         if (currentChatId === null) return;
//         setDrafts(prev => ({ ...prev, [currentChatId]: input }));
//         setCurrentChatId(null);
//         setInput(drafts['new'] || '');
//     };

//     const handleSendMessage = async () => {
//         const query = input.trim();
//         if (!query) {
//             alert('Please enter a message');
//             return;
//         }

//         setIsLoading(true);
//         const currentChat = getCurrentChat();
//         const isNewChat = currentChat.messages.length === 0;
//         const originalInput = input;

//         const userMessage = {
//             id: `user-${Date.now()}`,
//             role: 'user',
//             content: query,
//             timestamp: new Date().toISOString()
//         };

//         const tempId = isNewChat ? `temp-${Date.now()}` : currentChatId;

//         const updatedChat = {
//             ...currentChat,
//             id: tempId,
//             messages: [...currentChat.messages, userMessage],
//             title: isNewChat ? (query.substring(0, 30) + (query.length > 30 ? '...' : '')) : currentChat.title
//         };

//         setConversations(prev => {
//             if (isNewChat) {
//                 return [updatedChat, ...prev];
//             } else {
//                 return prev.map(chat => chat.id === currentChatId ? updatedChat : chat);
//             }
//         });

//         if (isNewChat) {
//             setCurrentChatId(tempId);
//         }
//         setInput('');

//         try {
//             let responseData;
//             if (isNewChat) {
//                 responseData = await api.startSession(user?.userid || 'current', query, selectedDocIds);
//             } else {
//                 responseData = await api.sendMessage(currentChatId, user?.userid || 'current', query);
//             }

//             const assistantMessage = {
//                 id: `assistant-${Date.now()}`,
//                 role: 'assistant',
//                 content: isNewChat ? responseData.conversations[0].response : responseData.response,
//                 timestamp: new Date().toISOString()
//             };

//             const finalChat = {
//                 ...(isNewChat ? { ...updatedChat, id: responseData.sessionid } : updatedChat),
//                 messages: [...updatedChat.messages, assistantMessage]
//             };

//             setConversations(prev =>
//                 isNewChat
//                     ? [finalChat, ...prev.filter(chat => chat.id !== tempId)]
//                     : prev.map(chat => chat.id === currentChatId ? finalChat : chat)
//             );

//             if (isNewChat) {
//                 setCurrentChatId(responseData.sessionid);
//             }

//             setDrafts(prev => {
//                 const newDrafts = { ...prev };
//                 delete newDrafts[isNewChat ? 'new' : currentChatId];
//                 return newDrafts;
//             });
//         } catch (error) {
//             console.error('Error sending message:', error);
//             alert(`Failed to send message: ${error.message}`); // Could be 401 if token expired
//             setInput(originalInput);
//         } finally {
//             setIsLoading(false);
//         }
//     };

//     const handleSwitchChat = async (chatId) => {
//         const prevId = currentChatId || 'new';
//         setDrafts(prev => ({ ...prev, [prevId]: input }));

//         setCurrentChatId(chatId);
//         setInput(drafts[chatId] || '');

//         const chat = conversations.find(c => c.id === chatId);
//         if (chat && chat.messages.length === 0) {
//             await loadSessionMessages(chatId);
//         }
//     };

//     const handleKeyPress = (e) => {
//         if (e.key === 'Enter' && !e.shiftKey) {
//             e.preventDefault();
//             handleSendMessage();
//         }
//     };

//     const currentChat = getCurrentChat();

//     return (
//         <div className="app-container">

//             <Sidebar
//                 conversations={conversations}
//                 currentChatId={currentChatId}
//                 handleSelectNew={handleSelectNew}
//                 handleSwitchChat={handleSwitchChat}
//                 isLoadingSessions={isLoadingSessions}
//                 logout={logout}
//                 documents={documents}
//                 handleFileUpload={handleFileUpload}
//                 fileInputRef={fileInputRef}
//                 isUploading={isUploading}
//             />

//             <main className="main-content">

//                 <ChatHeader user={user} />

//                 <ChatWindow
//                     isLoading={isLoading}
//                     isLoadingMessages={isLoadingMessages}
//                     currentChat={currentChat}
//                     documents={documents}
//                     selectedDocIds={selectedDocIds}
//                     toggleDocumentSelection={toggleDocumentSelection}
//                     messagesEndRef={messagesEndRef}
//                     formatMessageContent={formatMessageContent}
//                 />

//                 <InputBar
//                     input={input}
//                     setInput={setInput}
//                     handleSendMessage={handleSendMessage}
//                     handleKeyPress={handleKeyPress}
//                     isLoading={isLoading}
//                 />
//             </main>
//         </div>
//     );
// }

// function App() {
//     return (
//         <BrowserRouter>
//             <AuthProvider>
//                 <Routes>
//                     <Route path="/login" element={<Login />} />
//                     <Route path="/register" element={<Register />} />
//                     <Route
//                         path="/"
//                         element={
//                             <ProtectedRoute>
//                                 <ChatInterface />
//                             </ProtectedRoute>
//                         }
//                     />
//                 </Routes>
//             </AuthProvider>
//         </BrowserRouter>
//     );
// }

// export default App;