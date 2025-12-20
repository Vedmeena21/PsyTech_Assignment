import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:50010';

function App() {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [status, setStatus] = useState('Ready');

    // Refs to access latest state inside event listeners without closure issues
    const recognitionRef = useRef(null);
    const transcriptRef = useRef('');

    // Initialize Speech Recognition on mount
    useEffect(() => {
        // Browser compatibility check
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'hi-IN'; // Set to Hindi to capture accurate Devanagari

            recognition.onstart = () => {
                setIsListening(true);
                setStatus('Listening...');
            };

            recognition.onresult = (event) => {
                let currentTranscript = '';
                for (let i = 0; i < event.results.length; i++) {
                    currentTranscript += event.results[i][0].transcript;
                }

                // Update both Ref (for logic) and State (for UI)
                transcriptRef.current = currentTranscript;
                setTranscript(currentTranscript);
                setStatus('Processing speech...');
            };

            recognition.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                if (event.error === 'not-allowed') {
                    setError('Microphone permission denied. Please allow it in browser settings.');
                } else {
                    setError(`Error: ${event.error}`);
                }
                setIsListening(false);
                setStatus('Error occurred');
            };

            recognition.onend = () => {
                setIsListening(false);
                setStatus('Stopped');
            };

            recognitionRef.current = recognition;
        } else {
            setError('Browser not supported. Please use Google Chrome.');
            setStatus('Not Supported');
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);

    const startListening = () => {
        if (!recognitionRef.current) return;
        setError('');
        setResults(null);
        setTranscript('');
        transcriptRef.current = ''; // Reset ref

        try {
            recognitionRef.current.start();
        } catch (err) {
            console.error("Failed to start", err);
        }
    };

    const stopListening = () => {
        if (!recognitionRef.current) return;
        recognitionRef.current.stop();
        // setIsListening(false); // Handled by onend

        // Use the REF to get the text, ensuring it's not stale
        const finalGet = transcriptRef.current;
        console.log("Stopping. Final text:", finalGet);

        // Auto-analyze
        setTimeout(() => {
            if (finalGet && finalGet.trim()) {
                analyzeText(finalGet);
            }
        }, 800);
    };

    const analyzeText = async (text) => {
        if (!text || !text.trim()) return;

        setLoading(true);
        setStatus('Analyzing with AI...');
        setError('');

        try {
            const response = await axios.post(`${API_URL}/analyze`, {
                text: text
            });

            if (response.data.success) {
                setResults(response.data.data);
                setStatus('Analysis Complete');
            } else {
                setError(response.data.error || 'Analysis failed');
                setStatus('Failed');
            }
        } catch (err) {
            console.error('API Error:', err);
            setError('Failed to connect to backend.');
            setStatus('Connection Error');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-orange-50 p-4">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="text-center mb-8 pt-8">
                    <h1 className="text-5xl font-bold text-orange-800 mb-3">
                        Krishna AI Content Intelligence
                    </h1>
                    <p className="text-lg text-gray-600">
                        Devotional Content Moderation & Tagging Dashboard
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                        Speak or type in Hinglish for real-time AI analysis
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                        Professional Edition
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                    {/* Input Area */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-2xl font-semibold text-gray-800 flex items-center">
                                <Mic className="w-6 h-6 mr-2 text-orange-600" />
                                Voice Input
                            </h2>
                            <span className={`text-sm font-bold px-2 py-1 rounded ${status === 'Listening...' ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600'
                                }`}>
                                {status}
                            </span>
                        </div>

                        <div className="flex flex-col items-center space-y-4 mb-6">
                            <button
                                onClick={isListening ? stopListening : startListening}
                                disabled={loading || !!error}
                                className={`w-32 h-32 rounded-full flex items-center justify-center transition-all transform hover:scale-105 ${isListening
                                    ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                                    : 'bg-orange-500 hover:bg-orange-600'
                                    } text-white shadow-2xl`}
                            >
                                {isListening ? <MicOff className="w-12 h-12" /> : <Mic className="w-12 h-12" />}
                            </button>
                            <div className="text-center">
                                <p className="text-sm font-medium text-gray-700">
                                    {isListening ? 'Listening... Click to Stop' : 'Click to Speak (in Hindi)'}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    Powered by Native Web Speech API (hi-IN)
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={transcript}
                            onChange={(e) => {
                                setTranscript(e.target.value);
                                transcriptRef.current = e.target.value; // Sync ref if manually edited
                            }}
                            placeholder="Transcript appears here..."
                            className="w-full h-28 px-4 py-3 border-2 border-gray-300 rounded-lg text-gray-800"
                        />
                        <button
                            onClick={() => analyzeText(transcript)}
                            className="w-full mt-3 bg-orange-600 hover:bg-orange-700 text-white font-medium py-3 rounded-lg flex justify-center items-center"
                        >
                            <Send className="w-5 h-5 mr-2" /> Analyze Text
                        </button>

                        {error && (
                            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg flex items-center">
                                <AlertCircle className="w-5 h-5 mr-2" /> {error}
                            </div>
                        )}
                    </div>

                    {/* Results Area */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Results</h2>

                        {loading ? (
                            <div className="flex flex-col items-center justify-center h-64">
                                <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
                                <p className="mt-2 text-gray-500">Analyzing...</p>
                            </div>
                        ) : results ? (
                            <div className="space-y-6">
                                {/* Moderation Results */}
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-800 mb-4 pb-2 border-b-2 border-gray-200">
                                        Moderation Results
                                    </h3>

                                    {/* Sentiment */}
                                    <div className="mb-5 p-4 bg-blue-50 rounded-lg border border-blue-200">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="font-semibold text-gray-700">Sentiment</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold uppercase ${results.sentiment.label === 'positive' ? 'bg-green-500 text-white' :
                                                results.sentiment.label === 'negative' ? 'bg-red-500 text-white' : 'bg-gray-500 text-white'
                                                }`}>{results.sentiment.label}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${results.sentiment.confidence * 100}%` }}></div>
                                        </div>
                                        <p className="text-right text-xs text-blue-600 mt-1">{(results.sentiment.confidence * 100).toFixed(1)}% confidence</p>
                                    </div>

                                    {/* Toxicity */}
                                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="font-semibold text-gray-700">Toxicity</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold uppercase ${results.toxicity.label === 'safe' ? 'bg-green-500 text-white' :
                                                results.toxicity.label === 'offensive' ? 'bg-red-500 text-white' : 'bg-yellow-500 text-white'
                                                }`}>{results.toxicity.label}</span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div className="bg-purple-600 h-3 rounded-full" style={{ width: `${results.toxicity.confidence * 100}%` }}></div>
                                        </div>
                                        <p className="text-right text-xs text-purple-600 mt-1">{(results.toxicity.confidence * 100).toFixed(1)}% confidence</p>
                                    </div>
                                </div>

                                {/* Devotional Tags */}
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-800 mb-4 pb-2 border-b-2 border-gray-200">
                                        Devotional Category Tags
                                    </h3>
                                    {results.categories && results.categories.length > 0 ? (
                                        <div className="space-y-3">
                                            {results.categories.map((cat, idx) => (
                                                <div key={idx} className="p-4 bg-orange-50 rounded-lg border border-orange-200">
                                                    <div className="flex justify-between items-center mb-2">
                                                        <span className="font-semibold text-gray-800 capitalize text-base">
                                                            {cat.label.replace('_', ' ')}
                                                        </span>
                                                        <span className="text-sm font-bold text-orange-700">
                                                            {(cat.confidence * 100).toFixed(1)}%
                                                        </span>
                                                    </div>
                                                    <div className="w-full bg-orange-200 rounded-full h-3 overflow-hidden">
                                                        <div
                                                            className="bg-orange-600 h-3 rounded-full transition-all duration-500 ease-out"
                                                            style={{ width: `${cat.confidence * 100}%` }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <div className="text-center py-8">
                                            <p className="text-gray-500 italic">
                                                No categories detected above threshold (40%)
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="text-center text-gray-400 py-12">
                                <p>Record or type to see results</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;