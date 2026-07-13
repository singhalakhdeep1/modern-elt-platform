"""
Enhanced Data Quality Checks for ETL Platform
Comprehensive validation with schema checks, anomaly detection, and lineage tracking
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd
import numpy as np


class DataQualityChecker:
    """Comprehensive data quality validation"""
    
    def __init__(self):
        self.checks = {
            "files_scanned": 0,
            "rows_scanned": 0,
            "null_row_ids": 0,
            "invalid_payloads": 0,
            "schema_violations": 0,
            "duplicate_rows": 0,
            "anomalies_detected": 0,
            "data_freshness_issues": 0
        }
        self.schema_definitions = {
            "subscriptions": {
                "required_fields": ["row_id", "payload"],
                "payload_required": ["status", "amount", "region"],
                "field_types": {
                    "amount": "numeric",
                    "status": "string"
                }
            },
            "users": {
                "required_fields": ["row_id", "payload"],
                "payload_required": ["email", "created_at"],
                "field_types": {
                    "email": "email",
                    "created_at": "timestamp"
                }
            }
        }
    
    def run_checks(self) -> dict:
        """Run all data quality checks"""
        root = Path(__file__).resolve().parents[1]
        raw_dir = root / "extractors" / "raw_data"
        files = sorted(raw_dir.glob("*.json"))
        
        self.checks["files_scanned"] = len(files)
        
        for file in files:
            self._check_file(file)
        
        self.checks["passed"] = self._calculate_overall_status()
        self.checks["timestamp"] = datetime.now().isoformat()
        
        return self.checks
    
    def _check_file(self, file: Path):
        """Check individual file for quality issues"""
        try:
            rows = json.loads(file.read_text(encoding="utf-8"))
            self.checks["rows_scanned"] += len(rows)
            
            # Track row IDs for duplicate detection
            row_ids = []
            
            for row in rows:
                # Check null row IDs
                if not row.get("row_id"):
                    self.checks["null_row_ids"] += 1
                
                # Track duplicates
                row_id = row.get("row_id")
                if row_id in row_ids:
                    self.checks["duplicate_rows"] += 1
                row_ids.append(row_id)
                
                # Check payload structure
                payload = row.get("payload", {})
                if not isinstance(payload, dict):
                    self.checks["invalid_payloads"] += 1
                    continue
                
                # Schema validation
                table_name = file.stem.split('_')[0] if '_' in file.stem else "subscriptions"
                self._validate_schema(row, payload, table_name)
                
                # Anomaly detection
                self._detect_anomalies(payload)
                
                # Data freshness check
                self._check_data_freshness(row)
                
        except json.JSONDecodeError:
            self.checks["invalid_payloads"] += 1
    
    def _validate_schema(self, row: Dict, payload: Dict, table_name: str):
        """Validate row against schema definition"""
        schema = self.schema_definitions.get(table_name, {})
        
        # Check required fields
        for field in schema.get("required_fields", []):
            if not row.get(field):
                self.checks["schema_violations"] += 1
        
        # Check payload required fields
        for field in schema.get("payload_required", []):
            if field not in payload:
                self.checks["schema_violations"] += 1
        
        # Check field types
        for field, expected_type in schema.get("field_types", {}).items():
            if field in payload:
                if expected_type == "numeric" and not isinstance(payload[field], (int, float)):
                    self.checks["schema_violations"] += 1
                elif expected_type == "email" and "@" not in str(payload[field]):
                    self.checks["schema_violations"] += 1
    
    def _detect_anomalies(self, payload: Dict):
        """Detect statistical anomalies in data"""
        # Check for negative amounts where not expected
        if "amount" in payload and payload["amount"] < 0:
            self.checks["anomalies_detected"] += 1
        
        # Check for unusually large values
        if "amount" in payload and payload["amount"] > 1000000:
            self.checks["anomalies_detected"] += 1
    
    def _check_data_freshness(self, row: Dict):
        """Check if data is fresh (not stale)"""
        if "ingested_at" in row:
            try:
                ingest_time = datetime.fromisoformat(row["ingested_at"])
                age_hours = (datetime.now() - ingest_time).total_seconds() / 3600
                if age_hours > 48:  # Data older than 48 hours
                    self.checks["data_freshness_issues"] += 1
            except (ValueError, TypeError):
                pass
    
    def _calculate_overall_status(self) -> bool:
        """Calculate overall pass/fail status"""
        return (
            self.checks["null_row_ids"] == 0 and
            self.checks["invalid_payloads"] == 0 and
            self.checks["schema_violations"] == 0 and
            self.checks["duplicate_rows"] == 0
        )
    
    def generate_quality_report(self) -> Dict:
        """Generate detailed quality report"""
        checks = self.run_checks()
        
        report = {
            "summary": {
                "status": "PASS" if checks["passed"] else "FAIL",
                "total_files": checks["files_scanned"],
                "total_rows": checks["rows_scanned"],
                "quality_score": self._calculate_quality_score(checks)
            },
            "issues": {
                "null_row_ids": checks["null_row_ids"],
                "invalid_payloads": checks["invalid_payloads"],
                "schema_violations": checks["schema_violations"],
                "duplicate_rows": checks["duplicate_rows"],
                "anomalies": checks["anomalies_detected"],
                "freshness_issues": checks["data_freshness_issues"]
            },
            "recommendations": self._generate_recommendations(checks),
            "timestamp": checks["timestamp"]
        }
        
        return report
    
    def _calculate_quality_score(self, checks: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        if checks["rows_scanned"] == 0:
            return 100.0
        
        total_issues = (
            checks["null_row_ids"] +
            checks["invalid_payloads"] +
            checks["schema_violations"] +
            checks["duplicate_rows"] +
            checks["anomalies_detected"]
        )
        
        error_rate = total_issues / checks["rows_scanned"]
        score = max(0, 100 - (error_rate * 100))
        
        return round(score, 2)
    
    def _generate_recommendations(self, checks: Dict) -> List[str]:
        """Generate recommendations based on quality issues"""
        recommendations = []
        
        if checks["null_row_ids"] > 0:
            recommendations.append(f"Fix {checks['null_row_ids']} rows with null row IDs")
        
        if checks["invalid_payloads"] > 0:
            recommendations.append(f"Review {checks['invalid_payloads']} invalid payloads")
        
        if checks["schema_violations"] > 0:
            recommendations.append(f"Address {checks['schema_violations']} schema violations")
        
        if checks["duplicate_rows"] > 0:
            recommendations.append(f"Remove {checks['duplicate_rows']} duplicate rows")
        
        if checks["anomalies_detected"] > 0:
            recommendations.append(f"Investigate {checks['anomalies_detected']} data anomalies")
        
        if checks["data_freshness_issues"] > 0:
            recommendations.append("Review data freshness and update stale records")
        
        if not recommendations:
            recommendations.append("No quality issues detected - maintain current standards")
        
        return recommendations


def run_checks() -> dict:
    """Legacy function for backward compatibility"""
    checker = DataQualityChecker()
    return checker.run_checks()


if __name__ == "__main__":
    checker = DataQualityChecker()
    report = checker.generate_quality_report()
    print(json.dumps(report, indent=2))
