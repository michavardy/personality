/* eslint-disable react/prop-types */
// src/components/MessageList.jsx
import { useEffect, useRef } from 'react';

// eslint-disable-next-line react/prop-types
const MessageList = ({ promptHistory }) => {
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [promptHistory]);

  const getColorForCharacter = (character, colorMap) => {
    return colorMap?.[character] || 'black'; // Default to black if color is not found
  };

  return (
    <div className="w-full h-9/10 overflow-auto p-4 bg-gray-100 mb-28">
      {promptHistory.length > 0 ? (
        promptHistory.map((entry, index) => (
          <div key={index} className="p-2 border-b border-gray-300 text-left">
            <p className="text-gray-400">
              <strong style={{ color: getColorForCharacter(entry.speaker, entry.all_characters_color_map) }}>
                {entry.speaker}
              </strong> 
              {`: ${entry.content}`}
            </p>
          </div>
        ))
      ) : (
        <p>No messages yet.</p>
      )}
      <div ref={endOfMessagesRef} />
    </div>
  );
};

export default MessageList;