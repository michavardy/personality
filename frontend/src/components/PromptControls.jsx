/* eslint-disable react/prop-types */
// src/components/PromptControls.jsx
import { useState } from 'react';
import { FaChevronUp } from 'react-icons/fa';
import { MdGroups } from "react-icons/md";
import './PromptControls.css'; // Import your CSS file for loading animation

const PromptControls = ({ sendMessage, charactersColorMap }) => {
  const [selectedAudience, setSelectedAudience] = useState('all');
  const [promptContent, setPromptContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handlePromptChange = (event) => {
    setPromptContent(event.target.value);
  };

  const handlePromptSubmit = async () => {
    setIsLoading(true); // Show loading animation
    await sendMessage({
      speaker: 'user',
      audience: selectedAudience,
      trigger: "response",
      content: promptContent
    });
    setIsLoading(false); // Hide loading animation
    setPromptContent('');
  };

  return (
    <div className="fixed bottom-0 w-full h-1/10 bg-gray-50 border-t border-gray-300 flex flex-col p-4 rounded-md">
      {/* Loading Animation */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-bar"></div>
        </div>
      )}
      {/* Icon Buttons Row */}
      <div className="flex">
        <button
          className={`p-2 ${selectedAudience === 'all' ? 'text-black' : 'text-gray-400'} hover:text-blue-600`}
          onClick={() => setSelectedAudience('all')}
          title="all"
        >
          <MdGroups className="text-4xl" />
        </button>

        {/* Iterate over characters to create buttons, excluding 'user' and 'all' */}
        {Object.keys(charactersColorMap)
          .filter(character => character !== 'user' && character !== 'all') // Exclude 'user' and 'all'
          .map((character, index) => (
            <button
              key={index}
              className={`p-2 mx-2 ${selectedAudience === character ? 'text-white' : 'text-gray-400'} hover:text-gray-200`}
              onClick={() => setSelectedAudience(character)}
              title={character}
              style={{ backgroundColor: charactersColorMap[character] || 'gray' }} // Map background color
            >
              {`${character.split(" ")[0]}`}
            </button>
          ))
        }
      </div>

      {/* Prompt Field and Send Button */}
      <div className="flex items-center p-2">
        <input
          type="text"
          placeholder="Prompt here"
          value={promptContent}
          onChange={handlePromptChange}
          className="flex-grow p-2 border border-gray-300 rounded-md"
          onKeyUp={(event) => {
            if (event.key === "Enter") {
              handlePromptSubmit();
            }
          }}
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
