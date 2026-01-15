import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Message, ChatResponse } from '../types';
import './Chatbot.css';

// Typing animation component
const TypingAnimation: React.FC = () => {
  return <span className="typing-dots"></span>;
};

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your SQL Assistant powered by Ollama. Ask me questions about students in natural language.",
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [apiStatus, setApiStatus] = useState<'unknown' | 'connected' | 'error'>('unknown');
  const [hasHealthChecked, setHasHealthChecked] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    checkApiHealth();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/health');
      if (response.data.api === 'running' && response.data.ollama === 'connected') {
        setApiStatus('connected');
        
        // Update the initial welcome message with health info instead of adding a new message
        if (!hasHealthChecked) {
          setMessages(prev => prev.map(msg => 
            msg.id === '1' 
              ? {
                  ...msg,
                  text: `Hello! I'm your SQL Assistant powered by Ollama.\n\n✅ **System Status:**\n• API: Connected\n• Model: ${response.data.model || 'Ollama'}\n• Students: ${response.data.student_count || 0}\n\nAsk me questions about students in natural language.`
                }
              : msg
          ));
          setHasHealthChecked(true);
        }
      }
    } catch (error) {
      setApiStatus('error');
      if (!hasHealthChecked) {
        const errorMessage: Message = {
          id: 'api-error',
          text: '⚠️ Cannot connect to API server. Make sure the backend is running on http://localhost:8000',
          sender: 'bot',
          timestamp: new Date(),
          type: 'error',
          data: { error: 'API connection failed' }
        };
        setMessages(prev => [...prev, errorMessage]);
        setHasHealthChecked(true);
      }
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const response = await axios.post<ChatResponse>(
        'http://localhost:8000/query/',
        { question: inputText },
        { timeout: 45000 }
      );

      // Create a single response message with all components
      const responseId = Date.now().toString();
      
      const botResponse: Message = {
        id: responseId,
        text: '', // Main text will be in the explanation
        sender: 'bot',
        timestamp: new Date(),
        type: 'response',
        data: {
          modelInfo: response.data.model_used || 'Ollama',
          sql: response.data.sql_query,
          explanation: response.data.explanation,
          tableData: response.data.result,
          rowCount: response.data.result.length
        }
      };

      setMessages(prev => [...prev, botResponse]);
      
    } catch (error: any) {
      console.error('API Error:', error);
      
      let errorText = 'Failed to process your request.';
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          errorText = 'Request timed out. Ollama might be processing slowly.';
        } else if (error.response?.status === 503) {
          errorText = 'Ollama service is not available. Make sure Ollama is running.';
        } else {
          errorText = `Error: ${error.response?.data?.detail || error.message}`;
        }
      }
      
      const errorMessage: Message = {
        id: `${Date.now()}-error`,
        text: errorText,
        sender: 'bot',
        timestamp: new Date(),
        type: 'error',
        data: { error: error?.message || 'Unknown error' }
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const quickQuestions = [
    "How many students are there?",
    "Show all students in Data Science class",
    "What is the average marks?",
    "List students sorted by marks"
  ];

  const handleQuickQuestion = (question: string) => {
    setInputText(question);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderMessageContent = (message: Message) => {
    switch (message.type) {
      case 'response':
        return (
          <div className="message-content">
            {/* Model Info */}
            <div className="model-info">
              <span className="model-icon">🤖</span>
              <span className="model-text">Generated using {message.data?.modelInfo || 'Ollama'}</span>
            </div>

            {/* SQL Query */}
            {message.data?.sql && (
              <>
                <div className="content-header">
                  <span className="sql-label">📝 SQL Query</span>
                </div>
                <div className="sql-code-container">
                  <div className="sql-header">SQL</div>
                  <pre className="sql-code">
                    <code>{message.data.sql}</code>
                  </pre>
                </div>
              </>
            )}

            {/* Explanation */}
            {message.data?.explanation && (
              <>
                <div className="content-header">
                  <span className="explanation-label">💡 Explanation</span>
                </div>
                <div className="explanation-container">
                  <div className="explanation-header">How this works</div>
                  <div className="explanation-text">
                    {message.data.explanation}
                  </div>
                </div>
              </>
            )}

            {/* Table Data */}
            {message.data?.tableData && message.data.tableData.length > 0 && (
              <>
                <div className="content-header">
                  <span className="table-label">📊 Query Results</span>
                </div>
                <div className="table-container">
                  <div className="table-header">
                    <span>Data Preview</span>
                    <span>{message.data.tableData.length} rows</span>
                  </div>
                  <div className="table-scroll">
                    <table>
                      <thead>
                        <tr>
                          {message.data.tableData[0].map((_, index) => (
                            <th key={index}>Column {index + 1}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {message.data.tableData.map((row, rowIndex) => (
                          <tr key={rowIndex}>
                            {row.map((cell, cellIndex) => (
                              <td key={cellIndex}>
                                {typeof cell === 'string' && cell.includes('"') 
                                  ? cell.replace(/"/g, '') 
                                  : cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                  <div className="table-footer">
                    <span>Total rows: {message.data.tableData.length}</span>
                    <span>Data loaded successfully</span>
                  </div>
                </div>
              </>
            )}

            {/* No Data Message */}
            {message.data?.tableData && message.data.tableData.length === 0 && (
              <div className="no-data">📭 No data returned from query.</div>
            )}
          </div>
        );
      
      case 'error':
        return (
          <div className="message-content">
            <div className="content-header">
              <span className="error-label">❌ Error</span>
            </div>
            <div className="error-container">
              <div className="error-header">Something went wrong</div>
              <div className="error-text">{message.text}</div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="message-text">
            {message.text.split('\n').map((line, i) => (
              <React.Fragment key={i}>
                {line}
                {i < message.text.split('\n').length - 1 && <br />}
              </React.Fragment>
            ))}
          </div>
        );
    }
  };

  return (
    <div className="chatbot-container">
      {/* Header */}
      <div className="chatbot-header">
        <div className="header-content">
          <h1>
            <span>🤖</span>
            Narural Language to SQL Chatbot
          </h1>
          <p className="header-subtitle">
            Powered by Ollama • Ask questions about students in natural language
          </p>
          <div className="api-status-container">
            <div className={`api-status ${apiStatus}`}>
              <span>Status:</span>
              <span>
                {apiStatus === 'connected' ? '✅ Connected' :
                 apiStatus === 'error' ? '❌ Disconnected' : '⏳ Checking...'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Questions */}
      <div className="quick-questions">
        <h3>
          <span>💡</span>
          Quick Questions
        </h3>
        <div className="question-chips">
          {quickQuestions.map((question, index) => (
            <button
              key={index}
              className="question-chip"
              onClick={() => handleQuickQuestion(question)}
              disabled={isLoading}
              title={question}
            >
              {question}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="chatbot-messages">
        {messages.length === 0 ? (
          <div className="messages-empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Start a conversation</h3>
            <p>
              Ask questions about student data in natural language.
              The AI will generate SQL queries and show you the results.
            </p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.sender} ${message.type}`}
              >
                <div className="message-bubble">
                  <div className="message-header">
                    <span className="message-sender">
                      {message.sender === 'user' ? '👤 You' : '🤖 SQL Assistant'}
                    </span>
                    <span className="message-time">
                      {formatTime(message.timestamp)}
                    </span>
                  </div>
                  {renderMessageContent(message)}
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="message bot typing">
                <div className="message-bubble typing-indicator">
                  <div className="typing-text">
                    Thinking
                    <TypingAnimation />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="chatbot-input-area">
        <div className="input-wrapper">
          <div className="input-container">
            <textarea
              ref={textareaRef}
              value={inputText}
              onChange={handleInputChange}
              onKeyDown={handleKeyPress}
              placeholder="Type your question here... (e.g., How many students are in Data Science class?)"
              disabled={isLoading || apiStatus === 'error'}
              rows={1}
              className={apiStatus === 'error' ? 'input-error' : ''}
              maxLength={500}
            />
            {inputText.length > 0 && (
              <div className="character-count">
                {inputText.length}/500
              </div>
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={isLoading || !inputText.trim() || apiStatus === 'error'}
            className={`send-button ${isLoading ? 'loading' : ''}`}
          >
            {isLoading ? (
              <div className="button-spinner"></div>
            ) : (
              <>
                <span className="button-text">Send</span>
                <span className="button-shortcut">⏎</span>
              </>
            )}
          </button>
        </div>
        <div className="input-hint">
          <div className="hint-item">
            <kbd>Enter</kbd> to send
          </div>
          <div className="hint-item">
            <kbd>Shift</kbd> + <kbd>Enter</kbd> for new line
          </div>
          <div className="hint-ollama">
            <span>⚡</span>
            Using Ollama locally
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;