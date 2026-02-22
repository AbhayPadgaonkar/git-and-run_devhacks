interface EthereumProvider {
  request: (args: { method: string; params?: unknown[] }) => Promise<any>;
}

interface Window {
  ethereum?: EthereumProvider;
}