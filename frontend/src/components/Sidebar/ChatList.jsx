import React from 'react';

export default function ChatList({
    conversations,
    currentChatId,
    handleSwitchChat,
    isLoadingSessions,
}) {
    return (
        <div className="chat-list">
            {isLoadingSessions ? (
                <div className="loading-sessions">Loading sessions...</div>
            ) : conversations.length === 0 ? (
                <div className="no-sessions">No chats yet. Start a new one!</div>
            ) : (
                conversations.map((chat) => (
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
    );
}
