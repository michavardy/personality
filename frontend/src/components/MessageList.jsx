/* eslint-disable react/prop-types */
// src/components/MessageList.jsx
import { useEffect, useRef } from 'react';

// eslint-disable-next-line react/prop-types
const MessageList = ({ history }) => {
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [history]);

  return (
    <div className="w-full h-9/10 overflow-auto p-4 bg-gray-100 mb-28">
      {history.length > 0 ? (
        history.map((entry, index) => (
          <div key={index} className="p-2 border-b border-gray-300 text-left">
            <p className="text-gray-400"><strong>Prompt:</strong> {entry.prompt}</p>
            <p><strong>Response:</strong> {entry.response.replace("Output", "")}</p>
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
