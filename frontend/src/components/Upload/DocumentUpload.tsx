import { useState } from 'react';
import { Upload, File, CheckCircle, Loader2 } from 'lucide-react';
import { documentsApi } from '../../lib/api';

export default function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadSuccess(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setUploadSuccess(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    try {
      await documentsApi.uploadDocument(selectedFile, category || undefined);
      setUploadSuccess(true);
      setSelectedFile(null);
      setCategory('');
      alert('Dokumentum sikeresen feltöltve és feldolgozva!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Hiba történt a feltöltés során. Ellenőrizd, hogy a backend fut-e.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h2>Dokumentum feltöltés</h2>
        <p style={{ color: '#7f8c8d', marginTop: '8px' }}>
          Támogatott formátumok: PDF, DOCX, TXT
        </p>
      </div>

      <div
        className={`upload-area ${dragOver ? 'drag-over' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('file-input')?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,.docx,.txt"
          onChange={handleFileSelect}
        />

        {!selectedFile ? (
          <>
            <Upload size={48} className="upload-icon" />
            <h3 style={{ color: '#2c3e50', marginBottom: '10px' }}>
              Húzd ide a fájlt vagy kattints a kiválasztáshoz
            </h3>
            <p style={{ color: '#95a5a6' }}>
              PDF, DOCX vagy TXT fájl (max. 10MB)
            </p>
          </>
        ) : (
          <>
            <File size={48} style={{ color: '#3498db', margin: '0 auto 20px' }} />
            <h3 style={{ color: '#2c3e50', marginBottom: '10px' }}>
              {selectedFile.name}
            </h3>
            <p style={{ color: '#95a5a6' }}>
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </>
        )}
      </div>

      {selectedFile && (
        <>
          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <input
              type="text"
              className="category-input"
              placeholder="Kategória (opcionális, pl: Uniqua, Generali)"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
          </div>

          <div style={{ textAlign: 'center' }}>
            <button
              className="upload-btn"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? (
                <>
                  <Loader2 size={20} style={{ animation: 'spin 1s linear infinite' }} />
                  Feltöltés és feldolgozás...
                </>
              ) : uploadSuccess ? (
                <>
                  <CheckCircle size={20} />
                  Sikeres feltöltés!
                </>
              ) : (
                <>
                  <Upload size={20} />
                  Feltöltés és feldolgozás
                </>
              )}
            </button>
          </div>
        </>
      )}

      <div style={{ marginTop: '40px', padding: '20px', background: 'white', borderRadius: '12px' }}>
        <h3 style={{ color: '#2c3e50', marginBottom: '15px' }}>Hogyan működik?</h3>
        <ol style={{ color: '#7f8c8d', lineHeight: '1.8', paddingLeft: '20px' }}>
          <li>Válaszd ki vagy húzd be a dokumentumot</li>
          <li>Opcionálisan add meg a kategóriát (biztosító neve, terméktípus)</li>
          <li>Kattints a "Feltöltés" gombra</li>
          <li>A rendszer feldolgozza a dokumentumot és hozzáadja a tudásbázishoz</li>
          <li>Ezután a Chat oldalon kérdezhetsz a dokumentumból</li>
        </ol>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
