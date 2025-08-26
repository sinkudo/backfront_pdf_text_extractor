import { FaSearch, FaFilePdf, FaShieldAlt } from 'react-icons/fa';

export default function Features() {
  const features = [
    {
      icon: <FaSearch size={40} className="text-primary mb-3" />,
      title: "Анализ данных PDF",
      text: "Работаем с информацией, хранящейся в PDF-документе"
    },
    {
      icon: <FaFilePdf size={40} className="text-primary mb-3" />,
      title: "Сохранение структуры",
      text: "Генерируем новый PDF с сохранением оригинальной структуры"
    },
    {
      icon: <FaShieldAlt size={40} className="text-primary mb-3" />,
      title: "Без изменений PDF",
      text: "Исходный файл не трогаем, только читаем его данные"
    }
  ];

  return (
    <section id="features" className="py-5 bg-light">
      <div className="container">
        <div className="text-center mb-5">
          <h2 className="fw-bold">Почему наш подход уникален</h2>
          <p className="lead text-muted">Обычные OCR работают с PDF как с изображениями</p>
        </div>
        
        <div className="row g-4">
          {features.map((feature, index) => (
            <div key={index} className="col-md-4">
              <div className="text-center p-4 bg-white rounded shadow-sm">
                {feature.icon}
                <h3>{feature.title}</h3>
                <p className="text-muted">{feature.text}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}