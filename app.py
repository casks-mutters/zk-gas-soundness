import os
import sys
import json
import time
import argparse
from typing import List, Dict, Any
from datetime import datetime
from web3 import Web3

DEFAULT_RPC = os.environ.get("RPC_URL", "https://mainnet.infura.io/v3/YOUR_INFURA_KEY")

def fetch_gas_data(w3: Web3, block_id: str = "latest") -> Dict[str, Any]:
    """Retrieve gas price data and block info."""
    block = w3.eth.get_block(block_id)
    base_fee = block.get("baseFeePerGas", 0)
    gas_limit = block.get("gasLimit", 0)
    gas_used = block.get("gasUsed", 0)
    utilization = round((gas_used / gas_limit) * 100, 2) if gas_limit else 0
    return {
        "block_number": block.number,
        "base_fee_wei": base_fee,
        "gas_limit": gas_limit,
        "gas_used": gas_used,
        "utilization_percent": utilization,
        "timestamp": datetime.utcfromtimestamp(block.timestamp).isoformat() + "Z",
    }

def analyze_blocks(w3: Web3, count: int) -> List[Dict[str, Any]]:
    """Fetch and analyze last N blocks."""
    latest = w3.eth.block_number
    blocks: List[Dict[str, Any]] = []
    for i in range(latest - count + 1, latest + 1):
         # ✅ New: Show live progress percentage
        processed = i - (latest - count + 1) + 1
        percent = (processed / count) * 100
        print(f"🔍 Analyzing block {i} ({processed}/{count}, {percent:.1f}% complete)...")
        block = fetch_gas_data(w3, i)
        blocks.append(block)
    return blocks

def summarize(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary stats."""
    if not blocks:
        return {"ok": False, "msg": "No data"}
    utils = [b["utilization_percent"] for b in blocks]
    avg_util = sum(utils) / len(utils)
    high = max(utils)
    low = min(utils)
    avg_base_fee = sum(b["base_fee_wei"] for b in blocks) / len(blocks)
    return {
        "avg_utilization_percent": round(avg_util, 2),
        "max_utilization_percent": round(high, 2),
        "min_utilization_percent": round(low, 2),
        "avg_base_fee_gwei": round(avg_base_fee / 1e9, 3),
        "total_blocks": len(blocks),
    }

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="zk-gas-soundness — analyze recent block gas usage, base fee, and utilization for Web3 or zk monitoring."
    )
    p.add_argument("--rpc", default=DEFAULT_RPC, help="RPC URL (default: env RPC_URL or Infura)")
    p.add_argument("--count", type=int, default=10, help="Number of recent blocks to analyze (default: 10)")
    p.add_argument("--json", action="store_true", help="Output JSON format")
    p.add_argument("--timeout", type=int, default=30, help="RPC timeout seconds (default: 30)")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    if not args.rpc.startswith(("http://", "https://")):
        print("❌ Invalid RPC URL format.")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(args.rpc, request_kwargs={"timeout": args.timeout}))
    if not w3.is_connected():
        print("❌ RPC connection failed. Check RPC_URL.")
        sys.exit(1)

    print("🔧 zk-gas-soundness")
    print(f"🔗 RPC: {args.rpc}")
    print(f"🧱 Blocks to analyze: {args.count}")
    print(f"🕒 Timestamp: {datetime.utcnow().isoformat()}Z")

    t0 = time.time()
    try:
        blocks = analyze_blocks(w3, args.count)
        summary = summarize(blocks)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(2)
    elapsed = round(time.time() - t0, 2)

    print("\n📊 Summary:")
    print(f"  • Avg Utilization: {summary['avg_utilization_percent']}%")
    print(f"  • Max Utilization: {summary['max_utilization_percent']}%")
    print(f"  • Min Utilization: {summary['min_utilization_percent']}%")
    print(f"  • Avg Base Fee: {summary['avg_base_fee_gwei']} Gwei")
    print(f"  • Blocks Analyzed: {summary['total_blocks']}")
    print(f"⏱️ Completed in {elapsed}s")

    if args.json:
        out = {
            "rpc": args.rpc,
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "blocks": blocks,
            "summary": summary,
            "elapsed_seconds": elapsed,
        }
        print(json.dumps(out, ensure_ascii=False, indent=2))

    sys.exit(0)

if __name__ == "__main__":
    main()
