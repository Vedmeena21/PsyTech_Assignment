import React, { useState, useRef } from 'react';
import { Mic, MicOff, Send, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:50010';

function App() {
    const [isRecording, setIsRecording] = useState(false);
    const [transcription, setTranscription] = useState('');
    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    // Start recording audio
    const startRecording = async () => {
        setError('');
        setTranscription('');
        setResults(null);
        audioChunksRef.current = [];

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());

                // Create audio blob
                const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

                // Send to backend for Whisper transcription + analysis
                await analyzeAudio(audioBlob);
            };

            mediaRecorderRef.current = mediaRecorder;
            mediaRecorder.start();
            setIsRecording(true);
        } catch (err) {
            console.error('Microphone access error:', err);
            setError('Microphone access denied. Please allow microphone permissions.');
        }
    };

    // Stop recording
    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    // Analyze audio via backend API (Whisper + Multi-task model)
    const analyzeAudio = async (audioBlob) => {
        setLoading(true);
        setError('');

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');

            const response = await axios.post(`${API_URL}/analyze`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            if (response.data.success) {
                setTranscription(response.data.transcription);
                setResults(response.data.data);
            } else {
                setError(response.data.error || 'Analysis failed');
            }
        } catch (err) {
            console.error('API Error:', err);
            setError(
                err.response?.data?.error ||
                'Failed to connect to backend. Make sure the server is running.'
            );
        } finally {
            setLoading(false);
        }
    };

    // Analyze text via backend API
    const analyzeText = async (text) => {
        setLoading(true);
        setError('');

        try {
            const response = await axios.post(`${API_URL}/analyze`, {
                text: text
            });

            if (response.data.success) {
                setTranscription(response.data.transcription);
                setResults(response.data.data);
            } else {
                setError(response.data.error || 'Analysis failed');
            }
        } catch (err) {
            console.error('API Error:', err);
            setError(
                err.response?.data?.error ||
                'Failed to connect to backend. Make sure the server is running.'
            );
        } finally {
            setLoading(false);
        }
    };

    // Manual text submission
    const handleManualSubmit = () => {
        if (transcription.trim()) {
            analyzeText(transcription);
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
                        Voice → Whisper ASR (Backend) | Multi-task Transformer
                    </p>
                </div>

                {/* Main Content Grid */}
                <div className="grid md:grid-cols-2 gap-6">
                    {/* Input Section */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center">
                            <Mic className="w-6 h-6 mr-2 text-orange-600" />
                            Voice Input
                        </h2>

                        {/* Voice Recording Button */}
                        <div className="flex flex-col items-center space-y-4 mb-6">
                            <button
                                onClick={isRecording ? stopRecording : startRecording}
                                disabled={loading}
                                className={`w-32 h-32 rounded-full flex items-center justify-center transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed ${isRecording
                                    ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                                    : 'bg-orange-500 hover:bg-orange-600'
                                    } text-white shadow-2xl`}
                            >
                                {isRecording ? (
                                    <MicOff className="w-12 h-12" />
                                ) : (
                                    <Mic className="w-12 h-12" />
                                )}
                            </button>
                            <div className="text-center">
                                <p className="text-sm font-medium text-gray-700">
                                    {isRecording
                                        ? 'Recording... Click to stop'
                                        : 'Click to speak in Hinglish'}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">
                                    Audio sent to Whisper for transcription
                                </p>
                            </div>
                        </div>

                        {/* Manual Text Input */}
                        <div className="space-y-3">
                            <label className="block text-sm font-medium text-gray-700">
                                Or type your message:
                            </label>
                            <textarea
                                value={transcription}
                                onChange={(e) => setTranscription(e.target.value)}
                                placeholder="Type in Hinglish... (e.g., 'Mujhe job nahi mil rahi Krishna ji')"
                                className="w-full h-28 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent resize-none text-gray-800"
                                disabled={loading || isRecording}
                            />
                            <button
                                onClick={handleManualSubmit}
                                disabled={loading || !transcription.trim() || isRecording}
                                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                            >
                                <Send className="w-5 h-5" />
                                <span>Analyze Text</span>
                            </button>
                        </div>

                        {/* Error Display */}
                        {error && (
                            <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 rounded-lg flex items-start space-x-3">
                                <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
                                <div>
                                    <p className="text-sm font-medium text-red-800">Error</p>
                                    <p className="text-sm text-red-700 mt-1">{error}</p>
                                </div>
                            </div>
                        )}

                        {/* Transcription Display */}
                        {transcription && !error && (
                            <div className="mt-4 p-4 bg-orange-50 border-l-4 border-orange-400 rounded-lg">
                                <p className="text-sm font-semibold text-orange-900 mb-2">
                                    Transcription:
                                </p>
                                <p className="text-gray-800 leading-relaxed">{transcription}</p>
                            </div>
                        )}
                    </div>

                    {/* Results Section */}
                    <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100">
                        <h2 className="text-2xl font-semibold text-gray-800 mb-6">
                            Analysis Results
                        </h2>

                        {loading ? (
                            <div className="flex flex-col items-center justify-center h-96 space-y-4">
                                <Loader2 className="w-16 h-16 text-orange-500 animate-spin" />
                                <p className="text-gray-600 font-medium">Analyzing content...</p>
                                <p className="text-sm text-gray-500">Whisper ASR + Multi-task Transformer</p>
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
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold ${results.sentiment.label === 'positive' ? 'bg-green-500 text-white' :
                                                results.sentiment.label === 'negative' ? 'bg-red-500 text-white' :
                                                    'bg-gray-500 text-white'
                                                }`}>
                                                {results.sentiment.label.toUpperCase()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${results.sentiment.confidence * 100}%` }}
                                            />
                                        </div>
                                        <p className="text-sm text-gray-600 mt-2 text-right font-medium">
                                            {(results.sentiment.confidence * 100).toFixed(1)}% confidence
                                        </p>
                                    </div>

                                    {/* Toxicity */}
                                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="font-semibold text-gray-700">Toxicity</span>
                                            <span className={`px-3 py-1 rounded-full text-sm font-bold ${results.toxicity.label === 'safe' ? 'bg-green-500 text-white' :
                                                results.toxicity.label === 'offensive' ? 'bg-red-500 text-white' :
                                                    'bg-yellow-500 text-white'
                                                }`}>
                                                {results.toxicity.label.toUpperCase()}
                                            </span>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                                            <div
                                                className="bg-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
                                                style={{ width: `${results.toxicity.confidence * 100}%` }}
                                            />
                                        </div>
                                        <p className="text-sm text-gray-600 mt-2 text-right font-medium">
                                            {(results.toxicity.confidence * 100).toFixed(1)}% confidence
                                        </p>
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
                                                <div key={idx} className="p-4 bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg border border-orange-200">
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
                            <div className="flex flex-col items-center justify-center h-96 text-gray-400">
                                <Mic className="w-20 h-20 mb-4 opacity-30" />
                                <p className="text-center font-medium">
                                    Record or type a message to see analysis results
                                </p>
                                <p className="text-sm mt-2 text-center max-w-xs">
                                    Try: "Mujhe job nahi mil rahi Krishna ji"
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
