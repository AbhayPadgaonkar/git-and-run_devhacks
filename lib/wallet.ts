import { ethers } from "ethers";

/**
 * Step 1: MetaMask Connection
 *
 * ✔ Shows: "Connect to MetaMask" popup
 * ✔ User clicks: "Connect"
 * ✔ Returns: User's wallet address (e.g., 0x123...)
 *
 * MetaMask does NOT authenticate here - just connects.
 */
export async function connectWallet() {
  if (!window.ethereum) throw new Error("Metamask not installed");

  const accounts = await window.ethereum.request({
    method: "eth_requestAccounts",
  });

  return accounts[0];
}

/**
 * Step 3: MetaMask Signature - Message Signing
 *
 * ⭐ IMPORTANT: The message is NOT decoration - it's CRITICAL
 *
 * The system will verify:
 *   "This wallet created this signature for THIS SPECIFIC message"
 *
 * Verification checks THREE things together:
 *   1. Wallet address
 *   2. Message content
 *   3. Signature
 *
 * Without the message, the signature is meaningless.
 *
 * Analogy:
 *   - Signing a blank paper → meaningless
 *   - Signing a contract → meaningful (proves approval of content)
 *   - Message = contract content
 *   - Signature = proof of approval
 *
 * ✔ Shows: "Sign this message?" popup with full message content
 * ✔ Displays: Message content + wallet address
 * ✔ User clicks: "Sign" / "Reject"
 * ✔ Returns: Signature (created with private key for THIS message)
 *
 * Each signature is DIFFERENT because message changes:
 *   - Different nonce → different message
 *   - Different hash → different message
 *   - → Different signature each time
 *
 * This signature uniquely proves:
 *   ✔ Wallet ownership (only this wallet can create this signature)
 *   ✔ Approval of this specific content (message)
 *   ✔ Freshness (nonce prevents replay attacks)
 */
export async function signMessage(message: string) {
  const provider = new ethers.BrowserProvider(window.ethereum);
  const signer = await provider.getSigner();

  return signer.signMessage(message);
}