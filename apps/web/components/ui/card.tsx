import { type HTMLAttributes } from "react";
export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) { return <div className={`rounded-xl border border-white/10 bg-[#151515] ${className}`} {...props} />; }
