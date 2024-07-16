import React, { useEffect, useState } from 'react';
import axios from 'axios';

const MaintenanceComponent = () => {
    const [maintenanceAlerts, setMaintenanceAlerts] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isConnected, setIsConnected] = useState(false);

    // Singleton WebSocket instance
    let ws;

    // Fetch maintenance alerts from the server when the component mounts
    useEffect(() => {
        setIsLoading(true);
        axios.get('/api/maintenance-alert/')
            .then(response => {
                setMaintenanceAlerts(response.data.data || []);
                setIsLoading(false);
            })
            .catch(error => {
                console.error('There was an error fetching the maintenance alerts!', error);
                setError('Failed to fetch maintenance alerts. Please try again later.');
                setIsLoading(false);
            });
    }, []);

    // Establish WebSocket connection when the component mounts
    useEffect(() => {
        const connectWebSocket = () => {
            if (!ws || ws.readyState === WebSocket.CLOSED) {
                ws = new WebSocket('ws://localhost:8000/ws/notification/');

                ws.onopen = () => {
                    console.log('WebSocket Connected');
                    setIsConnected(true);
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);

                    if (data.message && data.notification_type === 'Maintenance Alert') {
                        setMaintenanceAlerts((prevAlerts) => [data, ...prevAlerts]);
                    }
                };

                ws.onerror = (error) => {
                    console.error('WebSocket Error:', error);
                };

                ws.onclose = (e) => {
                    console.log('WebSocket Disconnected:', e.reason);
                    setIsConnected(false);
                    setTimeout(connectWebSocket, 3000); // Attempt to reconnect after 3 seconds
                };
            }
        };

        connectWebSocket();

        // Cleanup function to close the WebSocket connection on unmount
        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, []); // Empty dependency array means this effect runs once on mount



    if (isLoading) return <div>Loading maintenance alerts...</div>;
    if (error) return <div style={{ color: 'red' }}>{error}</div>;

    return (
        <div>
            <h2>Maintenance Alerts {isConnected ? '(Live)' : '(Disconnected)'}</h2>
            {maintenanceAlerts.length === 0 ? (
                <p>No maintenance alerts yet.</p>
            ) : (
                <ul>
                    {maintenanceAlerts.map((alert, index) => (
                        <li key={index} style={{ color: 'orange' }}>{alert.message}</li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default MaintenanceComponent;
