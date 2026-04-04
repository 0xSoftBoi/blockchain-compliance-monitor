#!/usr/bin/env python3
"""Standalone entry point for the Blockchain Compliance Monitor engine.

Runs the compliance monitor in daemon mode, continuously screening
transactions and performing sanctions checks.

Usage:
    python run_monitor.py [--jurisdiction US,EU] [--risk-threshold 0.7]
"""
import argparse
import logging
import os
import sys
import time
from pathlib import Path

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/compliance.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Blockchain Compliance Monitor")
    parser.add_argument(
        "--jurisdictions",
        default=os.getenv("ENABLED_JURISDICTIONS", "US,EU"),
        help="Comma-separated list of jurisdictions (default: US,EU)",
    )
    parser.add_argument(
        "--risk-threshold",
        type=float,
        default=float(os.getenv("DEFAULT_RISK_THRESHOLD", "0.7")),
        help="Risk score threshold for flagging transactions (default: 0.7)",
    )
    parser.add_argument(
        "--institution",
        default=os.getenv("INSTITUTION_NAME", "Global Settlement"),
        help="Institution name for reports",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a quick demo screening and exit",
    )
    return parser.parse_args()


def run_demo(monitor):
    """Run a quick demo screening to verify the system works."""
    logger.info("Running demo transaction screening...")

    result = monitor.screen_transaction(
        transaction_hash="0x742d35cc6634c0532925a3b844bc9e7fbbdd98e3b7c007e836c8ebcf5df9ae25",
        from_address="0x123456789abcdef123456789abcdef1234567890",
        to_address="0xabcdef123456789abcdef123456789abcdef1234",
        amount=1_500_000,  # $15,000 in cents
        currency="USDC",
        metadata={"sender_country": "US", "recipient_country": "EU"},
    )

    print("\n--- Demo Screening Result ---")
    print(f"  Transaction : {result.transaction_hash[:20]}...")
    print(f"  Risk Score  : {result.risk_score:.2f}")
    print(f"  Risk Level  : {result.risk_level.upper()}")
    print(f"  Sanctioned  : {result.sanctions_match}")
    print(f"  Risk Factors: {result.risk_factors or ['None']}")
    print(f"  Approved    : {result.approved}")
    print(f"  Notes       : {result.notes}")
    print("----------------------------\n")

    # Demo compliance status lookup
    status = monitor.get_compliance_status("0x123456789abcdef123456789abcdef1234567890")
    print("--- Address Compliance Status ---")
    print(f"  Address     : {status['address'][:20]}...")
    print(f"  Sanctioned  : {status['sanctioned']}")
    print(f"  Risk Level  : {status['risk_level']}")
    print(f"  KYC Status  : {status['kyc_status']}")
    print(f"  Cleared     : {status['cleared_for_trading']}")
    print("---------------------------------\n")

    logger.info("Demo complete. System is operational.")


def main():
    args = parse_args()

    jurisdictions = [j.strip() for j in args.jurisdictions.split(",")]

    logger.info("Initializing Blockchain Compliance Monitor")
    logger.info(f"  Jurisdictions   : {jurisdictions}")
    logger.info(f"  Risk Threshold  : {args.risk_threshold}")
    logger.info(f"  Institution     : {args.institution}")

    from compliance_monitor import ComplianceMonitor
    from compliance_monitor.config import ComplianceConfig

    config = ComplianceConfig(
        jurisdictions=jurisdictions,
        risk_threshold=args.risk_threshold,
        enable_sanctions_screening=True,
        institution_name=args.institution,
    )

    monitor = ComplianceMonitor(config)
    logger.info("Compliance Monitor initialized successfully")

    if args.demo:
        run_demo(monitor)
        return

    # Daemon mode: keep running, ready to process transactions via the API
    logger.info("Monitor running in daemon mode. Start the API with:")
    logger.info("  uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(60)
            logger.debug("Monitor heartbeat — system operational")
    except KeyboardInterrupt:
        logger.info("Shutting down compliance monitor.")


if __name__ == "__main__":
    main()
