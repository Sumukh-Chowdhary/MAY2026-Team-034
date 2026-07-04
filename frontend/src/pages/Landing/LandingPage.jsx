import Navbar from "../../components/layout/Navbar";
import Footer from "../../components/layout/Footer";

import Hero from "./Hero";
import Stats from "./Stats";
import FeaturedClubs from "./FeaturedClubs";
import UpcomingEvents from "./UpcomingEvents";

function LandingPage() {
  return (
    <>
      <Navbar />
      <Hero />
      <Stats />
      <FeaturedClubs />
      <UpcomingEvents />
      <Footer />
    </>
  );
}

export default LandingPage;