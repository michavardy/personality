// src/App.jsx
import useChat from './hooks/useChat'
import GameControl from './components/GameControl';
import MessageList from './components/MessageList';
import PromptControls from './components/PromptControls';
import SignIn from './components/SignIn';
import { useState, useEffect} from 'react';
import useIdleKeyboard from './hooks/useIdleKeyboard';


function App() {
  const { sendMessage, charactersColorMap, promptHistory} = useChat();
  const [timer, setTimer] = useState(600); // Timer starts at 600 seconds (10 minutes)
  const [username, setUserName] = useState(null)
  const isIdleKeyboard = useIdleKeyboard(8000, true); // 8 seconds idle time, continuous mode enabled

useEffect(() => {
  if (timer > 0) {
    const intervalId = setInterval(() => {
      setTimer(prevTimer => prevTimer - 1);
    }, 1000);

    return () => clearInterval(intervalId);
  }
}, [timer]);


useEffect(() => {
  const handleIdleTrigger = async () => {
    if (isIdleKeyboard) {
    await sendMessage({
      speaker: null,
      audience: null,
      trigger: "trigger",
      content: null
    });
    }
  };

  handleIdleTrigger();
}, [isIdleKeyboard, charactersColorMap, promptHistory, sendMessage]); 


const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
  return (
    <div className="h-screen flex flex-col">
      {username ? (
        <>
          <GameControl promptHistory={promptHistory} timer={formatTime(timer)} username={username}/>
          <MessageList promptHistory={promptHistory} />
          <PromptControls  sendMessage={sendMessage}  charactersColorMap={charactersColorMap} />
        </>
      ) : (
        <SignIn setUserName={setUserName}/>
      )}
    </div>
  );
}

export default App;