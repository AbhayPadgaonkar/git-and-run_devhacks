import Link from 'next/link';
import { 
  Network, 
  ShieldCheck, 
  Activity, 
  ArrowRight,
  GitMerge,
  Lock,
  Cpu,
  Sparkles,
  ChevronRight,
  Fingerprint
} from 'lucide-react';

export default function HomePremiumGrid() {
  return (
    <main className="relative min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary/20 selection:text-primary font-sans flex flex-col items-center">
      
      {/* ========================================================= */}
      {/* FULL-SCREEN ENTERPRISE GRID & GLOWS                       */}
      {/* ========================================================= */}
      <div className="fixed inset-0 z-0 pointer-events-none flex justify-center">
         {/* 1. Continuous Architectural Grid (Bulletproof Hex) */}
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808025_1px,transparent_1px),linear-gradient(to_bottom,#80808025_1px,transparent_1px)] bg-[size:40px_40px]" />
         
         {/* 2. Top Primary Glow */}
         <div className="absolute top-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[120px] rounded-[100%] mix-blend-normal" />
         
         {/* 3. Bottom Primary Glow */}
         <div className="absolute bottom-[-10%] w-[80vw] h-[50vh] bg-primary/20 blur-[150px] rounded-[100%] mix-blend-normal" />
      </div>

      {/* ==================== FLOATING PILL NAVBAR ==================== */}
      <div className="w-full max-w-5xl px-6 pt-6 sticky top-0 z-50">
        <nav className="w-full bg-background/70 backdrop-blur-xl border border-border shadow-sm rounded-full flex items-center justify-between h-14 px-4 transition-all">
          <Link href="/" className="flex items-center gap-2 pl-2 group">
            <div className="bg-primary p-1.5 rounded-full text-primary-foreground shadow-sm group-hover:scale-105 transition-transform">
              <Network className="h-4 w-4" />
            </div>
            <span className="font-bold tracking-tight text-foreground">FederX</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
            <Link href="#features" className="hover:text-foreground transition-colors">Platform</Link>
            <Link href="#architecture" className="hover:text-foreground transition-colors">Architecture</Link>
            <Link href="#security" className="hover:text-foreground transition-colors">Security</Link>
          </div>
          
          <div className="flex items-center gap-3">
            <Link href="/login" className="hidden sm:block text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-4">
              Sign In
            </Link>
            {/* Shadcn Button */}
            <Link href="/deploy" className="inline-flex items-center justify-center rounded-full text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-5">
              Deploy <ArrowRight className="ml-1.5 h-4 w-4" />
            </Link>
          </div>
        </nav>
      </div>

      <div className="relative z-10 w-full max-w-6xl mx-auto px-6 flex flex-col items-center">
        
        {/* ==================== CENTERED MAJESTIC HERO ==================== */}
        <header className="w-full pt-32 pb-24 flex flex-col items-center text-center">
          
          {/* Shadcn Secondary Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/80 backdrop-blur-md px-3 py-1 text-xs font-semibold text-secondary-foreground mb-8 shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            Federated Aggregation Engine v2.0
            <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />
          </div>
          
          <h1 className="text-5xl md:text-7xl lg:text-[5.5rem] font-extrabold tracking-tighter leading-[1.05] text-foreground max-w-4xl mb-6">
            Train models locally. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-primary to-primary/50">
              Scale globally.
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl leading-relaxed mb-10">
            The enterprise control plane for decentralized AI. Harness edge compute with asynchronous updates and Byzantine fault tolerance—without exposing raw data.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
             <Link href="/authentication/signup" className="w-full sm:w-auto inline-flex items-center justify-center rounded-md text-base font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-foreground text-background shadow-lg hover:bg-foreground/90 h-12 px-8">
               Start Building
             </Link>
             <Link href="#architecture" className="w-full sm:w-auto inline-flex items-center justify-center rounded-md text-base font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-border bg-background/50 backdrop-blur-sm shadow-sm hover:bg-muted h-12 px-8 gap-2">
               Read Documentation
             </Link>
          </div>
        </header>

        {/* ==================== BENTO BOX FEATURES (SHADCN CARDS) ==================== */}
        <section id="features" className="w-full py-20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
            
            {/* Bento Item 1: Large Span */}
            <div className="md:col-span-2 rounded-2xl border border-border bg-card/80 backdrop-blur-md text-card-foreground shadow-sm p-8 flex flex-col justify-between relative overflow-hidden group">
              <div className="absolute right-0 top-0 w-64 h-64 bg-primary/5 rounded-full blur-[80px] pointer-events-none group-hover:bg-primary/10 transition-colors duration-500" />
              <div className="relative z-10">
                <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center border border-border text-primary mb-6">
                  <Activity size={24} />
                </div>
                <h3 className="text-2xl font-bold tracking-tight mb-2">Asynchronous Training</h3>
                <p className="text-muted-foreground max-w-md">
                  Stragglers no longer bottleneck your pipeline. Global weights update continuously as secure gradients arrive from edge devices.
                </p>
              </div>
            </div>

            {/* Bento Item 2: Square */}
            <div className="md:col-span-1 rounded-2xl border border-border bg-card/80 backdrop-blur-md text-card-foreground shadow-sm p-8 flex flex-col justify-between group hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center border border-border text-primary mb-6">
                <Fingerprint size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold tracking-tight mb-2">Absolute Privacy</h3>
                <p className="text-sm text-muted-foreground">
                  Raw data never leaves the edge. Only secure parameters hit the network.
                </p>
              </div>
            </div>

            {/* Bento Item 3: Square */}
            <div className="md:col-span-1 rounded-2xl border border-border bg-card/80 backdrop-blur-md text-card-foreground shadow-sm p-8 flex flex-col justify-between group hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center border border-border text-primary mb-6">
                <ShieldCheck size={24} />
              </div>
              <div>
                <h3 className="text-xl font-bold tracking-tight mb-2">Byzantine Tolerance</h3>
                <p className="text-sm text-muted-foreground">
                  Automatically quarantine and discard malicious data poisoning attacks.
                </p>
              </div>
            </div>

            {/* Bento Item 4: Large Span */}
            <div className="md:col-span-2 rounded-2xl border border-border bg-card/80 backdrop-blur-md text-card-foreground shadow-sm p-8 flex flex-col justify-between relative overflow-hidden group">
              <div className="absolute left-0 bottom-0 w-64 h-64 bg-primary/5 rounded-full blur-[80px] pointer-events-none group-hover:bg-primary/10 transition-colors duration-500" />
              <div className="relative z-10 flex flex-col h-full justify-between">
                <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center border border-border text-primary mb-6">
                  <GitMerge size={24} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold tracking-tight mb-2">Robust Aggregation</h3>
                  <p className="text-muted-foreground max-w-md">
                    Standard averaging fails on noisy data. Native support for robust statistical aggregators like Coordinate-wise Median and Trimmed Mean.
                  </p>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* ==================== CLEAN ARCHITECTURE PIPELINE ==================== */}
        <section id="architecture" className="w-full py-24 mb-20 border-t border-border mt-10">
          <div className="text-center mb-16">
             <h2 className="text-3xl font-bold tracking-tight text-foreground mb-4">Architecture Topology</h2>
             <p className="text-muted-foreground">A unified, secure loop connecting edge telemetry to central aggregation.</p>
          </div>
          
          <div className="flex flex-col md:flex-row justify-center items-center gap-4">
             
             {/* Edge Node */}
             <div className="w-56 p-6 rounded-2xl border border-border bg-card/80 backdrop-blur-md shadow-sm text-center relative z-10">
                <div className="mx-auto w-12 h-12 bg-secondary rounded-full flex items-center justify-center mb-4 border border-border text-foreground">
                  <Cpu size={20} />
                </div>
                <h4 className="font-bold text-foreground mb-1">Edge Device</h4>
                <p className="text-xs text-muted-foreground">Local Epochs</p>
             </div>

             {/* Connection Line */}
             <div className="hidden md:flex items-center text-muted-foreground w-16">
                <div className="h-px w-full bg-border"></div>
                <ArrowRight size={16} className="ml-[-8px] text-border" />
             </div>

             {/* Aggregator */}
             <div className="w-64 p-6 rounded-2xl border-2 border-primary/20 bg-primary/10 backdrop-blur-md shadow-lg text-center relative z-10">
                <div className="mx-auto w-12 h-12 bg-primary rounded-full flex items-center justify-center mb-4 text-primary-foreground shadow-md shadow-primary/20">
                  <Network size={20} />
                </div>
                <h4 className="font-bold text-foreground mb-1">Aggregator</h4>
                <p className="text-xs text-muted-foreground">Trimmed Mean</p>
             </div>

             {/* Connection Line */}
             <div className="hidden md:flex items-center text-muted-foreground w-16">
                <div className="h-px w-full bg-border"></div>
                <ArrowRight size={16} className="ml-[-8px] text-border" />
             </div>

             {/* Global Model */}
             <div className="w-56 p-6 rounded-2xl border border-border bg-card/80 backdrop-blur-md shadow-sm text-center relative z-10">
                <div className="mx-auto w-12 h-12 bg-secondary rounded-full flex items-center justify-center mb-4 border border-border text-foreground">
                  <Lock size={20} />
                </div>
                <h4 className="font-bold text-foreground mb-1">Global Model</h4>
                <p className="text-xs text-muted-foreground">Weight Broadcast</p>
             </div>

          </div>
        </section>

      </div>

      {/* ==================== MINIMAL FOOTER ==================== */}
      <footer className="w-full bg-muted/30 border-t border-border py-10 mt-auto relative z-10 backdrop-blur-md">
         <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
               <Network size={18} className="text-primary" />
               <span className="font-bold text-foreground tracking-tight">FederX</span>
            </div>
            <div className="text-sm text-muted-foreground font-medium">
               © 2026 FederX. Built with enterprise standards.
            </div>
         </div>
      </footer>

    </main>
  );
}