/* eslint-disable react-hooks/exhaustive-deps */
import useChat from './hooks/useChat'
import GameControl from './components/GameControl';
import MessageList from './components/MessageList';
import PromptControls from './components/PromptControls';
import SignIn from './components/SignIn';
import { useState, useEffect } from 'react';
import useIdleKeyboard from './hooks/useIdleKeyboard';

function App() {
  const { sendMessage, charactersColorMap, promptHistory, userID, threadId, postSignIn, postRegisterNewUser, sendTrigger } = useChat();
  const [timer, setTimer] = useState(600); // Timer starts at 600 seconds (10 minutes)
  const [username, setUserName] = useState(null);

  const isIdle = useIdleKeyboard(8000, false); // Removed callback from here
  useEffect(() => {
    if (isIdle) {
      console.log('Callback triggered: User is idle.');
      sendTrigger();
    }
  }, [isIdle]); // useEffect will trigger when isIdle changes
  
  useEffect(() => {
    if (timer > 0) {
      const intervalId = setInterval(() => {
        setTimer(prevTimer => prevTimer - 1);
      }, 1000);

      return () => clearInterval(intervalId);
    }
  }, [timer]);



  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="h-screen flex flex-col">
      {username ? (
        <>
          <GameControl promptHistory={promptHistory} timer={formatTime(timer)} username={username} />
          <MessageList promptHistory={promptHistory} />
          <PromptControls sendMessage={sendMessage} charactersColorMap={charactersColorMap} />
        </>
      ) : (
        <SignIn setUserName={setUserName} postSignIn={postSignIn} postRegisterNewUser={postRegisterNewUser} />
      )}
    </div>
  );
}

export default App;
