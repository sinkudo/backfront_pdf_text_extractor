import { Carousel } from 'react-bootstrap';
import "../../assets/styles/ExamplesSection.css";
export default function ExamplesSection() {
  return (
    <>
      {/* Секция с заголовком */}
      <div className="container text-center mb-4" style={{ position: 'relative' }}>
        <div style={{
          background: 'linear-gradient(135deg, rgba(110,142,251,0.1) 0%, rgba(167,119,227,0.1) 100%)',
          padding: '2rem',
          borderRadius: '15px',
          border: '1px solid rgba(110,142,251,0.3)',
          boxShadow: '0 10px 20px rgba(0,0,0,0.05)',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Декоративные элементы */}
          <div style={{
            position: 'absolute',
            top: '-50px',
            right: '-50px',
            width: '200px',
            height: '200px',
            background: 'radial-gradient(circle, rgba(110,142,251,0.15) 0%, rgba(110,142,251,0) 70%)',
            borderRadius: '50%'
          }}></div>
          <div style={{
            position: 'absolute',
            bottom: '-30px',
            left: '-30px',
            width: '150px',
            height: '150px',
            background: 'radial-gradient(circle, rgba(167,119,227,0.15) 0%, rgba(167,119,227,0) 70%)',
            borderRadius: '50%'
          }}></div>
          
          {/* Заголовок и подзаголовок */}
          <h3 className="fw-bold mb-3" style={{ position: 'relative', zIndex: 1 }}>
            Примеры сложных PDF, которые мы обрабатываем
          </h3>
          <p className="lead" style={{ position: 'relative', zIndex: 1 }}>
            Даже документы с битой кодировкой, сложным фоном и нестандартными шрифтами
          </p>
        </div>
      </div>

      {/* Карусель с примерами */}
      <div className="container py-4">
        <Carousel indicators={false} interval={null}>
          <Carousel.Item>
            <img
              src={require('../../assets/images/pdf1.png')}
              className="d-block w-100 carousel-img-transparent"
              alt="Битая кодировка"
            />
          </Carousel.Item>
          <Carousel.Item>
            <img
              src={require('../../assets/images/pdf2.png')}
              className="d-block w-100 carousel-img-transparent"
              alt="Сложный фон"
            />
          </Carousel.Item>
          <Carousel.Item>
            <img
              src={require('../../assets/images/pdf3.png')}
              className="d-block w-100 carousel-img-transparent"
              alt="Type3 шрифты"
            />
          </Carousel.Item>
          <Carousel.Item>
            <img
              src={require('../../assets/images/pdf4.png')}
              className="d-block w-100 carousel-img-transparent"
              alt="Плазменные артефакты"
            />
          </Carousel.Item>
        </Carousel>
      </div>
    </>
  );
}