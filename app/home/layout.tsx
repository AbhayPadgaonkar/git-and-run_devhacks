import Header from "../header/header";

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <main className="min-h-screen max-w-full pt-16">
      <Header />

      {children}
    </main>
  );
}
