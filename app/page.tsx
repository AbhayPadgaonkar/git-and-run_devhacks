import Link from 'next/link';
import { 
  Network, 
  Shield, 
  Lock, 
  Activity, 
  Server, 
  GitMerge,
  ArrowRight,
  Play,
  Zap,
  Globe
} from 'lucide-react';

export default function HomeDark() {
  return (
    // 1. THEME: Deep Void Background
    <main className="relative min-h-screen bg-[#05020A] text-white overflow-x-hidden selection:bg-purple-500 selection:text-white">
      
      {/* 2. AMBIENT GRID & GLOWS */}
      <div className="fixed inset-0 z-0 pointer-events-none">
         {/* Grid Pattern */}
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
         
         {/* Spotlights */}
         <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-purple-600/20 rounded-full blur-[120px] mix-blend-screen animate-pulse" />
         <div className="absolute bottom-0 right-0 w-[800px] h-[600px] bg-indigo-600/10 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10">
        
        {/* ==================== NAVBAR (Dark Glass) ==================== */}
        <nav className="w-full bg-[#05020A]/70 backdrop-blur-xl sticky top-0 z-50 border-b border-white/5">
          <div className="mx-auto flex max-w-7xl items-center justify-between p-5 lg:px-8">
            <Link href="/" className="group flex items-center gap-3">
              <div className="p-2 bg-gradient-to-tr from-purple-600 to-indigo-600 rounded-lg shadow-lg shadow-purple-500/20">
                <Network className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-wide">FederX</span>
            </Link>
            
            <div className="hidden lg:flex lg:gap-x-10">
              <NavLink href="#features" text="Capabilities" />
              <NavLink href="#architecture" text="Architecture" />
              <NavLink href="#benchmarks" text="Benchmarks" />
            </div>
            
            <div className="flex items-center gap-6">
              <Link href="/login" className="text-sm font-medium text-gray-400 hover:text-white transition-colors">
                Log In
              </Link>
              <Link href="/deploy" className="group relative px-6 py-2.5 rounded-lg bg-white text-black font-bold text-sm overflow-hidden transition-all hover:scale-105">
                <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-indigo-300 via-purple-300 to-indigo-300 opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="relative z-10">Deploy Node</span>
              </Link>
            </div>
          </div>
        </nav>

        {/* ==================== HERO SECTION ==================== */}
        <div className="relative pt-24 pb-32 lg:pt-40 lg:pb-48 text-center px-6">
            
            {/* Announcement Chip */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-purple-300 text-xs font-medium tracking-wider mb-8 hover:bg-white/10 transition-colors cursor-default backdrop-blur-md">
               <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-500"></span>
               </span>
               Robust Aggregation Engine v1.0 Live
            </div>

            {/* Glowing Headline */}
            <h1 className="text-5xl lg:text-8xl font-black text-white tracking-tighter mb-8 leading-[1.1] drop-shadow-[0_0_60px_rgba(168,85,247,0.4)]">
              Decentralized AI. <br/>
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-fuchsia-300 to-indigo-400">Zero Data Compromise.</span>
            </h1>

            <p className="max-w-2xl mx-auto text-xl text-gray-400 mb-12 leading-relaxed">
              Collaboratively train machine learning models across diverse networks. 
              <span className="text-white"> Asynchronous updates. Byzantine fault tolerance. 100% private.</span>
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
               <Link href="/select-role" className="w-full sm:w-auto px-8 py-4 bg-purple-600 hover:bg-purple-500 text-white rounded-xl font-bold text-lg shadow-[0_0_40px_-10px_rgba(147,51,234,0.5)] transition-all flex items-center justify-center gap-2">
                 Select Client or Server <Zap size={20} className="fill-white" />
               </Link>
               <Link href="#architecture" className="w-full sm:w-auto px-8 py-4 bg-white/5 border border-white/10 text-white rounded-xl font-bold text-lg hover:bg-white/10 transition-all flex items-center justify-center gap-2 backdrop-blur-sm">
                 <Play size={18} /> View Convergence Demo
               </Link>
            </div>
        </div>

        {/* ==================== STATS STRIP ==================== */}
        <div className="w-full border-y border-white/10 bg-white/[0.02] backdrop-blur-sm">
           <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-8 py-10 px-6 text-center">
              {[
                 { label: "Active Nodes", val: "10k+" },
                 { label: "Data Kept Private", val: "100%" },
                 { label: "Byzantine Tolerance", val: "33%" },
                 { label: "Aggregations/sec", val: "50k" }
              ].map((stat, i) => (
                 <div key={i}>
                    <div className="text-3xl font-black text-white mb-1">{stat.val}</div>
                    <div className="text-xs font-bold text-gray-500 uppercase tracking-widest">{stat.label}</div>
                 </div>
              ))}
           </div>
        </div>

        {/* ==================== FEATURES GRID ==================== */}
        <div id="features" className="py-32 px-6">
           <div className="max-w-7xl mx-auto">
              <div className="mb-20">
                 <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Resilience <span className="text-purple-400">Built-In.</span></h2>
                 <p className="text-xl text-gray-400 max-w-xl">Designed to handle heterogeneous datasets, slow stragglers, and malicious actors.</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                 {/* Feature 1 */}
                 <div className="md:col-span-2 group relative bg-gradient-to-b from-white/10 to-transparent p-1px rounded-3xl overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"/>
                    <div className="relative h-full bg-[#0A0510] rounded-[23px] p-10 border border-white/5 flex flex-col md:flex-row items-center gap-8">
                       <div className="flex-1">
                          <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-6 border border-purple-500/30">
                             <Activity size={24} className="text-purple-400" />
                          </div>
                          <h3 className="text-2xl font-bold text-white mb-3">Asynchronous Client Updates</h3>
                          <p className="text-gray-400 leading-relaxed">
                             No more waiting for slow nodes. Our architecture allows the global model to update continuously as soon as individual clients push their encrypted gradients. <span className="text-white">Zero blocking, maximum throughput.</span>
                          </p>
                       </div>
                    </div>
                 </div>

                 {/* Feature 2 */}
                 <div className="md:col-span-1 group relative bg-white/5 rounded-3xl p-10 border border-white/5 hover:bg-white/10 transition-colors">
                     <div className="w-12 h-12 bg-indigo-500/20 rounded-lg flex items-center justify-center mb-6 border border-indigo-500/30">
                        <GitMerge size={24} className="text-indigo-400" />
                     </div>
                     <h3 className="text-2xl font-bold text-white mb-3">Robust Aggregation</h3>
                     <p className="text-gray-400">
                        Utilizing advanced statistical algorithms like Trimmed Mean and Coordinate-wise Median to filter out noise and stabilize convergence.
                     </p>
                 </div>

                 {/* Feature 3 */}
                 <div className="md:col-span-1 group relative bg-white/5 rounded-3xl p-10 border border-white/5 hover:bg-white/10 transition-colors">
                     <div className="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mb-6 border border-pink-500/30">
                        <Lock size={24} className="text-pink-400" />
                     </div>
                     <h3 className="text-2xl font-bold text-white mb-3">Privacy Preservation</h3>
                     <p className="text-gray-400">
                        Raw data never leaves the client device. Only securely aggregated parameter updates are transmitted to the global server.
                     </p>
                 </div>

                 {/* Feature 4 */}
                 <div className="md:col-span-2 group relative bg-white/5 rounded-3xl p-10 border border-white/5 hover:bg-white/10 transition-colors overflow-hidden">
                     {/* Decorative Elements */}
                     <div className="absolute right-0 top-0 w-64 h-64 bg-red-600/10 blur-[80px] rounded-full pointer-events-none"></div>
                     
                     <h3 className="text-2xl font-bold text-white mb-3 relative z-10">Malicious Node Mitigation</h3>
                     <p className="text-gray-400 max-w-lg relative z-10">
                        Built-in Byzantine Fault Tolerance automatically detects data poisoning attempts and excludes compromised gradients before they poison the global model.
                     </p>
                     
                     <div className="mt-8 flex gap-4 relative z-10">
                        <div className="px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-lg text-green-400 text-sm font-mono">
                           Node A: Trusted
                        </div>
                        <div className="px-4 py-2 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm font-mono">
                           Node B: Blocked (Poisoning Detected)
                        </div>
                     </div>
                 </div>
              </div>
           </div>
        </div>

        {/* ==================== HOW IT WORKS (Neon Steps) ==================== */}
        <div id="architecture" className="py-32 relative">
           <div className="max-w-7xl mx-auto px-6">
              <div className="text-center mb-20">
                 <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">Training Pipeline</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
                 {/* Glowing Line */}
                 <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-px bg-gradient-to-r from-transparent via-purple-500 to-transparent opacity-50"></div>

                 {[
                    { title: "Local Training", icon: Server, color: "text-blue-400", desc: "Data stays on edge devices" },
                    { title: "Async Push", icon: Globe, color: "text-purple-400", desc: "Transmit secure gradients" },
                    { title: "Global Aggregation", icon: Shield, color: "text-pink-400", desc: "Trimmed mean & model update" }
                 ].map((step, i) => (
                    <div key={i} className="relative z-10 flex flex-col items-center text-center group">
                       <div className="w-24 h-24 bg-[#0F0518] rounded-2xl border border-white/10 shadow-[0_0_30px_-10px_rgba(255,255,255,0.1)] flex items-center justify-center mb-8 group-hover:border-purple-500/50 group-hover:shadow-[0_0_30px_-5px_rgba(168,85,247,0.3)] transition-all duration-500">
                          <step.icon size={32} className={`${step.color}`} />
                       </div>
                       <h3 className="text-xl font-bold text-white mb-2">{step.title}</h3>
                       <p className="text-gray-500 text-sm font-mono">{step.desc}</p>
                    </div>
                 ))}
              </div>
           </div>
        </div>

        {/* ==================== FOOTER ==================== */}
        <footer className="border-t border-white/5 bg-black py-12">
           <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex items-center gap-2 opacity-80">
                 <Network size={20} className="text-purple-500" />
                 <span className="font-bold text-xl text-white">FederX</span>
              </div>
              <p className="text-gray-600 text-sm">© 2024 FederX. System Status: <span className="text-green-500">Operational</span></p>
           </div>
        </footer>

      </div>
    </main>
  );
}

// Nav Helper
function NavLink({ href, text }: { href: string; text: string }) {
  return (
    <a href={href} className="text-sm font-medium text-gray-400 transition-colors hover:text-white hover:shadow-[0_0_20px_rgba(255,255,255,0.3)]">
      {text}
    </a>
  );
}