"use client";

import HomePremiumGrid from "./landing_page/page";
import ProjectMenu from "@/app/home/page"; // Adjust to where you saved the ProjectMenu code
import { useAuth } from "@/app/context/AuthContext";
import MainHeader from "./header/header";

export default function Home() {
  const { user } = useAuth();

  // The AuthContext handles the redirect, but we can prevent
  // the UI from flashing before the redirect happens.
  if (!user) return <HomePremiumGrid />;

  return (
    <div className="max-w-full min-h-screen">
      {/* You can now pass user data to components if needed */}
      {/* <HomePremiumGrid /> */}
      <MainHeader />

      <ProjectMenu />
    </div>
  );
}
