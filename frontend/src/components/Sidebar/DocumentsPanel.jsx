import React from 'react';

export default function DocumentsPanel({
    documents,
    handleFileUpload,
    fileInputRef,
    isUploading,
    handleDownload,
}) {
    return (
        <div className="documents-section">
            <div className="docs-header">
                <h3>Documents</h3>

                <input
                    type="file"
                    ref={fileInputRef}
                    style={{ display: 'none' }}
                    onChange={handleFileUpload}
                />

                <button
                    className="upload-doc-btn"
                    disabled={isUploading}
                    onClick={() => fileInputRef.current && fileInputRef.current.click()}
                >
                    +
                </button>
            </div>

            <div className="documents-list">
                {documents.length === 0 && <div className="no-docs">No documents</div>}

                {documents.map((doc) => (
                    <div
                        key={doc.id}
                        className="document-item"
                        title={doc.filename}
                        onClick={() => handleDownload(doc.id, doc.filename)}
                        style={{ cursor: 'pointer' }}
                    >
                        📄 {doc.filename}
                    </div>
                ))}
            </div>
        </div>
    );
}
