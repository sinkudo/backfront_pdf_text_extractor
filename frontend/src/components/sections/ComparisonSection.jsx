import { Table, ProgressBar, Card } from 'react-bootstrap';

export default function Comparison() {
  return (
    <section id="comparison" className="py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h2 className="fw-bold">Сравнение с другими решениями</h2>
          <p className="lead text-muted">Наш метод показывает лучшие результаты на сложных PDF</p>
        </div>
        
        <div className="row">
          <div className="col-lg-8 mx-auto">
            <Card border="light" className="shadow-sm">
              <Card.Body className="p-4">
                <div className="table-responsive">
                  <Table hover className="mb-4">
                    <thead className="table-light">
                      <tr>
                        <th>Характеристика</th>
                        <th>Обычные OCR</th>
                        <th>PDF Text Extractor</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td>Работа с PDF со сложным фоном</td>
                        <td><span className="badge bg-warning">Частично</span></td>
                        <td><span className="badge bg-success">Да</span></td>
                      </tr>
                      <tr>
                        <td>Точность на сложном фоне</td>
                        <td>35-70%</td>
                        <td>85-95%</td>
                      </tr>
                      <tr>
                        <td>Формирование корректного PDF</td>
                        <td><span className="badge bg-danger">Нет</span></td>
                        <td><span className="badge bg-success">Да</span></td>
                      </tr>
                    </tbody>
                  </Table>
                </div>
                
                <div className="mt-4">
                  <h5 className="mb-3">Результаты тестирования точности:</h5>
                  <div className="mb-3">
                    <h6 className="small">Tesseract</h6>
                    <ProgressBar now={50} variant="danger" label="50%" style={{ height: '25px' }} />
                  </div>
                  <div className="mb-3">
                    <h6 className="small">PDF Text Extractor</h6>
                    <ProgressBar 
                      now={90} 
                      style={{ 
                        height: '25px', 
                      }} 
                      label="90%" 
                    />
                  </div>
                  <p className="small text-muted">Тестирование проводилось на 14 типах сложных PDF-документов</p>
                </div>
              </Card.Body>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}