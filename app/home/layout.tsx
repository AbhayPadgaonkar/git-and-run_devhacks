import Header from "../header/header";

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="bg-linear-30 from-10% to from-violet-100 to-violet-200 min-h-screen max-w-full pt-16">
      <Header />

      {/* Content wrapper with z-10 so it sits above the grid */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </main>
  );
}