import React from 'react';
import './ChatWindow.css';
import MessageBubble from './MessageBubble';
import EmptyState from './EmptyState';

export default function ChatWindow({
    isLoading,
    isLoadingMessages,
    currentChat,
    documents,
    selectedDocIds,
    toggleDocumentSelection,
    messagesEndRef,
    formatMessageContent,
}) {
    return (
        <div className="chat-window">
            {isLoadingMessages && (
                <div className="loading-container">Loading messages...</div>
            )}

            {!isLoadingMessages &&
                (!currentChat || currentChat.messages.length === 0) &&
                !isLoading && (
                    <EmptyState
                        documents={documents}
                        selectedDocIds={selectedDocIds}
                        toggleDocumentSelection={toggleDocumentSelection}
                    />
                )}

            {!isLoadingMessages &&
                currentChat &&
                currentChat.messages.map((m) => (
                    <MessageBubble
                        key={m.id}
                        message={m}
                        formatMessageContent={formatMessageContent}
                    />
                ))}

            {isLoading && (
                <MessageBubble
                    message={{ id: 'assistant-loading', role: 'assistant', content: 'Thinking...' }}
                    formatMessageContent={(c) => c}
                />
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
