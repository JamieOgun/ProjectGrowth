import { NextResponse } from "next/server";
import { getMigrations } from "better-auth/db/migration";
import { auth } from "@/lib/auth";

export async function GET() {
  const { runMigrations } = await getMigrations(auth.options);
  await runMigrations();
  return NextResponse.json({ success: true });
}
