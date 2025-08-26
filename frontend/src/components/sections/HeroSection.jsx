import { Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';

export default function HeroSection() {
  return (
    <section class="hero-section">
        <div class="container text-center">
            <h1 class="display-4 fw-bold mb-4">Точное извлечение текста из сложных PDF</h1>
            <p class="lead mb-5">Ваш PDF останется исходным — мы только достанем из него текст, даже если другие OCR не видят его</p>
            <div class="d-grid gap-2 d-sm-flex justify-content-sm-center">
                <Button as={Link} to="/extract" variant="primary" size="lg" className="px-4 me-sm-3">Попробовать</Button>
            </div>
        </div>
    </section>
  );
}