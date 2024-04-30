import React, { useState } from 'react';
import Canvas from './Canvas';
import RotateLoader from 'react-spinners/RotateLoader';
import { useMicVADWrapper } from './hooks/useMicVADWrapper';
import { particleActions } from './particle-manager';

const App = () => {
    const [loading, setLoading] = useState(true);
    const [listening, setListening] = useState(false);
    const toggleListening = () => setListening(!listening);

    const micVAD = useMicVADWrapper(setLoading, listening);

    return (
        <div className="app-container">
            {loading ? (
                <RotateLoader
                    loading={loading}
                    color={"#27eab6"}
                    aria-label="Loading Spinner"
                    data-testid="loader"
                />
            ) : (
                <>
                    <Canvas draw={particleActions.draw} />
                    <button 
                        className={`listen-button ${listening ? 'listening' : ''}`}
                        onClick={toggleListening}
                    >
                        {listening ? 'Stop Listening' : 'Start Listening'}
                    </button>
                </>
            )}
        </div>
    );
};

export default App;
