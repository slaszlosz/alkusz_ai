import { useState } from 'react';
import { MessageSquare, Upload, FileText, BarChart3 } from 'lucide-react';
import ChatInterface from './components/Chat/ChatInterface';
import DocumentUpload from './components/Upload/DocumentUpload';
import DocumentBrowser from './components/Documents/DocumentBrowser';
import MetricsDashboard from './components/Metrics/MetricsDashboard';

type View = 'chat' | 'upload' | 'documents' | 'metrics';

function App() {
  const [currentView, setCurrentView] = useState<View>('chat');

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>AlkuszAI</h1>
          <p style={{ fontSize: '14px', color: '#95a5a6', marginTop: '5px' }}>
            Vállalati Tudásbázis
          </p>
        </div>

        <nav className="sidebar-nav">
          <div
            className={`nav-item ${currentView === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentView('chat')}
          >
            <MessageSquare size={20} />
            <span>Chat</span>
          </div>

          <div
            className={`nav-item ${currentView === 'upload' ? 'active' : ''}`}
            onClick={() => setCurrentView('upload')}
          >
            <Upload size={20} />
            <span>Feltöltés</span>
          </div>

          <div
            className={`nav-item ${currentView === 'documents' ? 'active' : ''}`}
            onClick={() => setCurrentView('documents')}
          >
            <FileText size={20} />
            <span>Dokumentumok</span>
          </div>

          <div
            className={`nav-item ${currentView === 'metrics' ? 'active' : ''}`}
            onClick={() => setCurrentView('metrics')}
          >
            <BarChart3 size={20} />
            <span>Metrikák</span>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {currentView === 'chat' && <ChatInterface />}
        {currentView === 'upload' && <DocumentUpload />}
        {currentView === 'documents' && <DocumentBrowser />}
        {currentView === 'metrics' && <MetricsDashboard />}
      </div>
    </div>
  );
}

export default App;
