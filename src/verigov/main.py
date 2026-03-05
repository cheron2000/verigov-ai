"""Main CLI application for VeriGov AI with storage abstraction"""

import sys
import argparse
import os
from pathlib import Path
from typing import List

from .config.api_config import APIConfig
from .collection.whitelist_manager import WhitelistManager
from .collection.source_collector import SourceCollector
from .infrastructure.audit_log import AuditLog
from .verification.intelligence_layer import IntelligenceLayer
from .verification.fact_verification_engine import FactVerificationEngine
from .monitoring.change_detector import ChangeDetector


class VeriGovApp:
    """Main application class with configurable storage backend"""
    
    def __init__(self, storage_mode: str = None):
        # Get storage mode from environment if not specified
        if storage_mode is None:
            storage_mode = os.getenv('STORAGE_MODE', 'local')
        
        self.storage_mode = storage_mode
        self.config = APIConfig()
        
        # Initialize components with storage mode
        self.whitelist = WhitelistManager(storage_mode=storage_mode)
        self.collector = SourceCollector(self.whitelist, self.config.timeout)
        self.audit = AuditLog(storage_mode=storage_mode)
        self.intelligence = IntelligenceLayer(self.config)
        self.engine = FactVerificationEngine(
            self.collector,
            self.intelligence,
            self.audit,
            storage_mode=storage_mode
        )
        self.monitor = ChangeDetector(self.collector, self.audit)
        
        print(f"🏛️  VeriGov AI initialized with {storage_mode} storage")
    
    def verify_claim(self, claim: str, sources: List[str] = None) -> dict:
        """Verify a single claim"""
        print(f"\n🔍 Verifying claim: {claim}")
        
        result = self.engine.verify(claim, sources)
        
        self._print_result(result)
        return result
    
    def verify_batch(self, claims: List[str], sources: List[str] = None) -> dict:
        """Verify multiple claims"""
        print(f"\n📊 Verifying batch of {len(claims)} claims...")
        
        batch_result = self.engine.verify_batch(claims, sources)
        
        print(f"\n✅ Batch verification completed!")
        print(f"📋 Batch ID: {batch_result['batch_id']}")
        print(f"📊 Summary: {batch_result['summary']}")
        
        return batch_result
    
    def get_verification(self, verification_id: str) -> dict:
        """Get a stored verification result"""
        result = self.engine.get_verification(verification_id)
        if result:
            self._print_result(result)
            return result
        else:
            print(f"❌ Verification {verification_id} not found")
            return None
    
    def get_batch_results(self, batch_id: str) -> List[dict]:
        """Get stored batch results"""
        results = self.engine.get_batch_results(batch_id)
        if results:
            print(f"📋 Batch {batch_id}: {len(results)} results")
            return results
        else:
            print(f"❌ Batch {batch_id} not found")
            return None
    
    def monitor_sources(self, urls: List[str], interval: int = 3600) -> None:
        """Monitor sources for changes"""
        print(f"\n👀 Monitoring {len(urls)} sources (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        def on_change(event):
            print(f"⚠️  Change detected: {event['url']}")
        
        try:
            self.monitor.monitor(urls, callback=on_change)
        except KeyboardInterrupt:
            print("\n✋ Monitoring stopped")
    
    def interactive_mode(self) -> None:
        """Run in interactive mode"""
        print(f"\n🏛️  VeriGov AI - Interactive Mode ({self.storage_mode} storage)")
        print("Commands: verify <claim>, get <verification_id>, batch <file>, audit, quit\n")
        
        while True:
            try:
                cmd = input("verigov> ").strip()
                
                if cmd.lower() == "quit":
                    break
                elif cmd.lower() == "audit":
                    self._show_audit()
                elif cmd.lower().startswith("verify "):
                    claim = cmd[7:].strip()
                    self.verify_claim(claim)
                elif cmd.lower().startswith("get "):
                    verification_id = cmd[4:].strip()
                    self.get_verification(verification_id)
                elif cmd.lower().startswith("batch "):
                    file_path = cmd[6:].strip()
                    self._verify_batch_from_file(file_path)
                else:
                    print("Commands: verify <claim>, get <verification_id>, batch <file>, audit, quit")
            except KeyboardInterrupt:
                print("\n")
                break
    
    def _verify_batch_from_file(self, file_path: str) -> None:
        """Verify claims from a file"""
        try:
            with open(file_path, 'r') as f:
                claims = [line.strip() for line in f if line.strip()]
            self.verify_batch(claims)
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")
    
    def export_audit_log(self, output_path: str) -> None:
        """Export audit log"""
        self.audit.export(output_path)
        print(f"✅ Audit log exported to {output_path}")
    
    def _print_result(self, result: dict) -> None:
        """Print verification result"""
        status_emoji = {
            "VERIFIED": "✅",
            "PARTIALLY_VERIFIED": "⚠️",
            "UNVERIFIED": "❓",
            "FALSE": "❌",
            "NO_SOURCES": "🚫",
            "ERROR": "⚠️"
        }
        
        emoji = status_emoji.get(result["status"], "❓")
        print(f"\n{emoji} Status: {result['status']}")
        print(f"🆔 ID: {result.get('verification_id', 'N/A')}")
        print(f"📊 Confidence: {result['confidence']}%")
        print(f"📝 Explanation: {result['explanation']}")
        print(f"🔗 Sources checked: {result.get('sources_checked', 0)}")
    
    def _show_audit(self) -> None:
        """Show recent audit entries"""
        entries = self.audit.query(limit=10)
        print(f"\n📋 Audit Log: {len(entries)} recent entries")
        for entry in entries[-5:]:
            print(f"  {entry['timestamp']} - {entry['event_type']}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="VeriGov AI - Government Information Verification")
    parser.add_argument("--storage", choices=['local', 'aws', 'hybrid'], 
                       help="Storage backend mode")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify a claim")
    verify_parser.add_argument("claim", help="Claim to verify")
    verify_parser.add_argument("--sources", nargs="+", help="Source URLs")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get verification result")
    get_parser.add_argument("verification_id", help="Verification ID")
    
    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Verify multiple claims")
    batch_parser.add_argument("file", help="File containing claims (one per line)")
    batch_parser.add_argument("--output", help="Output file for results")
    
    # Get batch command
    get_batch_parser = subparsers.add_parser("get-batch", help="Get batch results")
    get_batch_parser.add_argument("batch_id", help="Batch ID")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Monitor sources")
    monitor_parser.add_argument("--sources", nargs="+", required=True, help="URLs to monitor")
    monitor_parser.add_argument("--interval", type=int, default=3600, help="Check interval in seconds")
    
    # Interactive command
    subparsers.add_parser("interactive", help="Interactive mode")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Export audit log")
    audit_parser.add_argument("--output", default="audit_export.json", help="Output file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        app = VeriGovApp(storage_mode=args.storage)
        
        if args.command == "verify":
            app.verify_claim(args.claim, args.sources)
        elif args.command == "get":
            app.get_verification(args.verification_id)
        elif args.command == "batch":
            with open(args.file, 'r') as f:
                claims = [line.strip() for line in f if line.strip()]
            batch_result = app.verify_batch(claims)
            if args.output:
                import json
                with open(args.output, 'w') as f:
                    json.dump(batch_result, f, indent=2)
        elif args.command == "get-batch":
            app.get_batch_results(args.batch_id)
        elif args.command == "monitor":
            app.monitor_sources(args.sources, args.interval)
        elif args.command == "interactive":
            app.interactive_mode()
        elif args.command == "audit":
            app.export_audit_log(args.output)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
