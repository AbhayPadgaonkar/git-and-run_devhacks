import { ethers } from "ethers";
import { CONTRACT_ADDRESS, ABI } from "./config.ts";
export async function logToBlockchain(clientId: string, hash: string, round: number) {

  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

  const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, wallet);

  const tx = await contract.logUpdate(clientId, hash, round);

  await tx.wait();

  return tx.hash;
}