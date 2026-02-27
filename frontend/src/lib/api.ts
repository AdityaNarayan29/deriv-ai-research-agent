import type { SSEEvent } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function startInvestigation(
  targetName: string,
  targetContext: string,
  maxIterations: number,
  onEvent: (event: SSEEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/investigate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_name: targetName,
      target_context: targetContext,
      max_iterations: maxIterations,
    }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop()!; // keep incomplete chunk

    for (const part of parts) {
      if (!part.trim()) continue;

      let eventType = "message";
      let data = "";

      for (const line of part.split("\n")) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          data = line.slice(6);
        }
      }

      if (!data) continue;

      try {
        const parsed = JSON.parse(data);
        onEvent({ type: eventType, ...parsed } as SSEEvent);
      } catch {
        // skip malformed events
      }
    }
  }
}

export async function startDemoInvestigation(
  onEvent: (event: SSEEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE}/demo`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop()!;

    for (const part of parts) {
      if (!part.trim()) continue;

      let eventType = "message";
      let data = "";

      for (const line of part.split("\n")) {
        if (line.startsWith("event: ")) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith("data: ")) {
          data = line.slice(6);
        }
      }

      if (!data) continue;

      try {
        const parsed = JSON.parse(data);
        onEvent({ type: eventType, ...parsed } as SSEEvent);
      } catch {
        // skip malformed events
      }
    }
  }
}

export async function checkHealth(): Promise<{
  status: string;
  keys: Record<string, boolean>;
}> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}
