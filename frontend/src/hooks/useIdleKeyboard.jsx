import { useState, useEffect } from 'react';

const useIdleKeyboard = (idleTimeLimit = 8000, continuous = false) => {
  const [isIdle, setIsIdle] = useState(false);

  useEffect(() => {
    let idleTimeout;

    const resetIdleTimer = () => {
      console.log('Resetting idle timer...');
      clearTimeout(idleTimeout);
      idleTimeout = setTimeout(() => {
        console.log('User is idle.');
        setIsIdle(true);
        if (!continuous) {
          clearTimeout(idleTimeout);
        } else {
          setIsIdle(false); // Reset isIdle after triggering in continuous mode
        }
      }, idleTimeLimit);
    };

    const handleKeyboardActivity = () => {
      console.log('Keyboard activity detected.');
      if (isIdle) {
        setIsIdle(false); // Reset idle state if activity is detected
      }
      resetIdleTimer(); // Restart the idle timer on activity
    };

    window.addEventListener('keydown', handleKeyboardActivity);

    // Initialize idle timer
    resetIdleTimer();

    return () => {
      clearTimeout(idleTimeout);
      window.removeEventListener('keydown', handleKeyboardActivity);
    };
  }, [idleTimeLimit, continuous, isIdle]);

  return isIdle;
};

export default useIdleKeyboard;
