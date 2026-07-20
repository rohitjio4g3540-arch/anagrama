"use client";

import { AnimatePresence, motion } from "framer-motion";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { KnowledgeGraph } from "../components/knowledge-graph";

const navigation = ["Home", "Knowledge", "Projects", "Research", "Studio", "Graph", "Library"];
const sources = [
  { kind: "PDF", title: "The architecture of attention", meta: "Research note · 18 min", color: "#e0a46c" },
  { kind: "NOTE", title: "Friction is an interface", meta: "Studio · yesterday", color: "#c7f36b" },
  { kind: "WEB", title: "Computing as a medium", meta: "Saved link · 3 sources", color: "#7aa9ef" },
];
const agenda = [
  ["Reframe the research question", "The design system project", "Today"],
  ["Connect field notes to synthesis", "Urban listening", "Tomorrow"],
  ["Review open contradictions", "Sensemaking", "Fri"],
];
const pulseBars = [28, 42, 30, 68, 50, 76, 62, 92, 73, 100, 86, 96];

const container = { hidden: { opacity: 1 }, show: { opacity: 1, transition: { staggerChildren: 0.09, delayChildren: 0.05 } } };
const item = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.16, 1, 0.3, 1] as const } } };

function Logo() {
  return (
    <div className="flex items-center gap-2.5 font-semibold tracking-[-.04em]">
      <span className="grid h-7 w-7 shrink-0 place-items-center overflow-hidden rounded-md bg-white p-1">
        <svg viewBox="0 0 512 512" className="h-full w-full" aria-label="Anagrama">
          <polygon points="256,54 468,430 44,430" fill="none" stroke="#111111" strokeWidth="44" strokeLinejoin="round" strokeLinecap="round" />
          <path d="M238,232 a62,62 0 1,0 124,0 a62,62 0 1,0 -124,0" fill="none" stroke="#111111" strokeWidth="32" />
          <rect x="252" y="228" width="34" height="176" rx="16" fill="#111111" />
          <polygon points="150,300 176,346 124,346" fill="#111111" />
          <polygon points="118,366 180,366 160,396 98,396" fill="#111111" />
        </svg>
      </span>
      <span className="text-[19px] tracking-[-.01em]" style={{ fontFamily: "var(--font-wordmark)", fontWeight: 600, fontVariationSettings: '"SOFT" 60, "opsz" 60' }}>anagrama</span>
    </div>
  );
}
function Mark({ label, tone = "muted" }: { label: string; tone?: "muted" | "lime" | "blue" }) {
  const tones = { muted: "bg-white/8 text-white/55", lime: "bg-[#c7f36b]/12 text-[#c7f36b]", blue: "bg-[#799eef]/12 text-[#a9c1ff]" };
  return <span className={`rounded-md px-2 py-1 text-[10px] font-medium tracking-[.08em] ${tones[tone]}`}>{label}</span>;
}
function AnimatedNumber({ value, prefix = "" }: { value: number; prefix?: string }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const duration = 1000;
    function tick(now: number) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setDisplay(Math.round(eased * value));
      if (t < 1) raf = requestAnimationFrame(tick);
    }
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <>{prefix}{display}</>;
}
function ThinkingDots() {
  return (
    <span className="inline-flex items-center gap-1">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="h-1.5 w-1.5 rounded-full bg-[#c7f36b]"
          animate={{ y: [0, -4, 0], opacity: [0.4, 1, 0.4] }}
          transition={{ duration: 0.9, repeat: Infinity, ease: "easeInOut", delay: i * 0.15 }}
        />
      ))}
    </span>
  );
}

export default function Home() {
  const [active, setActive] = useState("Home");
  const [prompt, setPrompt] = useState("");
  const [thinking, setThinking] = useState(false);
  const [answer, setAnswer] = useState("");
  const [events, setEvents] = useState<string[]>(["Graph context loaded", "Memory: Design system project"]);
  const [commandOpen, setCommandOpen] = useState(false);
  const greeting = useMemo(() => new Date().getHours() < 12 ? "Good morning, Mira." : "Welcome back, Mira.", []);

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!prompt.trim() || thinking) return;
    const question = prompt.trim(); setPrompt(""); setThinking(true); setAnswer(""); setEvents(["Intent classified", "Retrieving graph context", "Searching knowledge memory"]);
    const fallback = "I found three useful paths through your knowledge: attention as architecture, friction as an intentional interface, and computation as a cultural medium. The strongest next move is to frame them as a single inquiry about how systems choreograph attention.";
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/stream`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: question, project_id: "design-system" }) });
      if (!response.ok || !response.body) throw new Error("offline");
      const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = "";
      while (true) { const { done, value } = await reader.read(); if (done) break; buffer += decoder.decode(value, { stream: true }); const lines = buffer.split("\n"); buffer = lines.pop() || ""; for (const line of lines) { if (!line.startsWith("data: ")) continue; const item = JSON.parse(line.slice(6)); if (item.type === "delta") setAnswer((current) => current + item.content); if (item.type === "tool") setEvents((current) => [...current, item.name]); } }
    } catch { for (const word of fallback.split(" ")) { await new Promise((resolve) => setTimeout(resolve, 13)); setAnswer((current) => current + (current ? " " : "") + word); } setEvents((current) => [...current, "Local knowledge workspace ready"]); }
    setThinking(false);
  }

  return <main className="noise min-h-screen bg-[#0c0c0c] text-[#edeae3]">
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-[224px] flex-col border-r border-white/10 bg-[#111111] p-4 lg:flex">
      <Logo />
      <div className="mt-9 space-y-1">{navigation.map((item) => <button key={item} onClick={() => setActive(item)} className={`relative flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-[13px] transition-colors ${active === item ? "text-white" : "text-white/45 hover:bg-white/5 hover:text-white/80"}`}>{active === item && <motion.span layoutId="nav-pill" className="absolute inset-0 rounded-lg bg-white/9" transition={{ type: "spring", stiffness: 380, damping: 32 }} />}<span className={`relative z-10 h-1.5 w-1.5 rounded-full ${active === item ? "bg-[#c7f36b]" : "bg-white/20"}`} /><span className="relative z-10">{item}</span></button>)}</div>
      <div className="mt-auto border-t border-white/10 pt-4"><button className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-[13px] text-white/45 hover:bg-white/5"><span className="rounded bg-white/10 px-1.5 py-0.5 text-[10px]">⌘K</span> Search everything</button><button className="mt-2 flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-[13px] text-white/45 hover:bg-white/5"><span className="h-5 w-5 rounded-full bg-gradient-to-br from-[#c7f36b] to-[#6d8f36]" /> Mira Chen</button></div>
    </aside>

    <div className="lg:pl-[224px]">
      <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/10 bg-[#0c0c0c]/85 px-5 backdrop-blur-xl md:px-8"><div className="flex items-center gap-3 lg:hidden"><Logo /></div><div className="hidden text-[12px] text-white/40 lg:block"><span className="text-white/70">{active}</span> <span className="mx-1">/</span> Your space</div><div className="ml-auto flex items-center gap-3"><button onClick={() => setCommandOpen(true)} className="hidden items-center gap-8 rounded-lg border border-white/10 bg-white/[.03] px-3 py-1.5 text-xs text-white/40 transition hover:border-white/20 hover:text-white/60 md:flex">Search your universe <kbd className="text-[10px]">⌘ K</kbd></button><button className="grid h-8 w-8 place-items-center rounded-lg border border-white/10 text-white/55 transition hover:bg-white/5">?</button></div></header>

      <section className="mx-auto max-w-[1540px] px-5 pb-10 pt-8 md:px-8 md:pt-12">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-10 flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 text-[11px] font-medium uppercase tracking-[.18em] text-[#c7f36b]">Your thinking space</p><h1 className="text-3xl font-medium tracking-[-.055em] text-white md:text-[46px]">{greeting}</h1><p className="mt-2 text-sm text-white/43">Your knowledge is forming new connections.</p></div><motion.div whileTap={{ scale: 0.96 }}><Button onClick={() => setCommandOpen(true)} className="group border border-white/10 bg-white/7 text-white transition hover:bg-white/12"><span className="inline-block transition-transform duration-200 group-hover:rotate-90">+</span> Capture</Button></motion.div></motion.div>

        <motion.div variants={container} initial="hidden" animate="show" className="grid gap-4 xl:grid-cols-[minmax(0,1.24fr)_minmax(360px,.9fr)]">
          <div className="space-y-4">
            <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
              <Card className="relative overflow-hidden rounded-[26px] p-5 md:p-8"><div className="absolute -right-20 -top-24 h-64 w-64 rounded-full bg-[#c7f36b]/[.075] blur-3xl" /><div className="relative flex items-start justify-between"><div><Mark label="IN FOCUS" tone="lime" /><h2 className="mt-4 max-w-xl text-2xl font-medium leading-[1.1] tracking-[-.045em] md:text-[34px]">How do systems shape what people pay attention to?</h2><p className="mt-3 max-w-lg text-sm leading-6 text-white/48">A living inquiry across design, technology, and cultural practice.</p></div><button className="text-xl text-white/30 transition hover:text-white">•••</button></div><div className="relative mt-7 flex flex-wrap gap-2"><Mark label="24 sources" /><Mark label="18 concepts" /><Mark label="6 tensions" tone="blue" /></div><div className="relative mt-6 flex items-center justify-between border-t border-white/10 pt-4"><div className="flex -space-x-2">{[{ bg: "#d19f83", label: "MC" }, { bg: "#748fce", label: "AN" }].map((a) => <motion.span key={a.label} whileHover={{ scale: 1.18, zIndex: 10 }} style={{ backgroundColor: a.bg }} className="relative grid h-7 w-7 place-items-center rounded-full border-2 border-[#151515] text-[9px] text-black">{a.label}</motion.span>)}<motion.span whileHover={{ scale: 1.18, zIndex: 10 }} className="relative grid h-7 w-7 place-items-center rounded-full border-2 border-[#151515] bg-white/15 text-[10px]">+3</motion.span></div><button className="text-xs text-[#c7f36b] transition hover:text-white">Open inquiry →</button></div></Card>
            </motion.div>

            <div className="grid gap-4 md:grid-cols-[1.15fr_.85fr]">
              <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
                <Card className="rounded-2xl p-5"><div className="flex items-start justify-between"><div><p className="text-[11px] uppercase tracking-[.15em] text-white/38">Knowledge pulse</p><p className="mt-3 text-3xl tracking-[-.06em]"><AnimatedNumber value={12} prefix="+" /></p><p className="mt-1 text-xs text-white/45">new connections this week</p></div><motion.span animate={{ y: [0, -3, 0] }} transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }} className="text-[#c7f36b]">↗</motion.span></div><div className="mt-6 flex h-9 items-end gap-1">{pulseBars.map((height, index) => <motion.span key={index} initial={{ scaleY: 0 }} animate={{ scaleY: 1 }} transition={{ duration: 0.5, delay: 0.4 + index * 0.035, ease: "easeOut" }} style={{ height: `${height}%`, transformOrigin: "bottom" }} className="w-full rounded-sm bg-[#c7f36b]/[.55]" />)}</div></Card>
              </motion.div>
              <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
                <Card className="rounded-xl p-5"><p className="text-[11px] uppercase tracking-[.15em] text-white/38">Unresolved tension</p><p className="mt-3 text-lg leading-6 tracking-[-.025em]">Personalization can create relevance—and narrow discovery.</p><div className="mt-5 flex items-center gap-2"><motion.span animate={{ opacity: [1, 0.35, 1] }} transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }} className="h-2 w-2 rounded-full bg-[#e0a46c]" /><span className="text-xs text-white/45">Evidence is split</span></div></Card>
              </motion.div>
            </div>

            <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
              <Card className="rounded-2xl p-5 md:p-6"><div className="mb-5 flex items-center justify-between"><div><p className="text-[11px] uppercase tracking-[.15em] text-white/38">Recent activity</p><h3 className="mt-1 text-lg tracking-[-.035em]">The graph is evolving</h3></div><button className="text-xs text-white/40 transition hover:text-white">View all</button></div><div className="space-y-0">{sources.map((source, index) => <div key={source.title} className={`flex gap-3 border-t border-white/8 first:border-t-0 first:pt-0 ${index === 0 ? "py-4" : "py-3"}`}><span style={{ backgroundColor: source.color }} className={`mt-1.5 rounded-full ${index === 0 ? "h-2.5 w-2.5" : "h-2 w-2"}`} /><div className="min-w-0 flex-1"><div className="flex items-center justify-between gap-3"><p className={`truncate text-white/85 ${index === 0 ? "text-[15px]" : "text-sm"}`}>{source.title}</p><Mark label={source.kind} /></div><p className={`mt-1 text-white/36 ${index === 0 ? "text-xs" : "text-[11px]"}`}>{source.meta} · linked to <span className="text-white/65">attention economy</span></p></div></div>)}</div></Card>
            </motion.div>
          </div>

          <div className="space-y-4">
            <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
              <Card className="grid-bg overflow-hidden rounded-2xl"><div className="flex items-center justify-between border-b border-white/10 p-5"><div><p className="text-[11px] uppercase tracking-[.15em] text-white/38">Knowledge graph</p><h3 className="mt-1 text-lg tracking-[-.035em]">A map of your ideas</h3></div><button onClick={() => setActive("Graph")} className="rounded-lg border border-white/10 px-2.5 py-1.5 text-xs text-white/55 transition hover:bg-white/6">Explore</button></div><div className="relative h-[300px] overflow-hidden"><KnowledgeGraph /></div><div className="flex items-center gap-4 border-t border-white/10 px-5 py-3 text-[10px] text-white/40"><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-[#c7f36b]" />Concept</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-[#7aa9ef]" />Source</span><span><i className="mr-1 inline-block h-2 w-2 rounded-full bg-[#e0a46c]" />Question</span><span className="ml-auto text-white/25">hover or click a node</span></div></Card>
            </motion.div>
            <motion.div variants={item} whileHover={{ y: -3 }} transition={{ type: "spring", stiffness: 300, damping: 22 }}>
              <Card className="rounded-xl p-5"><div className="flex items-center justify-between"><div><p className="text-[11px] uppercase tracking-[.15em] text-white/38">Next actions</p><h3 className="mt-1 text-lg tracking-[-.035em]">Move thinking forward</h3></div><span className="text-sm text-white/35">03</span></div><div className="mt-4 space-y-1">{agenda.map(([task, project, when], index) => <button key={task} className="group flex w-full items-center gap-3 rounded-lg px-2 py-2.5 text-left transition hover:bg-white/5"><span className={`rounded border transition-colors group-hover:border-[#c7f36b] ${index === 0 ? "h-4.5 w-4.5 border-white/35" : "h-4 w-4 border-white/25"}`} /><span className="min-w-0 flex-1"><span className={`block truncate ${index === 0 ? "text-sm text-white/90 font-medium" : index === 1 ? "text-sm text-white/70" : "text-[13px] text-white/50"}`}>{task}</span><span className="block pt-0.5 text-[11px] text-white/35">{project}</span></span><span className="text-[11px] text-white/35">{when}</span></button>)}</div></Card>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 16, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.6, delay: 1.15, ease: [0.16, 1, 0.3, 1] }} whileHover={{ y: -3 }}>
              <motion.div animate={{ boxShadow: ["0 0 0 0 rgba(199,243,107,0)", "0 0 24px 2px rgba(199,243,107,.12)", "0 0 0 0 rgba(199,243,107,0)"] }} transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut" }} className="rounded-2xl">
                <Card className="rounded-2xl border-[#c7f36b]/20 bg-[#c7f36b]/[.045] p-5"><div className="flex gap-3"><motion.span animate={{ rotate: [0, 8, 0, -8, 0] }} transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }} className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-[#c7f36b] text-black">✦</motion.span><div><p className="text-sm font-medium">A pattern is emerging</p><p className="mt-1 text-xs leading-5 text-white/48">Six sources connect <span className="text-[#c7f36b]">friction</span> to meaningful participation. Want to see the synthesis?</p><button className="mt-3 text-xs text-[#c7f36b] transition hover:text-white">Show me →</button></div></div></Card>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>

        <motion.form onSubmit={ask} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.4 }} className="relative sticky bottom-4 z-10 mx-auto mt-6 max-w-4xl">
          {thinking && <motion.div aria-hidden animate={{ opacity: [0.5, 1, 0.5] }} transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }} className="absolute -inset-px rounded-2xl bg-gradient-to-r from-[#c7f36b]/40 via-[#7aa9ef]/30 to-[#c7f36b]/40 blur-[2px]" />}
          <div className="relative rounded-2xl border border-white/12 bg-[#1a1a1a]/95 p-2 shadow-2xl backdrop-blur-xl"><div className="flex items-end gap-2"><button type="button" className="mb-1 rounded-lg p-2 text-white/45 transition hover:bg-white/7 hover:text-white">+</button><textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); e.currentTarget.form?.requestSubmit(); } }} rows={1} placeholder="Ask across everything you know…" className="max-h-32 min-h-[38px] flex-1 resize-none bg-transparent py-2.5 text-sm outline-none placeholder:text-white/35" /><Button disabled={!prompt.trim() || thinking} className="mb-1 bg-[#c7f36b] text-black transition hover:bg-[#d7ff88] disabled:bg-white/10 disabled:text-white/30">{thinking ? <span className="inline-flex items-center gap-2">Thinking <ThinkingDots /></span> : <>Ask <span>↑</span></>}</Button></div>{(thinking || answer) && <div className="border-t border-white/8 px-3 pb-2 pt-3"><div className="mb-2 flex flex-wrap gap-2">{events.map((item) => <Mark key={item} label={item} tone={item.includes("graph") ? "lime" : "muted"} />)}</div><p className="whitespace-pre-wrap text-sm leading-6 text-white/75">{answer}{thinking && <span className="ml-1 inline-block h-3 w-1 animate-pulse bg-[#c7f36b]" />}</p></div>}</div>
        </motion.form>
      </section>
    </div>
    <AnimatePresence>{commandOpen && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setCommandOpen(false)} className="fixed inset-0 z-50 grid place-items-start bg-black/65 px-4 pt-[15vh] backdrop-blur-sm"><motion.div initial={{ y: -12, opacity: 0, scale: 0.98 }} animate={{ y: 0, opacity: 1, scale: 1 }} exit={{ y: -12, opacity: 0, scale: 0.98 }} transition={{ duration: 0.18 }} onClick={(event) => event.stopPropagation()} className="w-full max-w-xl overflow-hidden rounded-xl border border-white/15 bg-[#191919] shadow-2xl"><input autoFocus placeholder="Search knowledge, ask a question, or capture an idea…" className="w-full border-b border-white/10 bg-transparent px-5 py-4 text-sm outline-none placeholder:text-white/35" /><div className="p-2"><p className="px-3 py-2 text-[10px] font-medium uppercase tracking-[.15em] text-white/35">Quick actions</p>{["Ask Anagrama", "Capture a thought", "Explore your graph"].map((item, index) => <motion.button key={item} initial={{ opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.05 + index * 0.05 }} whileHover={{ x: 2 }} onClick={() => { setCommandOpen(false); if (index === 0) document.querySelector<HTMLTextAreaElement>("textarea")?.focus(); }} className="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm text-white/75 transition-colors hover:bg-white/7"><span>{item}</span><span className="text-xs text-white/30">↵</span></motion.button>)}</div></motion.div></motion.div>}</AnimatePresence>
  </main>;
}
