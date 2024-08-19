import { useState, useEffect } from 'react';
import { FaLess } from 'react-icons/fa';

const useIdleKeyboard = (idleTimeLimit = 8000, continuous =FaLess) => {
  const [isIdle, setIsIdle] = useState(false);

  useEffect(() => {
    let idleTimeout;

    const resetIdleTimer = () => {
      clearTimeout(idleTimeout);
      idleTimeout = setTimeout(() => {
        setIsIdle(true)
        if (continuous){
          setIsIdle(false);
        }
      }, idleTimeLimit);
    };

    const handleKeyboardActivity = () => {
      if (isIdle) {
        setIsIdle(false);
      }
      resetIdleTimer();
    };

    window.addEventListener('keydown', handleKeyboardActivity);

    // Initialize idle timer
    resetIdleTimer();

    return () => {
      clearTimeout(idleTimeout);
      window.removeEventListener('keydown', handleKeyboardActivity);
    };
  }, [isIdle, idleTimeLimit]);

  return isIdle;
};

export default useIdleKeyboard;
