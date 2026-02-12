"use client";
import { useState, useRef, useEffect } from "react";
import { useApi } from "@/hooks/use-api";
import { useStreaming } from "@/hooks/use-streaming";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { DEFAULT_REPORT_DATE } from "@/lib/constants";
import type { DemoPrompt, ChatMessage } from "@/lib/types";
import { Send, Bot, User, Sparkles, Trash2, Zap } from "lucide-react";
import ReactMarkdown from "react-markdown";

export default function ChatPage() {
  const date = DEFAULT_REPORT_DATE;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const { text: streamText, isStreaming, stream } = useStreaming();

  const { data: prompts } = useApi<{ prompts: DemoPrompt[] }>("/api/chat/demo-prompts");
  const { data: quickQueries } = useApi<{ queries: string[] }>("/api/chat/quick-queries");

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, streamText]);

  async function sendMessage(query: string) {
    if (!query.trim() || isStreaming) return;

    const userMsg: ChatMessage = { role: "user", content: query };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    const response = await stream(query, date, messages);
    if (response) {
      setMessages((prev) => [...prev, { role: "assistant", content: response }]);
    }
  }

  return (
    <div className="space-y-4 max-w-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">AI Insights Chat</h1>
          <p className="text-muted-foreground">Ask questions about airport operations</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-xs">GenAI Powered</Badge>
          {messages.length > 0 && (
            <Button variant="ghost" size="sm" onClick={() => setMessages([])}>
              <Trash2 className="h-4 w-4 mr-1" /> Clear
            </Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4" style={{ height: "calc(100vh - 200px)" }}>
        {/* Sidebar: Demo Prompts */}
        <div className="lg:col-span-1 space-y-3 overflow-y-auto">
          <Card>
            <CardContent className="p-4 space-y-2">
              <p className="text-xs font-medium flex items-center gap-1 mb-2">
                <Sparkles className="h-3 w-3" /> Demo Scenarios
              </p>
              {prompts?.prompts.map((p) => (
                <Button
                  key={p.key}
                  variant="outline"
                  size="sm"
                  className="w-full justify-start text-xs h-auto py-2 whitespace-normal text-left"
                  onClick={() => sendMessage(p.prompt)}
                  disabled={isStreaming}
                >
                  {p.label}
                </Button>
              ))}
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 space-y-2">
              <p className="text-xs font-medium flex items-center gap-1 mb-2">
                <Zap className="h-3 w-3" /> Quick Queries
              </p>
              {quickQueries?.queries.slice(0, 5).map((q, i) => (
                <Button
                  key={i}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start text-xs h-auto py-2 whitespace-normal text-left"
                  onClick={() => sendMessage(q)}
                  disabled={isStreaming}
                >
                  {q}
                </Button>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-3 flex flex-col min-h-0">
          <Card className="flex flex-col flex-1 min-h-0 overflow-hidden">
            {/* Messages - scrollable */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 min-h-0">
              <div className="space-y-4">
                {messages.length === 0 && !isStreaming && (
                  <div className="text-center py-16 space-y-4">
                    <Bot className="h-12 w-12 mx-auto text-muted-foreground" />
                    <div>
                      <p className="font-medium">Welcome to AI Insights</p>
                      <p className="text-sm text-muted-foreground mt-1">Ask about airport operations or use a demo scenario to get started.</p>
                    </div>
                    <div className="flex flex-wrap justify-center gap-2 mt-4">
                      {["Queue compliance analysis", "Security lane issues", "Customer sentiment"].map((q) => (
                        <Button key={q} variant="outline" size="sm" className="text-xs" onClick={() => sendMessage(q)}>
                          {q}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {messages.map((msg, i) => (
                  <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : ""}`}>
                    {msg.role === "assistant" && (
                      <div className="shrink-0 w-7 h-7 rounded-full bg-primary flex items-center justify-center">
                        <Bot className="h-4 w-4 text-primary-foreground" />
                      </div>
                    )}
                    <div className={`max-w-[80%] rounded-lg px-4 py-3 text-sm ${msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                      {msg.role === "assistant" ? (
                        <div className="chat-markdown">
                          <ReactMarkdown>{msg.content}</ReactMarkdown>
                        </div>
                      ) : (
                        <div className="whitespace-pre-wrap">{msg.content}</div>
                      )}
                    </div>
                    {msg.role === "user" && (
                      <div className="shrink-0 w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center">
                        <User className="h-4 w-4 text-white" />
                      </div>
                    )}
                  </div>
                ))}

                {/* Streaming response */}
                {isStreaming && (
                  <div className="flex gap-3">
                    <div className="shrink-0 w-7 h-7 rounded-full bg-primary flex items-center justify-center">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                    <div className="max-w-[80%] rounded-lg px-4 py-3 text-sm bg-muted">
                      <div className="chat-markdown">
                        <ReactMarkdown>{streamText}</ReactMarkdown>
                        <span className="inline-block w-2 h-4 bg-foreground animate-pulse ml-0.5" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Input - pinned at bottom */}
            <div className="shrink-0 p-4 border-t border-border">
              <form
                onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
                className="flex gap-2"
              >
                <Input
                  placeholder="Ask about airport operations..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={isStreaming}
                  className="flex-1"
                />
                <Button type="submit" disabled={isStreaming || !input.trim()} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </form>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
