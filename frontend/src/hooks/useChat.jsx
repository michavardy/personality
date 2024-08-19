/* eslint-disable react-hooks/exhaustive-deps */
// src/hooks/useChat.jsx
import { useState, useEffect } from 'react';

const useChat = () => {

  const [charactersColorMap, setCharactersColorMap] = useState({});
  const [promptHistory, setPromptHistory] = useState([])
  const baseUrl =`http://${window.location.hostname}:80`

const fetchCharactersColorMap = async () => {
  if (Object.keys(charactersColorMap).length === 0) {
  const response = await fetch(`${baseUrl}/characters_color_map`);
  const data = await response.json();
  setCharactersColorMap(data.characters_color_map);
  }
};

const fetchInitialPrompt = async () => {
  try {
    const response = await fetch(`${baseUrl}/initial_prompt`);
    const data = await response.json();

    // Log the response to verify the structure
    console.log(data);

    // Extract the array from the data object
    const prompts = data.response;

    // Ensure prompts is an array before mapping
    if (Array.isArray(prompts)) {
      const initPromptHistory = prompts.map((prompt) => ({
        all_characters_color_map: charactersColorMap,
        speaker: prompt.speaker,
        audience: prompt.audience,
        trigger_type: prompt.trigger_type,  // Updated to match your data structure
        content: prompt.content,
      }));
      setPromptHistory(initPromptHistory);
    } else {
      console.error("Expected an array but got:", prompts);
    }
  } catch (error) {
    console.error("Failed to fetch initial prompt:", error);
  }
};
  
  useEffect(() => {
    fetchCharactersColorMap(),[]
  });
  useEffect(() => {
    if (Object.keys(charactersColorMap).length > 0) { // Ensure charactersColorMap is not empty
      fetchInitialPrompt();
    }
  }, [charactersColorMap]);


const sendMessage = async ({speaker,audience, trigger, content}) => {
      // Create a new prompt object
      const newPrompt = {
          speaker: speaker,
          audience: audience,
          trigger_type: trigger,
          content: content,
          all_characters_color_map: charactersColorMap
        };
      const updatedPromptHistory = [...promptHistory, newPrompt];

      const response = await fetch(`${baseUrl}/handle_prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedPromptHistory),
      });
      const newPromptHistory =  await response.json();
      setPromptHistory(newPromptHistory.response)
};

  return {
    sendMessage,
    charactersColorMap,
    promptHistory
  };
};

export default useChat;
