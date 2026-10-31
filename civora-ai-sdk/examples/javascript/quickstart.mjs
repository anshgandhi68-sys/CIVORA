/**
 * CIVORA AI JavaScript Quickstart Example.
 * Run with: node examples/javascript/quickstart.mjs
 */

import OpenAI from "openai";

const apiKey = process.env.CIVORA_API_KEY || "civora_sk_live_YOUR_KEY_HERE";
const baseURL = process.env.CIVORA_BASE_URL || "http://localhost:4000/v1";

console.log(`Connecting to CIVORA Universal API at: ${baseURL}`);

const client = new OpenAI({
  apiKey: apiKey,
  baseURL: baseURL,
});

async function run() {
  try {
    const response = await client.chat.completions.create({
      model: "civora-coder",
      messages: [
        { role: "system", content: "You are CIVORA Senior Coder." },
        { role: "user", content: "Write a high-performance LRU cache in JavaScript with unit tests." }
      ],
      temperature: 0.7,
    });

    console.log("\nCIVORA Response:\n");
    console.log(response.choices[0].message.content);
    console.log("\nToken Usage:", response.usage);
  } catch (err) {
    console.error("API Request Error:", err.message);
  }
}

run();
