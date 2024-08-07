// src/hooks/useChat.jsx
import { useState, useEffect } from 'react';

const useChat = () => {
  const [rules, setRules] = useState({});
  const [scenarios, setScenarios] = useState({});
  const baseUrl =`http://${window.location.hostname}:80`
  
  const fetchRules = async () => {
    const response = await fetch(`${baseUrl}/rules`);
    const data = await response.json();
    setRules(data.rules);
  };
const fetchScenarios = async () => {
  const response = await fetch(`${baseUrl}/scenario`);
  const data = await response.json();
  setScenarios(data.scenario);
};
  
  useEffect(() => {
    fetchRules();
    fetchScenarios()
  }, []);

const sendMessage = async (action, prompt, history) => {
  if (prompt.trim()) {
    const response = await fetch(`${baseUrl}/handle_prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ action, prompt, history}),
    });
    const message_response =  await response.json();
    return message_response

  }
};

  return {
    rules,
    scenarios,
    fetchRules,
    sendMessage,
  };
};

export default useChat;
