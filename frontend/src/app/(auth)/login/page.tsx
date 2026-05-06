"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { authClient } from "@/lib/auth-client";

type Step = "email" | "otp";

export default function LoginPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSendCode(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const { error } = await authClient.emailOtp.sendVerificationOtp({
        email,
        type: "sign-in",
      });
      if (error) {
        toast.error(error.message ?? "Failed to send code.");
        return;
      }
      setStep("otp");
      toast.success("Code sent — check your inbox.");
    } catch {
      toast.error("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const { error } = await authClient.signIn.emailOtp({
        email,
        otp,
      });
      if (error) {
        toast.error(error.message ?? "Invalid or expired code.");
        return;
      }
      router.push("/");
      router.refresh();
    } catch {
      toast.error("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f8f7f4] px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-10 flex items-center gap-2">
          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[#e85d4a]">
            <span className="text-xs font-bold text-white">G</span>
          </div>
          <span className="text-sm font-bold tracking-tight">GrowthOp</span>
        </div>

        {step === "email" ? (
          <>
            <h1 className="mb-1 text-2xl font-bold tracking-tight">
              welcome back
            </h1>
            <p className="mb-8 font-mono text-sm text-neutral-400">
              @JamieOgundiran · ai content agent
            </p>

            <form onSubmit={handleSendCode} className="flex flex-col gap-3">
              <div>
                <label className="mb-1.5 block font-mono text-xs tracking-widest text-neutral-400 uppercase">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="jamie@example.com"
                  required
                  autoFocus
                  className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-sm transition-colors placeholder:text-neutral-300 focus:border-neutral-400 focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !email}
                className="mt-1 w-full rounded-lg bg-black py-2.5 text-sm font-medium text-white transition-colors hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "sending..." : "send code"}
              </button>
            </form>
          </>
        ) : (
          <>
            <h1 className="mb-1 text-2xl font-bold tracking-tight">
              check your email
            </h1>
            <p className="mb-8 font-mono text-sm text-neutral-400">
              code sent to {email}
            </p>

            <form onSubmit={handleVerifyOtp} className="flex flex-col gap-3">
              <div>
                <label className="mb-1.5 block font-mono text-xs tracking-widest text-neutral-400 uppercase">
                  Code
                </label>
                <input
                  type="text"
                  value={otp}
                  onChange={(e) =>
                    setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
                  }
                  placeholder="000000"
                  required
                  autoFocus
                  inputMode="numeric"
                  maxLength={6}
                  className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2.5 text-center text-sm tracking-[0.4em] transition-colors placeholder:text-neutral-300 focus:border-neutral-400 focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={loading || otp.length < 6}
                className="mt-1 w-full rounded-lg bg-black py-2.5 text-sm font-medium text-white transition-colors hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? "verifying..." : "sign in"}
              </button>
            </form>

            <div className="my-5 flex items-center gap-3">
              <div className="flex-1 border-t border-neutral-200" />
              <span className="font-mono text-xs text-neutral-300">or</span>
              <div className="flex-1 border-t border-neutral-200" />
            </div>

            <p className="text-center text-sm text-neutral-400">
              wrong email?{" "}
              <button
                onClick={() => {
                  setStep("email");
                  setOtp("");
                }}
                className="font-medium text-black underline-offset-2 transition-all hover:underline"
              >
                go back
              </button>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
