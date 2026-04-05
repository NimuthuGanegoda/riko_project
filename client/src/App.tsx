import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Send, Volume2, Sparkles, Heart } from 'lucide-react';

const API_BASE = "http://localhost:8000";

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

const RikoSVG = () => (
  <svg viewBox="0 0 200 200" className="riko-avatar">
    <circle cx="100" cy="100" r="90" fill="#fff" />
    <path d="M40 80 Q 100 20 160 80" stroke="#ff7eb9" strokeWidth="8" fill="none" />
    <circle cx="70" cy="90" r="10" fill="#2d3436" />
    <circle cx="130" cy="90" r="10" fill="#2d3436" />
    <path d="M80 130 Q 100 150 120 130" stroke="#ff7eb9" strokeWidth="5" fill="none" />
    <path d="M50 100 Q 60 110 70 100" stroke="#ffadd2" strokeWidth="3" fill="none" />
    <path d="M130 100 Q 140 110 150 100" stroke="#ffadd2" strokeWidth="3" fill="none" />
  </svg>
);

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [status, setStatus] = useState("Ready to chat");
  const [isThinking, setIsThinking] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendText = async () => {
    if (!inputText.trim() || isThinking) return;
    
    const userMsg: Message = { role: 'user', content: inputText };
    setMessages(prev => [...prev, userMsg]);
    setInputText("");
    setIsThinking(true);
    setStatus("Thinking...");

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        text: inputText,
        history: messages
      });
      
      const rikoMsg: Message = { role: 'assistant', content: response.data.text };
      setMessages(prev => [...prev, rikoMsg]);
      
      if (response.data.audio_url) {
        playAudio(`${API_BASE}${response.data.audio_url}`);
      }
      setStatus("Ready");
    } catch (error) {
      console.error(error);
      setStatus("Error connecting to server");
    } finally {
      setIsThinking(false);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        sendVoice(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setStatus("Listening...");
    } catch (err) {
      console.error("Mic error:", err);
      setStatus("Microphone access denied");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
    setStatus("Processing voice...");
  };

  const sendVoice = async (blob: Blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    formData.append('history', JSON.stringify(messages));
    setIsThinking(true);

    try {
      const response = await axios.post(`${API_BASE}/voice`, formData);
      
      if (response.data.user_text) {
        setMessages(prev => [...prev, { role: 'user', content: response.data.user_text }]);
      }
      
      const rikoMsg: Message = { role: 'assistant', content: response.data.text };
      setMessages(prev => [...prev, rikoMsg]);
      
      if (response.data.audio_url) {
        playAudio(`${API_BASE}${response.data.audio_url}`);
      }
      setStatus("Ready");
    } catch (error) {
      console.error(error);
      setStatus("Voice processing failed");
    } finally {
      setIsThinking(false);
    }
  };

  const playAudio = (url: string) => {
    const audio = new Audio(url);
    setStatus("Speaking...");
    audio.onended = () => setStatus("Ready");
    audio.play();
  };

  return (
    <div className="app-container">
      {/* Left: Riko View */}
      <div className="riko-view">
        <motion.div 
          className="riko-avatar-container"
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        >
          <RikoSVG />
        </motion.div>
        
        <div className="status-badge">
          {isThinking ? <Sparkles size={16} className="animate-pulse" /> : <Heart size={16} fill={status === "Ready" ? "var(--primary)" : "none"} />}
          {status}
        </div>

        <div className="visualizer">
          {[...Array(8)].map((_, i) => (
            <motion.div 
              key={i}
              className="viz-bar"
              animate={status === "Speaking..." || isRecording ? { height: [10, Math.random() * 40 + 10, 10] } : { height: 10 }}
              transition={{ duration: 0.2, repeat: Infinity }}
            />
          ))}
        </div>
      </div>

      {/* Right: Chat View */}
      <div className="chat-view">
        <div className="chat-header">
          <h2>Riko AI 🌸</h2>
          <div className="flex gap-2">
            <Volume2 size={20} color="#ccc" />
          </div>
        </div>

        <div className="messages-list">
          <AnimatePresence>
            {messages.filter(m => m.role !== 'system').map((msg, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-riko'}`}
              >
                {msg.content}
              </motion.div>
            ))}
            {isThinking && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="message-bubble message-riko">
                ...
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <button 
            className={`action-btn mic-btn ${isRecording ? 'active' : ''}`}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
          >
            <Mic size={20} />
          </button>
          
          <div className="input-wrapper">
            <input 
              type="text" 
              className="chat-input" 
              placeholder="Type a message, senpai..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
            />
          </div>

          <button className="action-btn" onClick={handleSendText}>
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;
