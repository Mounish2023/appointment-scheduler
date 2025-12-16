import React from 'react';
import './ChatHeader.css';

export default function ChatHeader({ user }) {
    return (
        <header className="chat-header">
            <div>
                <h1>Assist</h1>
            </div>
            <div className="user-info">{user?.email}</div>
        </header>
    );
}
