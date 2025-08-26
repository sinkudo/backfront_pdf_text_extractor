import NavBar from '../components/ui/NavBar';
import Footer from '../components/ui/Footer';
import HeroSection from '../components/sections/HeroSection';
import FeaturesSection from '../components/sections/FeaturesSection';
import ExamplesSection from '../components/sections/ExamplesSection';
import HowItWorks from '../components/sections/HowItWorks';
import ComparisonSection from '../components/sections/ComparisonSection';
import DemoSection from '../components/sections/DemoSection';
import ResearchSection from '../components/sections/ResearchSection';
import '../assets/styles/landing.css';
export default function LandingPage() {
  return (
    <div className="landing-page">
      <NavBar />
      <HeroSection />
      <FeaturesSection />
      <ExamplesSection />
      <HowItWorks />
      <ComparisonSection />
      <DemoSection />
      <ResearchSection />
      <Footer />
    </div>
  );
}