// src/App.jsx
import useChat from './hooks/useChat'
import GameControl from './components/GameControl';
import MessageList from './components/MessageList';
import PromptControls from './components/PromptControls';
import { useState, useEffect} from 'react';


function App() {
  const { rules, scenarios, sendMessage } = useChat();
  const [scenariosList, setScenariosList] = useState([])
  const [currentScenario, setCurrentScenario] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [history, setHistory] = useState('')
  const [timer, setTimer] = useState(600); // Timer starts at 600 seconds (10 minutes)

useEffect(()=>{
  setScenariosList(Object.keys(scenarios))
},[scenarios])

useEffect(()=>{
  setCurrentScenario(scenariosList[0])
},[scenariosList])

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
    <div className="App">
      <GameControl rules={rules} currentScenario={currentScenario} scenarios={scenarios} history={history} timer={formatTime(timer)}/>
      <MessageList prompt={prompt} history={history}/>
      <PromptControls prompt={prompt} setPrompt={setPrompt} sendMessage={sendMessage} history={history} setHistory={setHistory}/>
    </div>
  );
}

export default App;