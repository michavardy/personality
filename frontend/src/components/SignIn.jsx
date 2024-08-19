/* eslint-disable react/prop-types */

import SignInImage from '../images/SignIn.svg';
import  { useState } from 'react';
const SignIn = ({setUserName}) => {
    
    const [user, setUser] = useState('');
    
    const handleSubmit = () => {
        setUserName(user); // Update the parent component's state
    };
    return (
        <div className="flex items-center justify-center w-2/5 h-2/5 m-auto bg-gray-100 border border-gray-300 rounded-lg shadow-lg">
            <div className="h-full flex-1">
                <img src={SignInImage} alt="Sign In" className="h-full object-contain" />
            </div>
            <div className="h-full w-1/4 p-4"> {/* Adjusted width here */}
                <form className="flex flex-col items-center h-full justify-center" onSubmit={handleSubmit}>
                    <input 
                        type="text" 
                        value={user} // Controlled input
                        onChange={(e) => setUser(e.target.value)} // Update state on change
                        placeholder="Username" 
                        className="w-full p-2 mb-4 border border-gray-300 rounded"
                    />
                    <button 
                        type="submit" 
                        className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Submit
                    </button>
                </form>
            </div>
        </div>
    );
};

export default SignIn;
