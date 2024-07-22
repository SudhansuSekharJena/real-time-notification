import React, { useEffect, useState } from "react";
import axios from "axios";

const NotificationComponent = () => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // Singleton WebSocket instance
  let ws;

  // Fetch notifications from the server when the component mounts
  useEffect(() => {
    setIsLoading(true);
    axios
      .get("/api/notification/")
      .then((response) => {
        setNotifications(response.data.data || []);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error("There was an error fetching the notifications!", error);
        setError("Failed to fetch notifications. Please try again later.");
        setIsLoading(false);
      });
  }, []);

  // Fetch announcements alerts from the server when the component mounts
  useEffect(() => {
    setIsLoading(true);
    axios
      .get("/api/announcements/")
      .then((response) => {
        setNotifications((prevNotifications) => [
          ...prevNotifications,
          ...(response.data.data || []),
        ]);
        setIsLoading(false);
      })
      .catch((error) => {
        console.error(
          "There was an error fetching the announcements alerts!",
          error
        );
        setError("Failed to fetch announcements alerts. Please try again later.");
        setIsLoading(false);
      });
  }, []);

  useEffect(()=>{
    axios
      .get("/api/maintenance_alert/")
      .then((response)=>{
        setNotifications((prevNotifications)=>[
          ...prevNotifications,
          ...(response.data.data || []),
        ]);
        setIsLoading(false)
      })
      .catch((error)=>{
        console.error("There was an error fetching the maintenance alerts!", error);
        setError("Failed to fetch maintenance alerts. Please try again later.");
        setIsLoading(false);
      })
  }, [])

  // Establish WebSocket connection when the component mounts
  useEffect(() => {
    const connectWebSocket = () => {
      if (!ws || ws.readyState === WebSocket.CLOSED) {
        ws = new WebSocket("ws://localhost:8000/ws/notification");

        ws.onopen = () => {
          console.log("WebSocket Connected");
          setIsConnected(true);
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);

          const existingNotification = notifications.find(
            (notification) =>
              notification.message === data.message &&
              notification.notification_type === data.notification_type
          );

          if (!existingNotification) {
            setNotifications((prevNotifications) => [
              data,
              ...prevNotifications,
            ]);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket Error:", error);
        };

        ws.onclose = (e) => {
          console.log("WebSocket Disconnected:", e.reason);
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

  // Helper function to render a notification based on its type
  const renderNotification = (notification, index) => {
    if (!notification) return null;

    // Render different notification types with different styles
    switch (notification.notification_type) {
      case "New Feature added":
        return (
          <li key={index} style={{ color: "green" }}>
            {notification.message}
          </li>
        );
      case "Session Started":
        return (
          <li key={index} style={{ color: "blue" }}>
            {notification.message}
          </li>
        );
      case "Session Ended":
        return (
          <li key={index} style={{ color: "grey" }}>
            {notification.message}
          </li>
        );
      case "Private Message":
        return (
          <li key={index} style={{ color: "purple" }}>
            {notification.message}
          </li>
        );
      case "announcements":
        return (
          <li key={index} style={{ color: "orange" }}>
            {notification.message}
          </li>
        );
      case "Subscription Plan Update":
        return (
          <li key={index} style={{ color: "red" }}>
            {notification.message}
          </li>
        );
      default:
        return <li key={index}>{notification.message}</li>;
    }
  };

  if (isLoading) return <div>Loading notifications...</div>;
  if (error) return <div style={{ color: "red" }}>{error}</div>;

  return (
    <div>
      <h2>Notifications {isConnected ? "(Live)" : "(Disconnected)"}</h2>
      {notifications.length === 0 ? (
        <p>No notifications yet.</p>
      ) : (
        <ul>
          {notifications.map((notification, index) =>
            renderNotification(notification, index)
          )}
        </ul>
      )}
    </div>
  );
};

export default NotificationComponent;
