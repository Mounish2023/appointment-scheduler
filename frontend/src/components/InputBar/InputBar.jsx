import React from 'react';
import './InputBar.css';

export default function InputBar({
    input,
    setInput,
    handleSendMessage,
    handleKeyPress,
    isLoading,
}) {
    return (
        <div className="input-area">
            <input
                type="text"
                className="message-input"
                placeholder="Type your message..."
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
                Send
            </button>
        </div>
    );
}
