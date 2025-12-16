import React from 'react';
import ChatList from './ChatList';
import DocumentsPanel from './DocumentsPanel';
import './Sidebar.css';

export default function Sidebar({
    conversations,
    currentChatId,
    handleSelectNew,
    handleSwitchChat,
    isLoadingSessions,
    logout,
    documents,
    handleFileUpload,
    fileInputRef,
    isUploading,
    isLoading,
    handleDownload,
}) {
    return (
        <aside className="sidebar">
            <div className="sidebar-top">
                <button
                    className="new-chat-btn"
                    onClick={handleSelectNew}
                    disabled={isLoading}
                >
                    + New Chat
                </button>
                <button className="logout-btn" onClick={logout}>
                    Logout
                </button>
            </div>

            <DocumentsPanel
                documents={documents}
                handleFileUpload={handleFileUpload}
                fileInputRef={fileInputRef}
                isUploading={isUploading}
                handleDownload={handleDownload}
            />

            <div className="chat-list-container">
                <h3 className="chat-list-title">Your Chats</h3>
                <ChatList
                    conversations={conversations}
                    currentChatId={currentChatId}
                    handleSwitchChat={handleSwitchChat}
                    isLoadingSessions={isLoadingSessions}
                />
            </div>
        </aside>
    );
}
