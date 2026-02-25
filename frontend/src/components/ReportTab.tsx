"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  report: string;
}

export function ReportTab({ report }: Props) {
  if (!report) {
    return (
      <div className="rounded-lg border border-white/10 bg-white/5 p-8 text-center text-slate-400">
        No report generated.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-6">
      <div className="prose prose-invert max-w-none prose-headings:text-white prose-p:text-slate-300 prose-strong:text-white prose-li:text-slate-300 prose-a:text-indigo-400">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{report}</ReactMarkdown>
      </div>
    </div>
  );
}
