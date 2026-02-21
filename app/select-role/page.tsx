import Link from 'next/link';
import { 
  Server, 
  Cpu, 
  ArrowLeft, 
  ShieldCheck, 
  LockKeyhole 
} from 'lucide-react';

export default function SelectRole() {
  return (
    <main className="relative min-h-screen bg-[#05020A] text-white flex flex-col items-center justify-center p-6 overflow-hidden selection:bg-purple-500 selection:text-white">
      
      {/* AMBIENT BACKGROUND GLOWS */}
      <div className="fixed inset-0 z-0 pointer-events-none">
         <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:32px_32px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
         <div className="absolute top-1/2 left-1/4 w-[600px] h-[600px] bg-purple-600/10 rounded-full blur-[120px] -translate-y-1/2" />
         <div className="absolute top-1/2 right-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[120px] -translate-y-1/2" />
      </div>

      <div className="relative z-10 w-full max-w-5xl mx-auto">
        
        {/* Back Navigation */}
        <Link href="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-12 group">
          <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium text-sm">Return to Hub</span>
        </Link>

        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-4">
            Initialize <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-indigo-400">Network Node</span>
          </h1>
          <p className="text-gray-400 text-lg max-w-xl mx-auto">
            Select your operational role in the federated network. Ensure you have the appropriate access credentials before proceeding.
          </p>
        </div>

        {/* Role Selection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* 1. SERVER ROLE */}
          <Link href="/" className="group relative bg-[#0A0510] rounded-3xl p-8 border border-white/5 hover:border-purple-500/50 transition-all duration-500 flex flex-col items-center text-center overflow-hidden h-full">
            {/* Hover Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="w-20 h-20 bg-purple-500/10 rounded-2xl flex items-center justify-center mb-6 border border-purple-500/20 group-hover:scale-110 transition-transform duration-500 shadow-[0_0_30px_-10px_rgba(168,85,247,0.3)]">
              <Server size={40} className="text-purple-400" />
            </div>
            
            <h2 className="text-2xl font-bold text-white mb-3">Central Aggregator</h2>
            <div className="flex items-center justify-center gap-2 text-xs font-mono text-purple-300 bg-purple-500/10 px-3 py-1 rounded-full mb-6 border border-purple-500/20">
              <ShieldCheck size={14} /> Robust Aggregation Engine
            </div>
            
            <p className="text-gray-400 leading-relaxed mb-8 flex-grow">
              Host the global model. Handle asynchronous gradient pushes from clients, apply Byzantine fault-tolerant aggregation (Trimmed Mean/Median), and distribute updated weights.
            </p>

            <div className="mt-auto w-full py-3 rounded-xl bg-white/5 group-hover:bg-purple-600 text-white font-bold transition-colors duration-300">
              Deploy Server Node
            </div>
          </Link>

          {/* 2. CLIENT ROLE */}
          <Link href="/" className="group relative bg-[#0A0510] rounded-3xl p-8 border border-white/5 hover:border-indigo-500/50 transition-all duration-500 flex flex-col items-center text-center overflow-hidden h-full">
            {/* Hover Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-bl from-indigo-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="w-20 h-20 bg-indigo-500/10 rounded-2xl flex items-center justify-center mb-6 border border-indigo-500/20 group-hover:scale-110 transition-transform duration-500 shadow-[0_0_30px_-10px_rgba(99,102,241,0.3)]">
              <Cpu size={40} className="text-indigo-400" />
            </div>
            
            <h2 className="text-2xl font-bold text-white mb-3">Edge Client</h2>
            <div className="flex items-center justify-center gap-2 text-xs font-mono text-indigo-300 bg-indigo-500/10 px-3 py-1 rounded-full mb-6 border border-indigo-500/20">
              <LockKeyhole size={14} /> Privacy-Preserving Execution
            </div>
            
            <p className="text-gray-400 leading-relaxed mb-8 flex-grow">
              Connect to the network as a data owner. Train the model locally on your private heterogeneous dataset and asynchronously push secure gradients to the global server.
            </p>

            <div className="mt-auto w-full py-3 rounded-xl bg-white/5 group-hover:bg-indigo-600 text-white font-bold transition-colors duration-300">
              Initialize Local Training
            </div>
          </Link>

        </div>
      </div>
    </main>
  );
}