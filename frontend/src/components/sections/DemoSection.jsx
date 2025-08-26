import React from 'react';
import BadPdf from '../../assets/pdfs/bad1.pdf';
import GoodPdf from '../../assets/pdfs/good1.pdf';


const DemoSection = ({badPdfPath = BadPdf, goodPdfPath = GoodPdf}) => {
  return (
    <section id="demo" className="demo-section py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h2 className="fw-bold">Пример работы с проблемным PDF</h2>
          <p className="lead text-muted">Попробуйте скопировать текст из обоих PDF</p>
        </div>
        
        <div className="row">
          <div className="col-md-6">
            <div className="card mb-4 h-100">
              <div className="card-body">
                <h5 className="card-title">Оригинальный PDF</h5>
                <div className="mb-3">
                  <h6>Проблема при копировании:</h6>
                  <div className="code-block bg-danger text-white">
                    <pre>Пример искаженного текста: </pre>
                  </div>
                </div>
                {/* Чистый PDF без интерфейса */}
                <div style={{ height: '500px', overflow: 'hidden', background: '#f8f9fa', border: '1px solid #ddd' }}>
                  <object 
                    data={`${badPdfPath}#toolbar=0&navpanes=0&scrollbar=0&statusbar=0&view=FitH`} 
                    type="application/pdf" 
                    width="100%" 
                    height="100%">
                    <p>Ваш браузер не поддерживает PDF. <a href="./pdfs/bad1.pdf">Скачать оригинал</a>.</p>
                  </object>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="card mb-4 h-100">
              <div className="card-body">
                <h5 className="card-title">Результат обработки</h5>
                <div className="mb-3">
                  <h6>Корректный текст:</h6>
                  <div className="code-block bg-success text-white">
                    <pre>Пример исправленного текста: ИЗBEЩEНИЯ МОPEПЛABATEЛЯМ</pre>
                  </div>
                </div>
                {/* Чистый PDF без интерфейса */}
                <div style={{ height: '500px', overflow: 'hidden', background: '#f8f9fa', border: '1px solid #ddd' }}>
                  <object 
                    data={`${goodPdfPath}#toolbar=0&navpanes=0&scrollbar=0&statusbar=0&view=FitH`} 
                    type="application/pdf" 
                    width="100%" 
                    height="100%">
                    <p>Ваш браузер не поддерживает PDF. <a href="./pdfs/good1.pdf">Скачать результат</a>.</p>
                  </object>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default DemoSection;