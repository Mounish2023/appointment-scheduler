import React from 'react';

export default function EmptyState({
    documents,
    selectedDocIds,
    toggleDocumentSelection,
}) {
    return (
        <div className="empty-state">
            <p>Hello! Start a conversation by typing a message below.</p>

            {documents.length > 0 && (
                <div className="document-selection">
                    <p>Select documents for context (optional):</p>
                    <div className="doc-bubbles">
                        {documents.map((doc) => (
                            <div
                                key={doc.id}
                                className={`doc-tag ${selectedDocIds.includes(doc.id) ? 'selected' : ''
                                    }`}
                                onClick={() => toggleDocumentSelection(doc.id)}
                            >
                                <span>📄</span>
                                <span className="doc-name">{doc.filename}</span>
                                {selectedDocIds.includes(doc.id) && <span className="checkmark">✓</span>}
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
