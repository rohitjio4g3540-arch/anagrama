"use client";

import { AnimatePresence, motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useState, type MouseEvent as ReactMouseEvent } from "react";

type NodeType = "concept" | "source" | "question";
interface Node { id: string; x: number; y: number; r: number; type: NodeType; label: string; meta: string; }
interface Edge { from: string; to: string; }

const TYPE_COLOR: Record<NodeType, string> = { concept: "#c7f36b", source: "#7aa9ef", question: "#e0a46c" };

const NODES: Node[] = [
  { id: "attention", x: 210, y: 82, r: 9, type: "concept", label: "attention", meta: "18 sources · 6 tensions" },
  { id: "computing", x: 328, y: 126, r: 6, type: "concept", label: "computing as medium", meta: "8 sources · concept" },
  { id: "friction", x: 195, y: 215, r: 7, type: "concept", label: "friction", meta: "12 sources · concept" },
  { id: "arch", x: 86, y: 154, r: 5, type: "source", label: "The architecture of attention", meta: "PDF · research note" },
  { id: "medium", x: 429, y: 65, r: 5, type: "source", label: "Computing as a medium", meta: "Web · saved link" },
  { id: "interface", x: 395, y: 210, r: 5, type: "source", label: "Friction is an interface", meta: "Note · studio" },
  { id: "inquiry", x: 467, y: 151, r: 4, type: "question", label: "How systems shape attention", meta: "Open inquiry" },
];

const EDGES: Edge[] = [
  { from: "arch", to: "attention" },
  { from: "attention", to: "computing" },
  { from: "computing", to: "medium" },
  { from: "arch", to: "friction" },
  { from: "friction", to: "computing" },
  { from: "computing", to: "interface" },
  { from: "attention", to: "friction" },
  { from: "attention", to: "medium" },
  { from: "computing", to: "inquiry" },
  { from: "friction", to: "interface" },
];

const PULSES: [string, string][] = [["attention", "computing"], ["friction", "computing"]];

const nodeById = Object.fromEntries(NODES.map((n) => [n.id, n]));

export function KnowledgeGraph() {
  const [hovered, setHovered] = useState<string | null>(null);
  const [focused, setFocused] = useState<string | null>(null);
  const mx = useMotionValue(250);
  const my = useMotionValue(135);
  const sx = useSpring(mx, { stiffness: 55, damping: 18 });
  const sy = useSpring(my, { stiffness: 55, damping: 18 });
  const px = useTransform(sx, [0, 500], [5, -5]);
  const py = useTransform(sy, [0, 270], [3, -3]);
  const glowX = useTransform(sx, (v) => `${(v / 500) * 100}%`);
  const glowY = useTransform(sy, (v) => `${(v / 270) * 100}%`);

  const active = hovered ?? focused;
  const activeNode = active ? nodeById[active] : null;
  const activeEdgeKeys = new Set(EDGES.filter((e) => e.from === active || e.to === active).map((e) => `${e.from}-${e.to}`));
  const connected = new Set<string>();
  if (active) {
    connected.add(active);
    EDGES.forEach((e) => { if (e.from === active) connected.add(e.to); if (e.to === active) connected.add(e.from); });
  }

  function handleMove(event: ReactMouseEvent<SVGSVGElement>) {
    const rect = event.currentTarget.getBoundingClientRect();
    mx.set(((event.clientX - rect.left) / rect.width) * 500);
    my.set(((event.clientY - rect.top) / rect.height) * 270);
  }

  return (
    <div className="relative">
      <motion.div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300"
        style={{ opacity: active ? 1 : 0, background: `radial-gradient(180px circle at ${glowX} ${glowY}, rgba(199,243,107,.08), transparent 65%)` }}
      />
      <motion.svg
        viewBox="0 0 500 270"
        className="h-full w-full cursor-crosshair touch-none"
        onMouseMove={handleMove}
        onMouseLeave={() => setHovered(null)}
      >
        <motion.g style={{ x: px, y: py }}>
          {EDGES.map((edge, i) => {
            const a = nodeById[edge.from];
            const b = nodeById[edge.to];
            const key = `${edge.from}-${edge.to}`;
            const isActive = activeEdgeKeys.has(key);
            const dim = active !== null && !isActive;
            return (
              <motion.line
                key={key}
                x1={a.x}
                y1={a.y}
                x2={b.x}
                y2={b.y}
                stroke={isActive ? TYPE_COLOR[a.type] : "rgba(255,255,255,.18)"}
                initial={{ pathLength: 0, opacity: 0, strokeWidth: 1 }}
                animate={{ pathLength: 1, opacity: dim ? 0.15 : 1, strokeWidth: isActive ? 1.6 : 1 }}
                transition={{
                  pathLength: { duration: 1, delay: 0.1 + i * 0.05, ease: "easeInOut" },
                  opacity: { duration: 0.3 },
                  strokeWidth: { duration: 0.2 },
                }}
              />
            );
          })}

          {PULSES.map(([fromId, toId], i) => {
            const a = nodeById[fromId];
            const b = nodeById[toId];
            return (
              <motion.circle
                key={`${fromId}-${toId}-pulse`}
                r={2.2}
                fill={TYPE_COLOR[a.type]}
                initial={{ opacity: 0 }}
                animate={{ cx: [a.x, b.x], cy: [a.y, b.y], opacity: [0, 1, 1, 0] }}
                transition={{ duration: 2.2, repeat: Infinity, repeatDelay: 3.4 + i * 1.7, delay: 1.6 + i * 0.8, ease: "easeInOut" }}
                style={{ filter: `drop-shadow(0 0 3px ${TYPE_COLOR[a.type]})` }}
              />
            );
          })}

          {NODES.map((n, i) => {
            const isActive = active === n.id;
            const dim = active !== null && !connected.has(n.id);
            return (
              <motion.g
                key={n.id}
                animate={{ y: [0, -3, 0] }}
                transition={{ duration: 2.6 + (i % 3) * 0.6, repeat: Infinity, ease: "easeInOut", delay: i * 0.35 }}
                onMouseEnter={() => setHovered(n.id)}
                onClick={() => setFocused((f) => (f === n.id ? null : n.id))}
                className="cursor-pointer"
              >
                {isActive && (
                  <motion.circle
                    cx={n.x}
                    cy={n.y}
                    r={n.r}
                    fill="none"
                    stroke={TYPE_COLOR[n.type]}
                    strokeWidth={1}
                    initial={{ opacity: 0.6, scale: 1 }}
                    animate={{ opacity: [0.6, 0], scale: [1, 2.6] }}
                    transition={{ duration: 1.3, repeat: Infinity, ease: "easeOut" }}
                    style={{ transformOrigin: `${n.x}px ${n.y}px` }}
                  />
                )}
                <motion.circle
                  cx={n.x}
                  cy={n.y}
                  r={n.r}
                  fill={TYPE_COLOR[n.type]}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: dim ? 0.85 : isActive ? 1.45 : 1, opacity: dim ? 0.25 : 1 }}
                  transition={{ type: "spring", stiffness: 260, damping: 16, delay: 0.5 + i * 0.05 }}
                  whileHover={{ scale: 1.5 }}
                  whileTap={{ scale: 1.15 }}
                  style={{ transformOrigin: `${n.x}px ${n.y}px` }}
                />
              </motion.g>
            );
          })}
        </motion.g>
      </motion.svg>

      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: active && active !== "attention" ? 0 : 1, y: 0 }}
        transition={{ delay: 0.9, duration: 0.4 }}
        className="pointer-events-none absolute left-[37%] top-[23%] rounded bg-[#c7f36b] px-2 py-1 text-[10px] font-medium text-black"
      >
        attention
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: active && active !== "friction" ? 0 : 1, y: 0 }}
        transition={{ delay: 1.05, duration: 0.4 }}
        className="pointer-events-none absolute bottom-[14%] left-[33%] rounded bg-white/10 px-2 py-1 text-[10px] text-white/70"
      >
        friction
      </motion.div>

      <AnimatePresence>
        {activeNode && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.97 }}
            transition={{ duration: 0.2 }}
            className="pointer-events-none absolute bottom-3 left-3 max-w-[230px] rounded-lg border border-white/15 bg-[#111111]/95 px-3 py-2 shadow-2xl backdrop-blur"
          >
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: TYPE_COLOR[activeNode.type] }} />
              <p className="text-[11px] font-medium text-white">{activeNode.label}</p>
            </div>
            <p className="mt-1 text-[10px] text-white/45">{activeNode.meta}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
