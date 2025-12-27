import React, { useState, useEffect, useRef } from 'react';
import {
  LayoutDashboard,
  Plus,
  GitBranch,
  Terminal,
  Play,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  Settings,
  FileCode,
  Layers,
  Box,
  Cpu,
  ShieldCheck,
  ChevronRight,
  Search,
  Menu,
  LogOut,
  Hammer,
  Rocket,
  Code,
  FileDiff,
  Activity,
  RefreshCw,
  Brain,
  MessageSquare,
  Save,
  ToggleLeft,
  ToggleRight,
  Globe,
  Database
} from 'lucide-react';

/** * MATRIX ARCHITECT // MISSION CONTROL
 * Builder/Executor service for the Matrix Ecosystem.
 */

// --- MOCK DATA ---

const MOCK_STATS = {
  active_jobs: 3,
  queue_depth: 12,
  success_rate: '98.5%',
  avg_build_time: '2m 14s',
  workers_online: 8
};

const MOCK_JOBS = [
  {
    id: 'job_992a',
    repo: 'matrix-org/payment-gateway',
    objective: 'Refactor Stripe integration to support v3 API',
    status: 'RUNNING',
    stage: 'VERIFY',
    started_at: '2m ago',
    branch: 'feat/stripe-v3-upgrade',
    progress: 65
  },
  {
    id: 'job_881b',
    repo: 'matrix-org/auth-service',
    objective: 'Patch security vulnerability in JWT handler',
    status: 'WAITING_APPROVAL',
    stage: 'GATE',
    started_at: '15m ago',
    branch: 'fix/jwt-overflow',
    progress: 40,
    guardian_risk: 85
  },
  {
    id: 'job_773c',
    repo: 'matrix-org/frontend-dashboard',
    objective: 'Deploy new analytics dashboard component',
    status: 'COMPLETED',
    stage: 'PUBLISH',
    started_at: '1h ago',
    branch: 'feat/analytics-dash',
    progress: 100
  },
  {
    id: 'job_664d',
    repo: 'matrix-org/legacy-api',
    objective: 'Migrate Python 3.8 to 3.11',
    status: 'FAILED',
    stage: 'PATCH',
    started_at: '3h ago',
    branch: 'chore/python-upgrade',
    progress: 25
  }
];

const MOCK_LOGS = [
  { time: '10:42:01', level: 'INFO', msg: 'Initializing sandbox environment...' },
  { time: '10:42:03', level: 'INFO', msg: 'Cloning repository matrix-org/payment-gateway...' },
  { time: '10:42:05', level: 'INFO', msg: 'Analyzing dependency tree...' },
  { time: '10:42:08', level: 'INFO', msg: 'Agent [Planner] identified 4 files for modification.' },
  { time: '10:42:12', level: 'INFO', msg: 'Generating patch set for Stripe v3 migration...' },
  { time: '10:42:15', level: 'INFO', msg: 'Applying patch to src/adapters/stripe.ts...' },
  { time: '10:42:16', level: 'WARN', msg: 'Deprecation warning detected in stripe.ts:142' },
  { time: '10:42:18', level: 'INFO', msg: 'Running verification suite...' },
];

const MOCK_DIFF = `
  import { Stripe } from 'stripe';

- const stripe = new Stripe(process.env.STRIPE_KEY, {
-   apiVersion: '2020-08-27',
- });
+ const stripe = new Stripe(process.env.STRIPE_KEY, {
+   apiVersion: '2023-10-16',
+   typescript: true,
+ });

  export const createCharge = async (amount: number, source: string) => {
-   return await stripe.charges.create({
-     amount,
-     currency: 'usd',
-     source,
-   });
+   return await stripe.paymentIntents.create({
+     amount,
+     currency: 'usd',
+     payment_method: source,
+     confirm: true,
+   });
  };
`;

// --- COMPONENTS ---

const StatusBadge = ({ status }) => {
  const styles = {
    RUNNING: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    COMPLETED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    FAILED: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    WAITING_APPROVAL: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    QUEUED: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
  };

  const icons = {
    RUNNING: <RefreshCw size={12} className="animate-spin" />,
    COMPLETED: <CheckCircle size={12} />,
    FAILED: <XCircle size={12} />,
    WAITING_APPROVAL: <ShieldCheck size={12} />,
    QUEUED: <Clock size={12} />
  };

  return (
    <span className={`px-2 py-1 rounded text-[10px] font-mono font-bold border flex items-center gap-2 w-fit ${styles[status]}`}>
      {icons[status]}
      {status.replace('_', ' ')}
    </span>
  );
};

const Card = ({ title, icon: Icon, children, className = '', action }) => (
  <div className={`bg-[#09090b] border border-white/10 rounded-xl overflow-hidden flex flex-col shadow-xl ${className}`}>
    {(title || Icon) && (
      <div className="px-4 py-3 border-b border-white/5 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-2">
          {Icon && <Icon size={16} className="text-indigo-400" />}
          <span className="text-xs font-bold text-zinc-300 uppercase tracking-widest">{title}</span>
        </div>
        {action}
      </div>
    )}
    <div className="p-4 flex-1 relative">{children}</div>
  </div>
);

const PipelineStep = ({ label, status, isActive }) => {
  const getStatusColor = () => {
    if (isActive) return 'border-indigo-500 text-indigo-400 bg-indigo-500/10 shadow-[0_0_15px_rgba(99,102,241,0.3)]';
    if (status === 'COMPLETED') return 'border-emerald-500/50 text-emerald-500 bg-emerald-500/5';
    if (status === 'FAILED') return 'border-rose-500/50 text-rose-500 bg-rose-500/5';
    if (status === 'WAITING') return 'border-amber-500/50 text-amber-500 bg-amber-500/5 animate-pulse';
    return 'border-zinc-800 text-zinc-600 bg-zinc-900';
  };

  return (
    <div className="flex flex-col items-center gap-2 z-10">
      <div className={`w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all duration-300 ${getStatusColor()}`}>
        {status === 'COMPLETED' ? <CheckCircle size={18} /> :
         status === 'FAILED' ? <XCircle size={18} /> :
         status === 'WAITING' ? <ShieldCheck size={18} /> :
         isActive ? <RefreshCw size={18} className="animate-spin" /> :
         <div className="w-2 h-2 rounded-full bg-current opacity-50" />}
      </div>
      <span className={`text-[10px] font-bold uppercase tracking-wider ${isActive ? 'text-white' : 'text-zinc-500'}`}>
        {label}
      </span>
    </div>
  );
};

// --- VIEWS ---

const DashboardView = ({ setActiveView }) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full auto-rows-min">
      {/* Overview Stats */}
      <div className="lg:col-span-4 grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Active Jobs', value: MOCK_STATS.active_jobs, icon: Activity, color: 'text-indigo-400' },
          { label: 'Queue Depth', value: MOCK_STATS.queue_depth, icon: Layers, color: 'text-zinc-400' },
          { label: 'Success Rate', value: MOCK_STATS.success_rate, icon: CheckCircle, color: 'text-emerald-400' },
          { label: 'Avg Build Time', value: MOCK_STATS.avg_build_time, icon: Clock, color: 'text-blue-400' },
          { label: 'Workers Online', value: MOCK_STATS.workers_online, icon: Cpu, color: 'text-amber-400' },
        ].map((stat, i) => (
          <div key={i} className="bg-zinc-900/50 border border-white/5 p-4 rounded-xl flex flex-col justify-between">
            <div className="flex justify-between items-start mb-2">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">{stat.label}</span>
              <stat.icon size={14} className={stat.color} />
            </div>
            <div className="text-2xl font-mono text-white">{stat.value}</div>
          </div>
        ))}
      </div>

      {/* Active Jobs List */}
      <Card title="Active Workloads" icon={Cpu} className="lg:col-span-3 min-h-[400px]">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-white/5 text-xs text-zinc-500 uppercase">
                <th className="p-4 font-bold">Job ID</th>
                <th className="p-4 font-bold">Target Repo</th>
                <th className="p-4 font-bold">Objective</th>
                <th className="p-4 font-bold">Stage</th>
                <th className="p-4 font-bold">Started</th>
                <th className="p-4 font-bold text-right">Status</th>
              </tr>
            </thead>
            <tbody className="text-sm divide-y divide-white/5">
              {MOCK_JOBS.map(job => (
                <tr
                  key={job.id}
                  onClick={() => setActiveView('job_detail')}
                  className="hover:bg-white/[0.02] transition-colors cursor-pointer group"
                >
                  <td className="p-4 font-mono text-indigo-400/80 group-hover:text-indigo-400">{job.id}</td>
                  <td className="p-4 font-medium text-white flex items-center gap-2">
                    <GitBranch size={14} className="text-zinc-600" />
                    {job.repo}
                  </td>
                  <td className="p-4 text-zinc-400 truncate max-w-xs">{job.objective}</td>
                  <td className="p-4">
                    <span className="text-xs font-mono text-zinc-300 bg-zinc-800 px-2 py-0.5 rounded border border-white/5">
                      {job.stage}
                    </span>
                  </td>
                  <td className="p-4 text-zinc-500 text-xs">{job.started_at}</td>
                  <td className="p-4 text-right">
                    <div className="flex justify-end">
                      <StatusBadge status={job.status} />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Actions */}
      <Card title="Architect Console" icon={Terminal} className="lg:col-span-1">
        <div className="flex flex-col gap-3">
          <button onClick={() => setActiveView('create_job')} className="flex items-center gap-3 p-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 transition-all shadow-lg shadow-indigo-500/20 group">
            <div className="p-2 bg-white/10 rounded-md">
              <Plus size={18} />
            </div>
            <div className="text-left">
              <div className="text-xs font-bold uppercase tracking-wider">New Build Plan</div>
              <div className="text-[10px] opacity-70 group-hover:opacity-100">Start a new architectural job</div>
            </div>
          </button>

          <div className="grid grid-cols-2 gap-3 mt-2">
            <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-lg bg-zinc-900 border border-white/5 hover:border-indigo-500/30 hover:bg-zinc-800 transition-all text-zinc-400 hover:text-white">
              <Hammer size={20} />
              <span className="text-[10px] font-bold uppercase">Fix Repo</span>
            </button>
            <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-lg bg-zinc-900 border border-white/5 hover:border-indigo-500/30 hover:bg-zinc-800 transition-all text-zinc-400 hover:text-white">
              <Box size={20} />
              <span className="text-[10px] font-bold uppercase">Create MCP</span>
            </button>
            <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-lg bg-zinc-900 border border-white/5 hover:border-indigo-500/30 hover:bg-zinc-800 transition-all text-zinc-400 hover:text-white">
              <Rocket size={20} />
              <span className="text-[10px] font-bold uppercase">Deploy</span>
            </button>
            <button className="flex flex-col items-center justify-center gap-2 p-4 rounded-lg bg-zinc-900 border border-white/5 hover:border-indigo-500/30 hover:bg-zinc-800 transition-all text-zinc-400 hover:text-white">
              <FileDiff size={20} />
              <span className="text-[10px] font-bold uppercase">Diff Check</span>
            </button>
          </div>

          <div className="mt-auto pt-4 border-t border-white/5">
             <div className="flex items-center justify-between text-xs text-zinc-500">
               <span>System Load</span>
               <span>34%</span>
             </div>
             <div className="w-full h-1 bg-zinc-800 rounded-full mt-2 overflow-hidden">
               <div className="h-full bg-indigo-500 w-[34%]" />
             </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

const JobDetailView = () => {
  const [activeTab, setActiveTab] = useState('logs');

  return (
    <div className="flex flex-col h-full gap-6">
      {/* Header */}
      <div className="flex justify-between items-start bg-zinc-900/50 p-6 rounded-xl border border-white/5 backdrop-blur-md">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-white font-mono">JOB_992A</h2>
            <StatusBadge status="RUNNING" />
          </div>
          <div className="flex items-center gap-4 text-sm text-zinc-400">
            <span className="flex items-center gap-1"><GitBranch size={14} /> matrix-org/payment-gateway</span>
            <span className="flex items-center gap-1"><Clock size={14} /> Started 2m ago</span>
            <span className="flex items-center gap-1"><Cpu size={14} /> Worker-04</span>
          </div>
          <p className="mt-4 text-sm text-zinc-300 max-w-2xl bg-black/30 p-3 rounded border border-white/5">
            Refactor Stripe integration to support v3 API. Ensure all payment intents are using the new confirm=true syntax.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-4 py-2 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-lg text-xs font-bold uppercase hover:bg-rose-500/20 transition-colors">Abort Job</button>
          <button className="px-4 py-2 bg-zinc-800 text-white border border-white/10 rounded-lg text-xs font-bold uppercase hover:bg-zinc-700 transition-colors">Download Artifacts</button>
        </div>
      </div>

      {/* Pipeline Visualization */}
      <div className="relative flex items-center justify-between px-16 py-8 bg-[#050505] rounded-xl border border-white/5 overflow-hidden">
         {/* Connector Line */}
         <div className="absolute top-1/2 left-20 right-20 h-0.5 bg-zinc-800 -z-0">
            <div className="h-full bg-indigo-500 w-[60%] animate-pulse" />
         </div>

         {/* Steps */}
         {['PLAN', 'PATCH', 'VERIFY', 'GATE', 'DEPLOY', 'PUBLISH'].map((step, i) => (
           <PipelineStep
             key={step}
             label={step}
             status={i < 2 ? 'COMPLETED' : i === 2 ? 'RUNNING' : 'PENDING'}
             isActive={i === 2}
           />
         ))}
      </div>

      {/* Details Pane */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Left: Console/Diff */}
        <Card className="lg:col-span-2 flex flex-col overflow-hidden">
          <div className="flex border-b border-white/10">
            <button
              onClick={() => setActiveTab('logs')}
              className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors ${activeTab === 'logs' ? 'border-indigo-500 text-white bg-white/5' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Live Logs
            </button>
            <button
              onClick={() => setActiveTab('diff')}
              className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors ${activeTab === 'diff' ? 'border-indigo-500 text-white bg-white/5' : 'border-transparent text-zinc-500 hover:text-zinc-300'}`}
            >
              Patch Diff
            </button>
          </div>

          <div className="flex-1 bg-black p-4 font-mono text-xs overflow-y-auto">
            {activeTab === 'logs' ? (
              <div className="space-y-2">
                {MOCK_LOGS.map((log, i) => (
                  <div key={i} className="flex gap-3">
                    <span className="text-zinc-600 shrink-0">{log.time}</span>
                    <span className={`shrink-0 w-12 font-bold ${log.level === 'INFO' ? 'text-indigo-400' : 'text-amber-400'}`}>{log.level}</span>
                    <span className="text-zinc-300">{log.msg}</span>
                  </div>
                ))}
                <div className="animate-pulse text-indigo-500">_</div>
              </div>
            ) : (
              <div className="text-zinc-400 whitespace-pre overflow-x-auto leading-relaxed">
                {MOCK_DIFF.split('\n').map((line, i) => (
                  <div key={i} className={`${line.startsWith('+') ? 'bg-emerald-500/10 text-emerald-400' : line.startsWith('-') ? 'bg-rose-500/10 text-rose-400' : ''}`}>
                    <span className="text-zinc-700 w-8 inline-block select-none">{i+1}</span>
                    {line}
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Right: Context & Artifacts */}
        <div className="flex flex-col gap-6">
          <Card title="Agent Reasoning" icon={Brain}>
             <div className="text-sm text-zinc-400 space-y-4">
                <p>The Planner Agent analyzed the codebase and detected <span className="text-white">stripe v2</span> usage. This requires a migration to PaymentIntents.</p>
                <div className="bg-zinc-900 p-3 rounded border border-white/5">
                   <div className="text-[10px] text-zinc-500 uppercase font-bold mb-1">Constraints Applied</div>
                   <ul className="list-disc list-inside text-xs space-y-1">
                      <li>TypeScript strict mode</li>
                      <li>No breaking changes to public API</li>
                      <li>Must pass existing test suite</li>
                   </ul>
                </div>
             </div>
          </Card>

          <Card title="Artifacts" icon={Box}>
             <div className="space-y-2">
                <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-colors cursor-pointer group">
                   <div className="flex items-center gap-2">
                      <FileCode size={14} className="text-indigo-400" />
                      <span className="text-xs text-zinc-300 group-hover:text-white">patch_v1.diff</span>
                   </div>
                   <span className="text-[10px] text-zinc-500">12KB</span>
                </div>
                <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded transition-colors cursor-pointer group">
                   <div className="flex items-center gap-2">
                      <Terminal size={14} className="text-zinc-400" />
                      <span className="text-xs text-zinc-300 group-hover:text-white">build_logs.txt</span>
                   </div>
                   <span className="text-[10px] text-zinc-500">450KB</span>
                </div>
             </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

const CreateJobView = () => (
  <div className="max-w-3xl mx-auto py-10">
    <h2 className="text-3xl font-bold text-white mb-2">Create Build Job</h2>
    <p className="text-zinc-400 mb-8">Define a high-level objective for Matrix Architect. The system will plan, patch, and deploy safely.</p>

    <Card className="space-y-6">
      <div>
        <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Target Repository</label>
        <div className="flex gap-2">
           <div className="flex items-center px-3 bg-zinc-900 border border-white/10 rounded-lg text-zinc-500">
              <GitBranch size={16} />
           </div>
           <input type="text" className="flex-1 bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none" placeholder="e.g. matrix-org/backend-service" />
        </div>
      </div>

      <div>
        <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Objective</label>
        <textarea className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none h-32" placeholder="Describe what needs to be done (e.g. 'Upgrade to Node 18 and fix linting errors')..." />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
           <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Constraint Profile</label>
           <select className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none">
              <option>Standard (Safe)</option>
              <option>Aggressive Refactor</option>
              <option>Security Hardening</option>
           </select>
        </div>
        <div>
           <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Target Environment</label>
           <select className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none">
              <option>Staging</option>
              <option>Production</option>
              <option>Ephemeral Sandbox</option>
           </select>
        </div>
      </div>

      <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-4 flex items-start gap-3">
         <ShieldCheck className="text-indigo-400 shrink-0 mt-0.5" size={18} />
         <div>
            <div className="text-xs font-bold text-indigo-400 uppercase mb-1">Policy Preview</div>
            <p className="text-xs text-zinc-400">Based on the inputs, this job will require <span className="text-white">Guardian Approval</span> before deployment due to "Production" target selection.</p>
         </div>
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-white/5">
         <button className="px-6 py-2 rounded-lg text-xs font-bold text-zinc-400 hover:text-white transition-colors">Cancel</button>
         <button className="px-6 py-2 rounded-lg bg-indigo-600 text-white text-xs font-bold hover:bg-indigo-500 shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2">
            <Rocket size={14} /> Launch Job
         </button>
      </div>
    </Card>
  </div>
);

// --- ARCHITECT CHAT (NEURAL LINK) ---
const ArchitectChatView = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'ai', text: 'Matrix Architect Neural Interface connected. I am tracking 3 active build pipelines. How can I assist you with the construction process?' }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    const userMsg = { id: Date.now(), role: 'user', text: inputValue };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsTyping(true);

    setTimeout(() => {
      setIsTyping(false);
      const responses = [
        "I'm currently applying patches to the payment-gateway. Test coverage has increased by 12%.",
        "Autopilot has detected a dependency conflict in the legacy-api migration. I've paused the job for manual review.",
        "Deploying artifacts to the staging environment. All pre-flight checks passed.",
        "The build queue is optimal. Worker efficiency is at 98%.",
        "I've optimized the Dockerfile for the frontend-dashboard. Build times should decrease by approximately 40 seconds."
      ];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];

      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        text: randomResponse
      };
      setMessages(prev => [...prev, aiMsg]);
    }, 1500);
  };

  return (
    <Card title="Architect Neural Link" icon={MessageSquare} className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm ${
              msg.role === 'user'
                ? 'bg-indigo-600 text-white rounded-br-sm'
                : 'bg-zinc-800 text-zinc-200 border border-white/10 rounded-bl-sm'
            }`}>
              <div className="flex items-center gap-2 mb-1 opacity-60 text-[10px] font-bold uppercase tracking-wider">
                {msg.role === 'ai' ? <><Cpu size={12} /> Architect AI</> : 'Engineer'}
              </div>
              <div className="leading-relaxed">{msg.text}</div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
             <div className="bg-zinc-800 px-4 py-3 rounded-2xl rounded-bl-sm border border-white/10 flex items-center gap-2">
                <Activity size={14} className="text-indigo-500 animate-bounce" />
                <span className="text-xs text-zinc-500 font-mono">Calculating...</span>
             </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-zinc-900/50 border-t border-white/5">
        <div className="relative">
          <input
            type="text"
            className="w-full bg-black border border-white/10 rounded-xl py-3 pl-4 pr-12 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
            placeholder="Query system status..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
          />
          <button
            onClick={handleSendMessage}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 bg-indigo-500/10 text-indigo-400 rounded-lg hover:bg-indigo-500/20 transition-colors"
          >
            <Play size={16} />
          </button>
        </div>
      </div>
    </Card>
  );
};

// --- SETTINGS VIEW ---
const SettingsView = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl mx-auto">
      <Card title="System Configuration" icon={Settings}>
        <div className="space-y-6">
          <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Matrix Hub Endpoint</label>
            <div className="flex gap-2">
              <Globe size={18} className="text-zinc-600 mt-2" />
              <input type="text" className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none" defaultValue="https://hub.matrix.ai/api/v1" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">Guardian Policy Server</label>
            <div className="flex gap-2">
              <ShieldCheck size={18} className="text-zinc-600 mt-2" />
              <input type="text" className="w-full bg-black border border-white/10 rounded-lg p-3 text-sm text-white focus:border-indigo-500/50 outline-none" defaultValue="https://guardian.matrix.ai/policy" />
            </div>
          </div>

          <div className="pt-4 border-t border-white/5">
             <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-zinc-300">Auto-Approve Low Risk Jobs</span>
                <ToggleRight className="text-indigo-500 cursor-pointer" size={24} />
             </div>
             <div className="flex items-center justify-between mb-4">
                <span className="text-sm text-zinc-300">Verbose Logging</span>
                <ToggleLeft className="text-zinc-600 cursor-pointer" size={24} />
             </div>
             <div className="flex items-center justify-between">
                <span className="text-sm text-zinc-300">Sandbox Isolation Mode</span>
                <ToggleRight className="text-indigo-500 cursor-pointer" size={24} />
             </div>
          </div>
        </div>
      </Card>

      <Card title="Integration Secrets" icon={Database}>
        <div className="space-y-6">
           <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">GitHub Personal Access Token</label>
            <input type="password" value="ghp_xxxxxxxxxxxxxxxxxxxxxx" disabled className="w-full bg-zinc-900 border border-white/5 rounded-lg p-3 text-sm text-zinc-500" />
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase mb-2">OpenAI API Key (Planner)</label>
            <input type="password" value="sk-xxxxxxxxxxxxxxxxxxxxxx" disabled className="w-full bg-zinc-900 border border-white/5 rounded-lg p-3 text-sm text-zinc-500" />
          </div>
           <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-4 flex gap-3">
              <AlertTriangle className="text-amber-500 shrink-0" size={20} />
              <div className="text-xs text-amber-200/80">
                 Secrets are encrypted at rest using Vault. To rotate keys, please use the CLI tool <code>matrix-cli secrets rotate</code>.
              </div>
           </div>
        </div>
      </Card>

      <div className="lg:col-span-2 flex justify-end">
         <button className="flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold text-sm transition-all shadow-lg shadow-indigo-500/20">
            <Save size={16} /> Save Configuration
         </button>
      </div>
    </div>
  );
};

// --- MAIN LAYOUT ---

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const NAV_ITEMS = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'create_job', label: 'Plan Builder', icon: Plus },
    { id: 'chat', label: 'Architect Chat', icon: MessageSquare }, // New Item
    { id: 'jobs', label: 'Job History', icon: Layers },
    { id: 'approvals', label: 'Approvals', icon: ShieldCheck },
    { id: 'artifacts', label: 'Artifacts', icon: Box },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-black text-zinc-100 font-sans flex">
      {/* Sidebar */}
      <aside className="w-64 bg-zinc-950 border-r border-white/5 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-white/5 gap-3">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <Cpu size={20} className="text-white" />
          </div>
          <div>
             <div className="font-bold text-white tracking-wider text-sm">MATRIX<span className="text-zinc-500">ARCHITECT</span></div>
             <div className="text-[10px] text-zinc-600 font-mono">BUILDER CONSOLE</div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                activeView === item.id
                  ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                  : 'text-zinc-400 hover:bg-white/5 hover:text-white border border-transparent'
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-white/5">
           <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-xs font-bold text-white">
                 RM
              </div>
              <div className="flex-1">
                 <div className="text-xs font-bold text-white">Ruslan Magana</div>
                 <div className="text-[10px] text-zinc-500">Lead Engineer</div>
              </div>
              <LogOut size={14} className="text-zinc-500 hover:text-white cursor-pointer" />
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col h-screen overflow-hidden relative">
        {/* Background FX */}
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-5 pointer-events-none" />
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500/0 via-indigo-500/50 to-indigo-500/0 opacity-20 pointer-events-none" />

        {/* Top Bar */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-white/5 bg-zinc-950/50 backdrop-blur-md z-10">
           <div className="flex items-center gap-4 text-zinc-500 text-sm">
              <span>Matrix Ecosystem</span>
              <ChevronRight size={14} />
              <span className="text-white">Architect</span>
              {activeView !== 'dashboard' && (
                 <>
                   <ChevronRight size={14} />
                   <span className="text-white capitalize">{activeView.replace('_', ' ')}</span>
                 </>
              )}
           </div>

           <div className="flex items-center gap-4">
              <div className="relative">
                 <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                 <input type="text" placeholder="Search jobs..." className="bg-zinc-900 border border-white/10 rounded-full py-1.5 pl-9 pr-4 text-xs text-white focus:outline-none focus:border-indigo-500/50 w-64" />
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-zinc-500 bg-zinc-900 px-3 py-1.5 rounded-full border border-white/5">
                 <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                 SYSTEM ONLINE
              </div>
           </div>
        </header>

        {/* View Area */}
        <main className="flex-1 overflow-y-auto p-8 relative z-0">
           {activeView === 'dashboard' && <DashboardView setActiveView={setActiveView} />}
           {activeView === 'create_job' && <CreateJobView />}
           {activeView === 'job_detail' && <JobDetailView />}
           {activeView === 'chat' && <ArchitectChatView />}
           {activeView === 'settings' && <SettingsView />}

           {/* Placeholders for other views */}
           {['jobs', 'approvals', 'artifacts'].includes(activeView) && (
              <div className="flex flex-col items-center justify-center h-full text-zinc-600">
                 <Code size={48} className="mb-4 opacity-20" />
                 <h3 className="text-lg font-bold text-zinc-500">Module Under Construction</h3>
                 <p className="text-sm">This interface module is coming in Matrix Architect v2.0</p>
              </div>
           )}
        </main>
      </div>
    </div>
  );
}
