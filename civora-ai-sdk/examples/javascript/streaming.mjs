/**
 * CIVORA AI JavaScript Streaming Example.
 * Run with: node examples/javascript/streaming.mjs
 */

import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.CIVORA_API_KEY || "civora_sk_live_YOUR_KEY_HERE",
  baseURL: process.env.CIVORA_BASE_URL || "http://localhost:4000/v1",
});

async function runStream() {
  console.log("--- Starting Real-Time Stream from CIVORA General AI ---");

  try {
    const stream = await client.chat.completions.create({
      model: "civora-general",
      messages: [
        { role: "user", content: "Compare eventual consistency with strong consistency in distributed systems." }
      ],
      stream: true,
    });

    for await (const chunk of stream) {
      const delta = chunk.choices[0]?.delta?.content || "";
      process.stdout.write(delta);
    }
    console.log("\n\n[STREAM FINISHED]");
  } catch (err) {
    console.error("Stream Error:", err);
  }
}

runStream();
