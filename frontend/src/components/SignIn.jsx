/* eslint-disable react/prop-types */

import SignInImage from '../images/SignIn.svg';
import { useState } from 'react';
import Modal from './SignInModel'
const SignIn = ({ setUserName, postSignIn, postRegisterNewUser}) => {
    const [password, setPassword] = useState('');
    const [user, setUser] = useState('');
    const [email, setEmail] = useState('');
    const [isModalVisible, setIsModalVisible] = useState(false);
    const guestUserName = 'guest'
    const guestPassword = ''

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('handle submit')
        const isSignIn = postSignIn({ username: user, password: password })
        if (isSignIn){
            setUserName(user)
        }
        setIsModalVisible(false); // Close the modal after submitting
    };

    const handleRegisterClick = (e) => {
        e.preventDefault();
        console.log("Register as new user clicked");
        const isSignIn = postRegisterNewUser({username:user, password:password, email:email})
        if (isSignIn){
            setUserName(user)
        }
        setIsModalVisible(false); // Close the modal after submitting
    };

    const handleGuestClick = (e) => {
        e.preventDefault();
        console.log('handle guest click')
        const isSignIn = postSignIn({ username: guestUserName, password: guestPassword })
        if (isSignIn){
            setUserName(guestUserName)
        }
        setIsModalVisible(false); // Close the modal after submitting
    };

    return (
        <div className="flex items-center justify-center w-2/5 h-2/5 m-auto bg-gray-100 border border-gray-300 rounded-custom shadow-lg">
            <div className="h-full flex-1">
                <img src={SignInImage} alt="Sign In" className="h-full object-contain" />
            </div>
            <div className="h-full w-1/4 p-4 flex flex-col justify-center"> {/* Adjusted here */}
                <form className="flex flex-col items-center" onSubmit={handleSubmit}>
                    <input 
                        type="text" 
                        value={user} // Controlled input
                        onChange={(e) => setUser(e.target.value)} // Update state on change
                        placeholder="Username" 
                        className="w-full p-2 mb-4 border border-gray-300 rounded"
                    />
                    <input 
                        type="password" 
                        value={password} // Controlled input
                        onChange={(e) => setPassword(e.target.value)} // Update state on change
                        placeholder="Password" 
                        className="w-full p-2 mb-4 border border-gray-300 rounded"
                    />
                    <button 
                        type="submit" 
                        className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Sign In
                    </button>
                </form>
                <div className="mt-4 text-center">
                    <div 
                        className="text-blue-500 cursor-pointer hover:underline"
                        onClick={() => setIsModalVisible(true)}
                    >
                        Register as new user
                    </div>
                    <div 
                        className="text-blue-500 cursor-pointer hover:underline mt-2"
                        onClick={handleGuestClick}
                    >
                        Visit as guest
                    </div>
                </div>
            </div>
            {/* Render the Modal */}
            <Modal 
                isVisible={isModalVisible} 
                onClose={() => setIsModalVisible(false)} 
                onSubmit={handleRegisterClick}
                user={user} 
                setUser={setUser}
                password={password} 
                setPassword={setPassword}
                email={email} 
                setEmail={setEmail}
            />
        </div>
    );
};

export default SignIn;
