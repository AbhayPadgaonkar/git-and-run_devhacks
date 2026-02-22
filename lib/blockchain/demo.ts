import { logToBlockchain } from "./service.ts";
import crypto from "crypto";
import "dotenv/config";
export function hashModelUpdate(weights: any) {
  return crypto
    .createHash("sha256")
    .update(JSON.stringify(weights))
    .digest("hex");
}
function generateMockWeights() {
  return {
    conv1: Array.from({ length: 10 }, () => Math.random()),
    conv2: Array.from({ length: 8 }, () => Math.random()),
    fc: Array.from({ length: 5 }, () => Math.random())
  };
}

(async () => {
  try {
    const weights = generateMockWeights();
    const weightHash = hashModelUpdate(weights);
    
    console.log("📦 Model Update Hash:", weightHash);
    console.log("📤 Sending to blockchain...\n");
    
    const txHash = await logToBlockchain("client_1", weightHash, 1);

    console.log("✅ Blockchain TX:", txHash);
  } catch (error: any) {
    console.error("❌ Error:", error.message || error);
    process.exit(1);
  }
})();