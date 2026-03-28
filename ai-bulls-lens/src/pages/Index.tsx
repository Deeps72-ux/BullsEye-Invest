import { useEffect } from "react";

const Index = () => {
  useEffect(() => {
    // Initialize dark mode by default
    if (!localStorage.getItem("bullseye_theme")) {
      document.documentElement.classList.add("dark");
    }
  }, []);
  
  // This redirects handled by Dashboard route at "/"
  return null;
};

export default Index;
