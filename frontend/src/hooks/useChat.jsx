/* eslint-disable react-hooks/exhaustive-deps */
// src/hooks/useChat.jsx
import { useState, useEffect } from 'react';

const useChat = () => {

  const [charactersColorMap, setCharactersColorMap] = useState({});
  const [promptHistory, setPromptHistory] = useState([])
  const [ userID, setUserId] = useState(null)
  const [threadId, setThreadId] = useState(null)
  const baseUrl =`http://${window.location.hostname}:80`


  const postSignIn = async ({ username, password }) => {
    const response = await fetch(`${baseUrl}/sign_in`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json" // Set the content type to JSON
      },
      body: JSON.stringify({ // Convert the object to JSON string
        username: username,
        password: password
      })
    });
    if (response.ok) {
      // Extract the headers
      const threadIdHeader = response.headers.get("thread_id");
      const userIdHeader = response.headers.get("user_id");
  
      // Save the values in state variables
      setUserId(userIdHeader);
      setThreadId(threadIdHeader);
    } else {
      // Handle errors
      console.error("Sign-in failed:", response.statusText);
    }
    const data = await response.json(); // Parse the JSON response
    return data;
  };
  
  const postRegisterNewUser = async ({ username, password, email }) => {
    const response = await fetch(`${baseUrl}/register_new_user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json" // Set the content type to JSON
      },
      body: JSON.stringify({ // Convert the object to JSON string
        username: username,
        password: password,
        email:email,
      })
    });
    if (response.ok) {
      // Extract the headers
      const threadIdHeader = response.headers.get("thread_id");
      const userIdHeader = response.headers.get("user_id");
  
      // Save the values in state variables
      setUserId(userIdHeader);
      setThreadId(threadIdHeader);
    } else {
      // Handle errors
      console.error("Sign-in failed:", response.statusText);
    }
    const data = await response.json(); // Parse the JSON response
    return data;
  };


  const fetchCharactersColorMap = async () => {
    if (userID && threadId && Object.keys(charactersColorMap).length === 0) {
      const response = await fetch(`${baseUrl}/characters_color_map`, {
        headers: {
          "user_id": userID,
          "thread_id": threadId,
        },
      });
      const data = await response.json();
      setCharactersColorMap(data.characters_color_map);
    }
  };

  const fetchInitialPrompt = async () => {
    if (userID && threadId) {
      try {
        const response = await fetch(`${baseUrl}/initial_prompt`, {
          headers: {
            "user_id": userID,
            "thread_id": threadId,
          },
        });
        const data = await response.json();

        console.log(data);

        const prompts = data.response;

        if (Array.isArray(prompts)) {
          const initPromptHistory = prompts.map((prompt) => ({
            all_characters_color_map: charactersColorMap,
            speaker: prompt.speaker,
            audience: prompt.audience,
            trigger_type: prompt.trigger_type,
            content: prompt.content,
          }));
          setPromptHistory(initPromptHistory);
        } else {
          console.error("Expected an array but got:", prompts);
        }
      } catch (error) {
        console.error("Failed to fetch initial prompt:", error);
      }
    }
  };

  useEffect(() => {
    if (userID && threadId) {
      fetchCharactersColorMap();
    }
  }, [userID, threadId]);

  useEffect(() => {
    if (userID && threadId && Object.keys(charactersColorMap).length > 0) {
      fetchInitialPrompt();
    }
  }, [userID, threadId, charactersColorMap]);

const sendTrigger = async() => {
  const response = await fetch(`${baseUrl}/trigger_prompt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      "user_id": userID,
      "thread_id": threadId,
    },
    body: JSON.stringify(promptHistory),
  });
  const newPromptHistory =  await response.json();
  setPromptHistory(newPromptHistory.response)
  
}
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
          "user_id": userID,
          "thread_id": threadId,
        },
        body: JSON.stringify(updatedPromptHistory),
      });
      const newPromptHistory =  await response.json();
      setPromptHistory(newPromptHistory.response)
};

  return {
    sendMessage,
    sendTrigger,
    charactersColorMap,
    promptHistory,
    userID, 
    threadId,
    postSignIn,
    postRegisterNewUser
  };
};

export default useChat;
