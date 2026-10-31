/**
 * CIVORA AI TypeScript Integration Example.
 */

import OpenAI from "openai";

interface CivoraConfig {
  apiKey: string;
  baseUrl?: string;
  model?: "civora-coder" | "civora-general" | "civora-repository-agent" | "civora-engineering-agent";
}

export class CivoraClient {
  private client: OpenAI;
  private defaultModel: string;

  constructor(config: CivoraConfig) {
    this.defaultModel = config.model || "civora-coder";
    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseUrl || "http://localhost:4000/v1",
    });
  }

  async askCode(prompt: string): Promise<string> {
    const res = await this.client.chat.completions.create({
      model: this.defaultModel,
      messages: [{ role: "user", content: prompt }],
    });
    return res.choices[0]?.message?.content ?? "";
  }
}

// Example usage
async function example() {
  const civora = new CivoraClient({
    apiKey: process.env.CIVORA_API_KEY || "civora_sk_live_YOUR_KEY_HERE",
    model: "civora-coder"
  });

  const reply = await civora.askCode("Write a TypeScript debounce function.");
  console.log(reply);
}

if (process.env.RUN_EXAMPLE) {
  example().catch(console.error);
}
