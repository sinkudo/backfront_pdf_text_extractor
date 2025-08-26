import { Accordion } from 'react-bootstrap';

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="py-5 bg-light">
      <div className="container">
        <div className="row align-items-center">
          <div className="col-lg-6">
            <h2 className="fw-bold mb-4">Как это работает</h2>
            <Accordion defaultActiveKey="0">
              <Accordion.Item eventKey="0">
                <Accordion.Header>1. Извлечение шрифтов</Accordion.Header>
                <Accordion.Body>
                  Извлечение шрифтов всех шрифтов вшитых в PDF.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="1">
                <Accordion.Header>2. Извлечение глифов</Accordion.Header>
                <Accordion.Body>
                  Извлечение глифов шрифтов PDF-документа как изображений.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="2">
                <Accordion.Header>3. Распознавание глифов</Accordion.Header>
                <Accordion.Body>
                  Распознавание изображений глифов с помощью свёрточной нейронной сети.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="3">
                <Accordion.Header>4. Сопоставление глифов и символов.</Accordion.Header>
                <Accordion.Body>
                  Создание словаря соответствий между глифами и символами полученными в результате работы нейронной сети.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="4">
                <Accordion.Header>5. Восстановление текста.</Accordion.Header>
                <Accordion.Body>
                  Восстановление корректного текста на основе созданного словаря соответствий.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="5">
                <Accordion.Header>6. Постпроцессинг текста.</Accordion.Header>
                <Accordion.Body>
                  Исправление ошибок распознавания полученных в результате работы нейронной сети.
                </Accordion.Body>
              </Accordion.Item>
              <Accordion.Item eventKey="6">
                <Accordion.Header>7. (Опционально) Формирование нового PDF-документа с копируемым текстом.</Accordion.Header>
                <Accordion.Body>
                  Вшивание CMAP-таблиц для шрифтов позволяющей копировать текст корректно.
                </Accordion.Body>
              </Accordion.Item>
            </Accordion>
          </div>
          <div className="col-lg-6">
            <div className="p-4">
              <h4 className="fw-bold mb-3">Технические детали:</h4>
              <p>Мы не используем OCR — вместо этого декодируем внутренние данные PDF, включая:</p>
              <ul>
                <li>CMAP-таблицы для нестандартных шрифтов</li>
                <li>Потоки шрифтов любого формата</li>
                <li>Встроенные кодировки символов</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}