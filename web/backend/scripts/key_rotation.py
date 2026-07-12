#!/usr/bin/env python3
"""Phase 3 Task 20: Key Rotation CLI Tool
Provides command-line interface for managing encryption key rotation

Usage:
    # View current key information
    python scripts/key_rotation.py info

    # View version distribution report
    python scripts/key_rotation.py report

    # Rotate to new key version
    python scripts/key_rotation.py rotate --new-version 2

    # Migrate secrets to new version
    python scripts/key_rotation.py migrate --target-version 2

    # Full rotation workflow (rotate + migrate)
    python scripts/key_rotation.py full-rotation --new-version 2

Environment Variables:
    ENCRYPTION_MASTER_PASSWORD: Master password for encryption (required)
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Optional


# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.encryption import EncryptionManager, SecretManager


class KeyRotationCLI:
    """CLI for key rotation operations"""

    def __init__(self, master_password: Optional[str] = None):
        """Initialize CLI

        Args:
            master_password: Master password (if None, reads from env)

        """
        self.master_password = master_password or os.getenv("ENCRYPTION_MASTER_PASSWORD")

        if not self.master_password:
            print("❌ Error: ENCRYPTION_MASTER_PASSWORD not set")
            print("Set it with: export ENCRYPTION_MASTER_PASSWORD='your-secure-password'")
            sys.exit(1)

        # Initialize managers
        self.encryption_mgr = EncryptionManager(master_password=self.master_password, key_version=1)
        self.secret_mgr = SecretManager(encryption_manager=self.encryption_mgr)

    def cmd_info(self):
        """Display current key information"""
        print("\n" + "=" * 70)
        print("📊 Encryption Key Information")
        print("=" * 70)

        info = self.encryption_mgr.get_key_info()

        print(f"\n🔑 Current Version: {info['current_version']}")
        print(f"📦 Available Versions: {sorted(info['available_versions'])}")

        print("\n📅 Key Metadata:")
        for version in sorted(info["key_metadata"].keys()):
            metadata = info["key_metadata"][version]
            print(f"\n  Version {version}:")
            print(f"    Created:  {metadata['created_at']}")
            if metadata["rotated_at"]:
                print(f"    Rotated:  {metadata['rotated_at']}")
            else:
                print("    Status:   Active")

        print("\n" + "=" * 70 + "\n")

    def cmd_report(self):
        """Display version distribution report"""
        print("\n" + "=" * 70)
        print("📈 Secret Version Distribution Report")
        print("=" * 70)

        report = self.secret_mgr.get_version_report()

        print(f"\n📦 Total Secrets: {report['total_secrets']}")
        print(f"🔑 Current Encryption Version: {report['current_encryption_version']}")
        print(f"⚠️  Secrets Needing Migration: {report['needs_migration']}")

        if report["version_distribution"]:
            print("\n📊 Version Distribution:")
            for version in sorted(report["version_distribution"].keys()):
                count = report["version_distribution"][version]
                percentage = (count / report["total_secrets"]) * 100
                is_current = version == report["current_encryption_version"]
                marker = "✅" if is_current else "⚠️ "
                print(f"  {marker} Version {version}: {count} secrets ({percentage:.1f}%)")

        if report["legacy_format_count"] > 0:
            print(f"\n🔒 Legacy Format: {report['legacy_format_count']} secrets (no version)")

        print("\n" + "=" * 70 + "\n")

    def cmd_rotate(self, new_version: int, dry_run: bool = False):
        """Rotate to new key version

        Args:
            new_version: New version number
            dry_run: If True, only show what would happen

        """
        print("\n" + "=" * 70)
        print(f"🔄 Key Rotation: Version {self.encryption_mgr.current_key_version} → {new_version}")
        print("=" * 70)

        # Validation
        if new_version <= self.encryption_mgr.current_key_version:
            print(
                f"\n❌ Error: New version ({new_version}) must be greater than current version ({self.encryption_mgr.current_key_version})",
            )
            return False

        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")
            print(f"Would rotate from version {self.encryption_mgr.current_key_version} to version {new_version}")
            print("✅ Validation passed")
            return True

        # Confirm
        response = input(f"\n⚠️  Are you sure you want to rotate to version {new_version}? (yes/no): ")
        if response.lower() != "yes":
            print("❌ Rotation cancelled")
            return False

        # Perform rotation
        print(f"\n🔄 Rotating to version {new_version}...")
        success = self.encryption_mgr.rotate_key(new_version)

        if success:
            print(f"✅ Successfully rotated to version {new_version}")
            print("\n⚠️  Note: Existing secrets are still encrypted with old versions.")
            print(f"   Run 'migrate --target-version {new_version}' to re-encrypt them.")
            return True
        print("❌ Rotation failed")
        return False

    def cmd_migrate(self, target_version: int, dry_run: bool = False, force: bool = False):
        """Migrate secrets to target version

        Args:
            target_version: Target version number
            dry_run: If True, only show what would happen
            force: Skip confirmation prompt

        """
        print("\n" + "=" * 70)
        print(f"🔄 Secret Migration to Version {target_version}")
        print("=" * 70)

        # Get current report
        report = self.secret_mgr.get_version_report()
        print(f"\n📦 Total Secrets: {report['total_secrets']}")
        print(f"⚠️  Secrets Needing Migration: {report['needs_migration']}")

        if report["total_secrets"] == 0:
            print("\n❌ No secrets to migrate")
            return False

        if report["needs_migration"] == 0:
            print("\n✅ All secrets already at current version")
            return True

        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")
            print(f"Would migrate {report['needs_migration']} secrets to version {target_version}")
            return True

        # Confirm
        if not force:
            response = input(
                f"\n⚠️  Migrate {report['needs_migration']} secrets to version {target_version}? (yes/no): ",
            )
            if response.lower() != "yes":
                print("❌ Migration cancelled")
                return False

        # Perform migration
        print("\n🔄 Migrating secrets...")
        migration_report = self.secret_mgr.migrate_to_key_version(target_version)

        # Display results
        print("\n" + "=" * 70)
        print("📊 Migration Results")
        print("=" * 70)
        print(f"\n✅ Migrated:       {migration_report['migrated']}")
        print(f"✓  Already Current: {migration_report['already_current']}")
        print(f"❌ Failed:         {migration_report['failed']}")
        print(f"📦 Total:          {migration_report['total_secrets']}")

        if migration_report["errors"]:
            print("\n❌ Errors:")
            for error in migration_report["errors"][:10]:  # Show first 10 errors
                print(f"  • {error['key']}: {error['error']}")
            if len(migration_report["errors"]) > 10:
                print(f"  ... and {len(migration_report['errors']) - 10} more")

        duration = (
            datetime.fromisoformat(migration_report["end_time"])
            - datetime.fromisoformat(migration_report["start_time"])
        ).total_seconds()
        print(f"\n⏱️  Duration: {duration:.2f}s")

        success = migration_report["failed"] == 0
        if success:
            print("\n✅ Migration completed successfully")
        else:
            print("\n⚠️  Migration completed with errors")

        print("=" * 70 + "\n")
        return success

    def cmd_full_rotation(self, new_version: int, dry_run: bool = False):
        """Perform full rotation workflow (rotate + migrate)

        Args:
            new_version: New version number
            dry_run: If True, only show what would happen

        """
        print("\n" + "=" * 70)
        print(f"🔄 Full Key Rotation Workflow to Version {new_version}")
        print("=" * 70)

        if dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")

        # Step 1: Display current state
        print("\n📊 Step 1: Current State")
        print("-" * 70)
        self.cmd_info()
        self.cmd_report()

        # Step 2: Rotate key
        print("\n🔑 Step 2: Rotate Encryption Key")
        print("-" * 70)
        if not self.cmd_rotate(new_version, dry_run=dry_run):
            print("\n❌ Full rotation failed at key rotation step")
            return False

        if dry_run:
            print("\n✅ Dry run completed successfully")
            return True

        # Step 3: Migrate secrets
        print("\n🔄 Step 3: Migrate Secrets")
        print("-" * 70)
        if not self.cmd_migrate(new_version, force=True):
            print("\n⚠️  Key rotated but secret migration failed")
            print("   Secrets are still using old encryption versions")
            return False

        # Step 4: Verify
        print("\n✅ Step 4: Verification")
        print("-" * 70)
        self.cmd_report()

        print("\n✅ Full rotation workflow completed successfully!")
        print("=" * 70 + "\n")
        return True

    def cmd_health_check(self):
        """Perform health check on encryption system"""
        print("\n" + "=" * 70)
        print("🏥 Encryption System Health Check")
        print("=" * 70)

        # Check 1: Master password set
        print("\n1️⃣ Master Password")
        if self.master_password:
            print("   ✅ Master password configured")
        else:
            print("   ❌ Master password not set")

        # Check 2: Current key info
        print("\n2️⃣ Current Key Status")
        info = self.encryption_mgr.get_key_info()
        print(f"   ✅ Current version: {info['current_version']}")
        print(f"   ✅ Available versions: {len(info['available_versions'])}")

        # Check 3: Secret status
        print("\n3️⃣ Secret Status")
        report = self.secret_mgr.get_version_report()
        print(f"   📦 Total secrets: {report['total_secrets']}")

        if report["needs_migration"] == 0:
            print(f"   ✅ All secrets current (version {report['current_encryption_version']})")
        else:
            print(
                f"   ⚠️  {report['needs_migration']} secrets need migration to version {report['current_encryption_version']}",
            )

        # Check 4: Test encryption/decryption
        print("\n4️⃣ Encryption/Decryption Test")
        try:
            test_data = "health-check-test"
            encrypted = self.encryption_mgr.encrypt(test_data)
            decrypted = self.encryption_mgr.decrypt(encrypted)
            if decrypted == test_data:
                print("   ✅ Encryption/decryption working correctly")
            else:
                print("   ❌ Encryption/decryption mismatch")
        except Exception as e:
            print(f"   ❌ Encryption/decryption failed: {e}")

        print("\n" + "=" * 70 + "\n")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Key Rotation Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View current key information
  python scripts/key_rotation.py info

  # View version distribution report
  python scripts/key_rotation.py report

  # Rotate to version 2 (dry run)
  python scripts/key_rotation.py rotate --new-version 2 --dry-run

  # Rotate to version 2
  python scripts/key_rotation.py rotate --new-version 2

  # Migrate secrets to version 2
  python scripts/key_rotation.py migrate --target-version 2

  # Full rotation workflow (rotate + migrate)
  python scripts/key_rotation.py full-rotation --new-version 2

  # Health check
  python scripts/key_rotation.py health-check
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Info command
    subparsers.add_parser("info", help="Display current key information")

    # Report command
    subparsers.add_parser("report", help="Display version distribution report")

    # Rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate to new key version")
    rotate_parser.add_argument("--new-version", type=int, required=True, help="New version number")
    rotate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )

    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Migrate secrets to target version")
    migrate_parser.add_argument("--target-version", type=int, required=True, help="Target version number")
    migrate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )
    migrate_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    # Full rotation command
    full_parser = subparsers.add_parser("full-rotation", help="Perform full rotation workflow (rotate + migrate)")
    full_parser.add_argument("--new-version", type=int, required=True, help="New version number")
    full_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making changes",
    )

    # Health check command
    subparsers.add_parser("health-check", help="Perform health check on encryption system")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize CLI
    try:
        cli = KeyRotationCLI()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        sys.exit(1)

    # Execute command
    try:
        if args.command == "info":
            cli.cmd_info()
        elif args.command == "report":
            cli.cmd_report()
        elif args.command == "rotate":
            success = cli.cmd_rotate(args.new_version, dry_run=args.dry_run)
            sys.exit(0 if success else 1)
        elif args.command == "migrate":
            success = cli.cmd_migrate(args.target_version, dry_run=args.dry_run, force=args.force)
            sys.exit(0 if success else 1)
        elif args.command == "full-rotation":
            success = cli.cmd_full_rotation(args.new_version, dry_run=args.dry_run)
            sys.exit(0 if success else 1)
        elif args.command == "health-check":
            cli.cmd_health_check()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
