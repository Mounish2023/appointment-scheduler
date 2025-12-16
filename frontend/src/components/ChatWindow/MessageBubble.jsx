import React from 'react';

export default function MessageBubble({ message, formatMessageContent }) {
    const html =
        typeof formatMessageContent === 'function'
            ? formatMessageContent(message.content)
            : message.content;

    return (
        <div className={`message-container ${message.role}`}>
            <div className={`message ${message.role}`}>
                <div
                    className="message-html-content"
                    dangerouslySetInnerHTML={{ __html: html }}
                />
            </div>
        </div>
    );
}
