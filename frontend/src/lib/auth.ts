import { betterAuth } from "better-auth";
import { emailOTP } from "better-auth/plugins";
import { nextCookies } from "better-auth/next-js";
import { Pool } from "pg";
import { Resend } from "resend";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  baseURL: process.env.BETTER_AUTH_URL,
  secret: process.env.BETTER_AUTH_SECRET,
  plugins: [
    emailOTP({
      otpLength: 6,
      expiresIn: 300,
      disableSignUp: false,
      sendVerificationOTP: async ({ email, otp, type }) => {
        const result = await pool.query(
          "SELECT 1 FROM allowlist WHERE email = $1 LIMIT 1",
          [email.toLowerCase()],
        );
        if (result.rowCount === 0) {
          throw new Error("This email is not authorized to access GrowthOp.");
        }
        if (type === "sign-in") {
          const resend = new Resend(process.env.RESEND_API_KEY);
          await resend.emails.send({
            from: "GrowthOp <onboarding@resend.dev>",
            to: email,
            subject: "Your GrowthOp sign-in code",
            html: `
              <div style="font-family:monospace;max-width:400px;margin:0 auto;padding:32px">
                <p style="font-size:14px;font-weight:bold;margin-bottom:24px">GrowthOp</p>
                <p style="font-size:14px;color:#666;margin-bottom:16px">Your sign-in code:</p>
                <div style="font-size:36px;font-weight:bold;letter-spacing:8px;margin-bottom:24px">${otp}</div>
                <p style="font-size:12px;color:#999">Expires in 5 minutes. If you didn't request this, ignore this email.</p>
              </div>
            `,
          });
        }
      },
    }),
    nextCookies(),
  ],
});
