// src/App.jsx
import { useState } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState("");

  const handleSend = async () => {
    if (prompt.trim()) {
      // Add the user's message to the list
      setMessages([...messages, { sender: 'user', text: prompt }]);

      // Clear the prompt input
      setPrompt("");

      // Send the prompt to the backend (Replace this with your actual API call)
      const response = await fetch('http://your-backend-api-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });
      const data = await response.json();

      // Add the response from ChatGPT to the messages list
      setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: data.response }]);
    }
  };

  return (
    <div className="flex flex-col h-screen p-10">
      <div className="flex-1 p-4 overflow-auto bg-gray-100">
        {messages.map((message, index) => (
          <div key={index} className={`p-2 my-2 rounded ${message.sender === 'user' ? 'bg-blue-200 self-end' : 'bg-gray-200 self-start'}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="p-4 bg-white flex">
        <input
          type="text"
          className="flex-1 p-2 border border-gray-300 rounded"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type your message..."
        />
        <button
          className="ml-2 p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          onClick={handleSend}
        >
          ↑
        </button>
      </div>
    </div>
  );
}

export default App;
