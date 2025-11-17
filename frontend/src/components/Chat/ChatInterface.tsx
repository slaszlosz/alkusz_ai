import { useState, useEffect, useRef } from 'react';
import { Send, FileText, Loader2 } from 'lucide-react';
import { chatApi, documentsApi, type Source, type Message } from '../../lib/api';
import ReactMarkdown from 'react-markdown';

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput('');
    setLoading(true);

    // Add user message to UI
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    // Add empty assistant message that will be streamed into
    const assistantMsgId = (Date.now() + 1).toString();
    const assistantMsg: Message = {
      id: assistantMsgId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      // Use streaming endpoint
      const response = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let sources: Source[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                if (data.type === 'conversation_id') {
                  setConversationId(data.conversation_id);
                } else if (data.type === 'content') {
                  fullContent += data.content;
                  // Update the assistant message with streaming content
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMsgId
                        ? { ...msg, content: fullContent }
                        : msg
                    )
                  );
                } else if (data.type === 'sources') {
                  sources = data.sources;
                  // Add sources to the message
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMsgId
                        ? { ...msg, sources: sources }
                        : msg
                    )
                  );
                } else if (data.type === 'done') {
                  // Streaming complete
                  break;
                }
              } catch (e) {
                console.log('Parse error:', e);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Hiba történt az üzenet küldésekor. Ellenőrizd, hogy a backend fut-e.');
      // Remove the empty assistant message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMsgId));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSourceClick = (source: Source) => {
    const url = documentsApi.downloadDocument(source.doc_id);
    window.open(url, '_blank');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>AlkuszAI Asszisztens</h2>
        <p style={{ fontSize: '14px', color: '#7f8c8d', marginTop: '4px' }}>
          Kérdezz bármit a feltöltött dokumentumokból
        </p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <h3>Üdvözöllek az AlkuszAI-ban!</h3>
            <p style={{ marginTop: '10px' }}>
              Tölts fel dokumentumokat a Dokumentumok menüpontban,<br />
              majd tedd fel a kérdéseidet.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`message ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}
          >
            {msg.role === 'assistant' ? (
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            ) : (
              msg.content
            )}

            {msg.sources && msg.sources.length > 0 && (
              <div className="message-sources">
                <h4>Források:</h4>
                {msg.sources.map((source, idx) => (
                  <div
                    key={idx}
                    className="source-item"
                    onClick={() => handleSourceClick(source)}
                    title={source.chunk_text}
                  >
                    <FileText size={16} />
                    <span>
                      {source.filename} - {source.page}. oldal
                    </span>
                    <span style={{ marginLeft: 'auto', color: '#95a5a6' }}>
                      {(source.relevance_score * 100).toFixed(0)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <Loader2 size={20} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
            <span style={{ marginLeft: '10px' }}>Gondolkodom...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <div className="chat-input-wrapper">
          <input
            type="text"
            className="chat-input"
            placeholder="Írj egy kérdést... (pl. 'Uniqua basic casco biztosítás mennyit térít jégkárra?')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button
            className="chat-send-btn"
            onClick={handleSend}
            disabled={loading || !input.trim()}
          >
            <Send size={20} />
            Küldés
          </button>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
