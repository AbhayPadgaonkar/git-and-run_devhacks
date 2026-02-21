import Header from "../header/header";

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="bg-linear-30 from-10% to from-violet-100 to-violet-200 min-h-screen max-w-full pt-16">
      <Header />

      {children}
    </main>
  );
}
