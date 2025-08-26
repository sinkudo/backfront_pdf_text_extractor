import React, { useState } from 'react';
import { Container, Row, Col, Card, Button, Alert, Spinner } from 'react-bootstrap';
import NavBar from '../components/ui/NavBar';
import Footer from '../components/ui/Footer';
import '../assets/styles/ExtractPage.css';

const TextExtractorPage = () => {
  // Состояние компонента
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [pdfData, setPdfData] = useState(null);

  // Обработчик выбора файла
  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult('');
    setError('');
    setPdfData(null);
  };
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  const extractText = async () => {
    if (!file) {
      setError('Пожалуйста, выберите файл');
      return;
    }

    setIsProcessing(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      // const response = await fetch('https://20b94ebd58b7.ngrok-free.app/extract-text', {
      //   method: 'POST',
      //   body: formData,
      // });
      const response = await fetch(`${API_BASE_URL}/extract-text`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Ошибка сервера');
      }

      const data = await response.json();
      setResult(data.text);
      setPdfData({
        base64: data.pdf,
        filename: data.filename
      });
    } catch (err) {
      setError(err.message || 'Ошибка при обработке файла');
      console.error('Ошибка:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Скачивание исправленного PDF
  const downloadPdf = () => {
    if (!pdfData) return;
    
    try {
      // Декодируем base64
      const byteCharacters = atob(pdfData.base64);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], {type: 'application/pdf'});
      
      // Создаем ссылку для скачивания
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = pdfData.filename;
      document.body.appendChild(link);
      link.click();
      
      // Очистка
      setTimeout(() => {
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }, 100);
    } catch (err) {
      setError('Ошибка при создании PDF');
      console.error(err);
    }
  };

  return (
    <div className="extractor-container">
      <NavBar />
      
      <main className="extractor-main">
        <Container>
          <Row className="justify-content-center">
            <Col md={8}>
              <h1 className="text-center mb-4">Извлечение текста из PDF</h1>
              
              <Card className="shadow mb-4">
                <Card.Body>
                  <div className="mb-4">
                    <label htmlFor="pdf-upload" className="pdf-upload-label">
                      <strong>Выберите PDF-файл:</strong>
                    </label>
                    <input
                      type="file"
                      id="pdf-upload"
                      className="form-control"
                      accept=".pdf"
                      onChange={handleFileChange}
                      disabled={isProcessing}
                    />
                    {file && (
                      <div className="file-selected">
                        Выбран файл: {file.name}
                      </div>
                    )}
                  </div>

                  <div className="d-grid gap-2">
                    <Button
                      variant="primary"
                      size="lg"
                      onClick={extractText}
                      disabled={isProcessing || !file}
                    >
                      {isProcessing ? (
                        <>
                          <Spinner
                            as="span"
                            animation="border"
                            size="sm"
                            role="status"
                            aria-hidden="true"
                            className="me-2"
                          />
                          Обработка...
                        </>
                      ) : (
                        'Извлечь текст'
                      )}
                    </Button>
                  </div>

                  {error && (
                    <Alert variant="danger" className="mt-3">
                      {error}
                    </Alert>
                  )}
                </Card.Body>
              </Card>

              {(result || pdfData) && (
                <Card className="shadow">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-center mb-3">
                      <h5 className="mb-0">Результат:</h5>
                      {pdfData && (
                        <Button
                          variant="success"
                          onClick={downloadPdf}
                          size="sm"
                        >
                          Скачать исправленный PDF
                        </Button>
                      )}
                    </div>
                    
                    {result && (
                      <div className="mt-3">
                        <pre className="result-pre">
                          {result}
                        </pre>
                      </div>
                    )}
                    
                    <div className="mt-3 d-flex gap-2">
                      {result && (
                        <>
                          <Button
                            variant="outline-primary"
                            onClick={() => navigator.clipboard.writeText(result)}
                          >
                            Копировать текст
                          </Button>
                          <Button 
                            variant="outline-secondary" 
                            onClick={() => {
                              setResult('');
                              setPdfData(null);
                            }}
                          >
                            Очистить
                          </Button>
                        </>
                      )}
                    </div>
                  </Card.Body>
                </Card>
              )}
            </Col>
          </Row>
        </Container>
      </main>

      <Footer />
    </div>
  );
};

export default TextExtractorPage;