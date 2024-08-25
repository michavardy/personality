import React from 'react';

const Modal = ({ isVisible, onClose, onSubmit, user, setUser, password, setPassword, email, setEmail }) => {
    if (!isVisible) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div className="bg-white p-8 rounded shadow-lg w-1/3">
                <h2 className="text-xl mb-4">Register New User</h2>
                <form className="flex flex-col space-y-4" onSubmit={onSubmit}>
                    <input 
                        type="text" 
                        value={user} 
                        onChange={(e) => setUser(e.target.value)} 
                        placeholder="Username" 
                        className="p-2 border border-gray-300 rounded"
                    />
                    <input 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        placeholder="Password" 
                        className="p-2 border border-gray-300 rounded"
                    />
                    <input 
                        type="email" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                        placeholder="Email" 
                        className="p-2 border border-gray-300 rounded"
                    />
                    <div className="flex justify-end space-x-4">
                        <button 
                            type="button" 
                            onClick={onClose} 
                            className="p-2 bg-gray-300 rounded hover:bg-gray-400"
                        >
                            Cancel
                        </button>
                        <button 
                            type="submit" 
                            className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                        >
                            Submit
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Modal;
