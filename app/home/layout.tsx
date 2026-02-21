import Header from "../header/header";

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // Replaced the flat background with your premium theme background
    <main className="relative min-h-screen bg-background text-foreground overflow-x-hidden pt-16 selection:bg-primary/20 selection:text-primary">
      
      {/* ========================================================= */}
      {/* FULL-SCREEN ENTERPRISE GRID & GLOWS (Layout Level)          */}
      {/* ========================================================= */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
         {/* Continuous Architectural Grid */}
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
         
         {/* Top Primary Glow */}
         <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[120px] rounded-[100%] mix-blend-normal" />
         
         {/* Bottom Primary Glow */}
         <div className="absolute bottom-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[150px] rounded-[100%] mix-blend-normal" />
      </div>

      <Header />

      {/* Content wrapper with z-10 so it sits above the grid */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </main>
  );
}