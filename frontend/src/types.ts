export interface Doc {
  id: number;
  filename: string;
  title: string;
  pages: number;
  size: number;
  chunks: number;
  created_at: string;
}

export interface Source {
  n: number;
  chunk_id: number;
  page: number; // 0-based
  score: number;
  text: string;
  used: boolean;
  cited: boolean;
}

export type Reason = "answered" | "low_similarity" | "model_declined";

export interface Answer {
  id: number;
  question: string;
  answer: string | null;
  answerable: boolean;
  reason: Reason;
  confidence: { level: "high" | "medium" | "low"; score: number; threshold: number };
  sources: Source[];
}
