import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import * as api from '../services/api';

const DocumentRedirect = () => {
    const { id } = useParams();
    const [searchParams] = useSearchParams();
    const page = searchParams.get('page');
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUrlAndRedirect = async () => {
            try {
                const response = await api.getDownloadUrl(id);
                if (response && response.download_url) {
                    let finalUrl = response.download_url;
                    if (page) {
                        finalUrl += `#page=${page}`;
                    }
                    window.location.href = finalUrl;
                } else {
                    setError('Failed to retrieve document URL.');
                }
            } catch (err) {
                console.error("Error fetching document URL:", err);
                setError('Error fetching document. You may not have permission or the file does not exist.');
            }
        };

        if (id) {
            fetchUrlAndRedirect();
        }
    }, [id, page]);

    if (error) {
        return (
            <div style={{ padding: '20px', textAlign: 'center', color: 'red' }}>
                <h3>Error</h3>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            flexDirection: 'column'
        }}>
            <div className="loader"></div>
            <p style={{ marginTop: '20px' }}>Redirecting to document...</p>
        </div>
    );
};

export default DocumentRedirect;
