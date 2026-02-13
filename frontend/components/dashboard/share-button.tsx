"use client";
import { useState } from "react";
import { Share2, Check, Copy, Mail, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ShareButtonProps {
  title: string;
  content?: string;
  className?: string;
}

export function ShareButton({ title, content, className }: ShareButtonProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const shareText = content || `${title} — BIAL Operations Dashboard`;

  async function copyToClipboard() {
    try {
      await navigator.clipboard.writeText(shareText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for environments where clipboard API is unavailable
    }
  }

  function shareViaEmail() {
    const subject = encodeURIComponent(title);
    const body = encodeURIComponent(shareText);
    window.open(`mailto:?subject=${subject}&body=${body}`, "_blank");
    setOpen(false);
  }

  return (
    <div className="relative">
      <Button variant="outline" size="sm" onClick={() => setOpen(!open)} className={cn("gap-2", className)}>
        <Share2 className="h-4 w-4" />
        Share
      </Button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute right-0 top-full mt-2 z-50 w-48 rounded-lg border border-border bg-card p-2 shadow-lg space-y-1">
            <button onClick={copyToClipboard} className="flex items-center gap-2 w-full rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors">
              {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
              {copied ? "Copied!" : "Copy to clipboard"}
            </button>
            <button onClick={shareViaEmail} className="flex items-center gap-2 w-full rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors">
              <Mail className="h-4 w-4" />
              Share via Email
            </button>
          </div>
        </>
      )}
    </div>
  );
}
