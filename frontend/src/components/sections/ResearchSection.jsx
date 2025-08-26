export default function Research() {
  return (
    <section className="py-5 bg-light">
      <div className="container">
        <div className="row align-items-center">
          <div className="col-lg-6">
            <h2 className="fw-bold mb-4">Научное обоснование</h2>
            <ul className="mb-4">
              <li>Точность 95% на 14 типах документов</li>
              <li>Обучение на 29,172 изображениях глифов</li>
              <li>102 класса символов</li>
            </ul>
            <a 
              href="https://www.ispras.ru/proceedings/docs/2024/36/3/isp_36_2024_3_189.pdf" 
              className="btn btn-outline-primary"
              target="_blank"
              rel="noopener noreferrer"
            >
              Читать исследование
            </a>
          </div>
          <div className="col-lg-6 mt-4 mt-lg-0">
            <div className="card">
              <div className="card-body">
                <h5 className="card-title">Цитирование</h5>
                <p className="card-text">
                  Загородников М.В., Михайлов А.А. Восстановление текстового слоя PDF документов. 
                  Труды ИСП РАН, том 36, вып. 3, 2024 г.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}