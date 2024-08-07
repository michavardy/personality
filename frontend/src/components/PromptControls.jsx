/* eslint-disable react/prop-types */
// src/components/PromptControls.jsx
import { useState } from 'react';
import { FaSearch, FaWalking, FaMicrophone, FaChevronUp } from 'react-icons/fa';

const PromptControls = ({ prompt, setPrompt, sendMessage, setHistory, history }) => {
  const [selectedAction, setselectedAction] = useState('describe');


  const handlePromptChange = (event) => {
    setPrompt(event.target.value);
  };
  const handlePromptSubmit = async () => {
    const currentPrompt = prompt; // Store a copy of the current prompt
    const response = await sendMessage(selectedAction, prompt, history)
    setHistory((prevHistory) => [...prevHistory, { prompt: currentPrompt, action: selectedAction, response: response.response }]); // Append new entry to history
    setPrompt('')
  }

  
  return (
    <div className="fixed bottom-0 w-full h-1/10 bg-gray-50 border-t border-gray-300  flex flex-col p-4 rounded-md">
      {/* Icon Buttons Row */}
      <div className="flex ">
        <button
          className={`p-2 ${selectedAction === 'describe' ? 'text-black' : 'text-gray-400'} hover:text-blue-600 `}
          onClick={() => setselectedAction('describe')}
          title="Describe"
        >
          <FaSearch className="text-xl" />
        </button>
        <button
          className={`p-2 ${selectedAction === 'walk' ? 'text-black' : 'text-gray-400'} hover:text-blue-600 `}
          onClick={() => setselectedAction('walk')}
          title="Go"
        >
          <FaWalking className="text-xl" />
        </button>
        <button
          className={`p-2 ${selectedAction === 'microphone' ? 'text-black' : 'text-gray-400'} hover:text-blue-600`}
          onClick={() => setselectedAction('microphone')}
          title="Talk"
        >
          <FaMicrophone className="text-xl" />
        </button>
      </div>

      {/* Prompt Field and Send Button */}
      <div className="flex items-center p-2">
        <input
          type="text"
          placeholder="Prompt here"
          value={prompt}
          onChange={handlePromptChange}
          className="flex-grow p-2 border border-gray-300 rounded-md"
          onKeyUp={(event) => {
            if (event.key === "Enter") {
              handlePromptSubmit}}
          }
        />
        <button
          className="p-2 ml-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
          onClick={handlePromptSubmit}
        >
          <FaChevronUp className="text-xl" />
        </button>
      </div>
    </div>
  );
};

export default PromptControls;
