"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export function GenerateMoreButton() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/api/ideas/generate`, { method: "POST" });
      router.refresh();
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button
      size="sm"
      className="bg-black text-xs text-white hover:bg-neutral-800"
      onClick={handleGenerate}
      disabled={loading}
    >
      {loading ? "generating..." : "+ generate more"}
    </Button>
  );
}
