import { useEffect, useRef } from 'react';
import { useMicVAD } from '@ricky0123/vad-react';
import { onMisfire, onSpeechEnd, onSpeechStart } from '../speech-manager';

export const useMicVADWrapper = (onLoadingChange, listening) => {
    const micVAD = useMicVAD({
        startOnLoad: false,
        onSpeechStart,
        onSpeechEnd,
        onVADMisfire: onMisfire, // Ensure this is the correct name as per your imports
        positiveSpeechThreshold: 0.90,
        negativeSpeechThreshold: 0.75,
        minSpeechFrames: 4,
        preSpeechPadFrames: 5,
    });

    const loadingRef = useRef(micVAD.loading);

    useEffect(() => {
        if (loadingRef.current !== micVAD.loading) {
            onLoadingChange(micVAD.loading);
            loadingRef.current = micVAD.loading;
        }
    }, [micVAD.loading, onLoadingChange]);

    useEffect(() => {
        if (listening) {
            micVAD.start();
        } else {
            micVAD.pause();
        }
    }, [listening, micVAD]);

    return micVAD;
};
