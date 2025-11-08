# zk-gas-soundness

## Overview
**zk-gas-soundness** retrieves and analyzes recent EVM blocks to assess gas usage, base fees, and block utilization.  
It’s designed for **zk-rollup and L2 monitoring**, where consistent gas usage ensures stable proof generation and cost efficiency.

## Features
- Fetches last N blocks and computes gas utilization percentage  
- Reports average and peak gas usage  
- Displays average base fee (Gwei)  
- JSON output for dashboards or CI  
- Works with any EVM-compatible RPC  

## Installation
1. Requires Python 3.9+  
2. Install dependency:
   pip install web3  
3. Set your RPC endpoint:
   export RPC_URL=https://mainnet.infura.io/v3/YOUR_KEY

## Usage
Basic check of last 10 blocks:
   python app.py --count 10

Check 25 recent blocks on another network:
   python app.py --rpc https://arb1.arbitrum.io/rpc --count 25

Output as JSON:
   python app.py --count 15 --json

Change timeout (for slow RPCs):
   python app.py --count 10 --timeout 60

Monitor in CI with JSON parsing:
   python app.py --count 50 --json > gas_report.json

## Example Output
🔧 zk-gas-soundness  
🔗 RPC: https://mainnet.infura.io/v3/...  
🧱 Blocks to analyze: 10  
🕒 Timestamp: 2025-11-08T18:21:10Z  

📊 Summary:  
  • Avg Utilization: 84.5%  
  • Max Utilization: 96.3%  
  • Min Utilization: 62.7%  
  • Avg Base Fee: 18.2 Gwei  
  • Blocks Analyzed: 10  
⏱️ Completed in 2.3s  

## Notes
- **Utilization Formula:** `(gasUsed / gasLimit) * 100`  
- **Base Fee:** Derived from block’s EIP-1559 field (in Wei → converted to Gwei).  
- **ZK Use Case:** Stable and high utilization indicates predictable fee behavior for zk proof systems.  
- **Performance:** Works efficiently even on L2 RPCs with short block intervals.  
- **Automation:** Integrate in CI/CD to monitor block gas patterns hourly.  
- **Cross-chain Comparison:** Use separate runs for L1 vs L2 networks to detect anomalies.  
- **Exit Code:** Always `0` (no failure detection); add conditions in CI to alert on extreme deviations.
