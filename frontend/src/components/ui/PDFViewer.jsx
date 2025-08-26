import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { Button } from 'react-bootstrap';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

// Настройка PDF worker
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function PDFViewer({ file, width = 500 }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  return (
    <div className="pdf-viewer">
      <Document
        file={file}
        onLoadSuccess={onDocumentLoadSuccess}
        loading={<div>Загрузка PDF...</div>}
        error={<div className="text-danger">Ошибка загрузки PDF</div>}
      >
        <Page 
          pageNumber={pageNumber} 
          width={width}
          renderTextLayer={false}
          loading={<div>Загрузка страницы...</div>}
        />
      </Document>
      
      {numPages && (
        <div className="d-flex justify-content-between align-items-center mt-2">
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={() => setPageNumber(prev => Math.max(prev - 1, 1))}
            disabled={pageNumber <= 1}
          >
            ← Назад
          </Button>
          
          <span className="text-muted small">
            Страница {pageNumber} из {numPages}
          </span>
          
          <Button
            variant="outline-secondary"
            size="sm"
            onClick={() => setPageNumber(prev => Math.min(prev + 1, numPages))}
            disabled={pageNumber >= numPages}
          >
            Вперед →
          </Button>
        </div>
      )}
    </div>
  );
}