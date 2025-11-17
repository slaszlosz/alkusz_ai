import { useState, useEffect } from 'react';
import { Download, Trash2, FileText, Loader2 } from 'lucide-react';
import { documentsApi, type Document } from '../../lib/api';

export default function DocumentBrowser() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentsApi.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const statsData = await documentsApi.getStats();
      setStats(statsData);
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleDownload = (doc: Document) => {
    const url = documentsApi.downloadDocument(doc.id);
    window.open(url, '_blank');
  };

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Biztosan törölni szeretnéd: ${doc.filename}?`)) return;

    try {
      await documentsApi.deleteDocument(doc.id);
      setDocuments(documents.filter((d) => d.id !== doc.id));
      loadStats(); // Refresh stats
      alert('Dokumentum sikeresen törölve!');
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Hiba történt a törlés során.');
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('hu-HU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number) => {
    return (bytes / 1024 / 1024).toFixed(2) + ' MB';
  };

  if (loading) {
    return (
      <div className="loading">
        <Loader2 size={32} style={{ animation: 'spin 1s linear infinite' }} />
        <span style={{ marginLeft: '15px' }}>Betöltés...</span>
      </div>
    );
  }

  return (
    <div className="documents-container">
      <div className="documents-header">
        <div>
          <h2 style={{ color: '#2c3e50' }}>Dokumentumok</h2>
          {stats && (
            <p style={{ color: '#7f8c8d', marginTop: '8px' }}>
              {stats.total_documents} dokumentum • {stats.total_pages} oldal • {stats.total_chunks} chunk
            </p>
          )}
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="empty-state">
          <FileText size={64} />
          <h3 style={{ marginTop: '20px' }}>Még nincsenek dokumentumok</h3>
          <p style={{ marginTop: '10px' }}>
            Menj a Feltöltés oldalra dokumentumok hozzáadásához
          </p>
        </div>
      ) : (
        <div className="documents-grid">
          {documents.map((doc) => (
            <div key={doc.id} className="document-card">
              <h3>{doc.filename}</h3>

              <div className="document-info">
                <div className="document-info-item">
                  <span>Méret:</span>
                  <span>{formatFileSize(doc.file_size)}</span>
                </div>
                <div className="document-info-item">
                  <span>Oldalak:</span>
                  <span>{doc.page_count}</span>
                </div>
                <div className="document-info-item">
                  <span>Chunkok:</span>
                  <span>{doc.chunk_count}</span>
                </div>
                {doc.category && (
                  <div className="document-info-item">
                    <span>Kategória:</span>
                    <span style={{ fontWeight: '600', color: '#3498db' }}>
                      {doc.category}
                    </span>
                  </div>
                )}
                <div className="document-info-item">
                  <span>Feltöltve:</span>
                  <span>{formatDate(doc.upload_date)}</span>
                </div>
                <div className="document-info-item">
                  <span>Státusz:</span>
                  <span
                    className={`status-badge ${
                      doc.processed ? 'status-processed' : 'status-processing'
                    }`}
                  >
                    {doc.processed ? 'Feldolgozva' : 'Feldolgozás alatt'}
                  </span>
                </div>
              </div>

              <div className="document-actions">
                <button
                  className="btn btn-primary"
                  onClick={() => handleDownload(doc)}
                  title="Letöltés"
                >
                  <Download size={16} />
                  Letöltés
                </button>
                <button
                  className="btn btn-danger"
                  onClick={() => handleDelete(doc)}
                  title="Törlés"
                >
                  <Trash2 size={16} />
                  Törlés
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
