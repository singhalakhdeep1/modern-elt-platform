"""
Data Lineage Tracking for ETL Platform
Tracks data flow from source to destination with full audit trail
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class LineageNode:
    """Represents a node in the data lineage graph"""
    node_id: str
    node_type: str  # source, transformation, destination
    name: str
    metadata: Dict[str, Any]
    timestamp: str


@dataclass
class LineageEdge:
    """Represents an edge (relationship) between nodes"""
    source_id: str
    target_id: str
    transformation: str
    metadata: Dict[str, Any]


class DataLineageTracker:
    """Tracks complete data lineage from source to destination"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
        self.lineage_file = Path("lineage/data_lineage.json")
        self.lineage_file.parent.mkdir(exist_ok=True)
        
    def add_source(self, source_id: str, source_type: str, metadata: Dict[str, Any]):
        """Add a data source to the lineage graph"""
        node = LineageNode(
            node_id=source_id,
            node_type="source",
            name=metadata.get("name", source_id),
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
        self.nodes[source_id] = node
        
    def add_transformation(self, transform_id: str, transform_type: str, metadata: Dict[str, Any]):
        """Add a transformation step to the lineage graph"""
        node = LineageNode(
            node_id=transform_id,
            node_type="transformation",
            name=metadata.get("name", transform_id),
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
        self.nodes[transform_id] = node
        
    def add_destination(self, dest_id: str, dest_type: str, metadata: Dict[str, Any]):
        """Add a destination to the lineage graph"""
        node = LineageNode(
            node_id=dest_id,
            node_type="destination",
            name=metadata.get("name", dest_id),
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )
        self.nodes[dest_id] = node
        
    def add_edge(self, source_id: str, target_id: str, transformation: str, metadata: Dict[str, Any]):
        """Add a relationship between nodes"""
        edge = LineageEdge(
            source_id=source_id,
            target_id=target_id,
            transformation=transformation,
            metadata=metadata
        )
        self.edges.append(edge)
        
    def track_etl_job(self, job_name: str, sources: List[str], transformations: List[str], destinations: List[str]):
        """Track a complete ETL job lineage"""
        job_id = self._generate_id(job_name)
        
        # Add job as transformation node
        self.add_transformation(
            job_id,
            "etl_job",
            {
                "name": job_name,
                "job_type": "etl",
                "sources": sources,
                "transformations": transformations,
                "destinations": destinations
            }
        )
        
        # Connect sources to job
        for source in sources:
            self.add_edge(source, job_id, "extract", {"timestamp": datetime.now().isoformat()})
        
        # Connect job to destinations
        for dest in destinations:
            self.add_edge(job_id, dest, "load", {"timestamp": datetime.now().isoformat()})
        
        return job_id
    
    def get_lineage_graph(self) -> Dict:
        """Get the complete lineage graph"""
        return {
            "nodes": [asdict(node) for node in self.nodes.values()],
            "edges": [asdict(edge) for edge in self.edges],
            "generated_at": datetime.now().isoformat()
        }
    
    def get_upstream(self, node_id: str) -> List[Dict]:
        """Get all upstream nodes for a given node"""
        upstream = []
        visited = set()
        
        def traverse(current_id):
            if current_id in visited:
                return
            visited.add(current_id)
            
            for edge in self.edges:
                if edge.target_id == current_id:
                    upstream.append(asdict(self.nodes[edge.source_id]))
                    traverse(edge.source_id)
        
        traverse(node_id)
        return upstream
    
    def get_downstream(self, node_id: str) -> List[Dict]:
        """Get all downstream nodes for a given node"""
        downstream = []
        visited = set()
        
        def traverse(current_id):
            if current_id in visited:
                return
            visited.add(current_id)
            
            for edge in self.edges:
                if edge.source_id == current_id:
                    downstream.append(asdict(self.nodes[edge.target_id]))
                    traverse(edge.target_id)
        
        traverse(node_id)
        return downstream
    
    def save_lineage(self):
        """Save lineage to file"""
        lineage_data = self.get_lineage_graph()
        self.lineage_file.write_text(json.dumps(lineage_data, indent=2))
        
    def load_lineage(self):
        """Load lineage from file"""
        if self.lineage_file.exists():
            lineage_data = json.loads(self.lineage_file.read_text())
            
            # Reconstruct nodes
            for node_data in lineage_data["nodes"]:
                node = LineageNode(**node_data)
                self.nodes[node.node_id] = node
            
            # Reconstruct edges
            for edge_data in lineage_data["edges"]:
                edge = LineageEdge(**edge_data)
                self.edges.append(edge)
    
    def _generate_id(self, name: str) -> str:
        """Generate unique ID from name"""
        return hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]


class CostOptimizer:
    """Optimizes ETL pipeline costs"""
    
    def __init__(self):
        self.cost_metrics = {
            "compute_cost": 0.0,
            "storage_cost": 0.0,
            "data_transfer_cost": 0.0,
            "total_cost": 0.0
        }
        
    def calculate_job_cost(self, job_name: str, rows_processed: int, duration_seconds: float, storage_gb: float) -> Dict:
        """Calculate cost for a single ETL job"""
        # Cost factors (example rates - adjust based on cloud provider)
        compute_rate = 0.05  # $ per compute hour
        storage_rate = 0.023  # $ per GB-month
        transfer_rate = 0.09  # $ per GB transferred
        
        compute_cost = (duration_seconds / 3600) * compute_rate
        storage_cost = storage_gb * storage_rate / 30  # Daily storage cost
        transfer_cost = (rows_processed * 0.001) / 1024 * transfer_rate  # Estimate transfer size
        
        total_cost = compute_cost + storage_cost + transfer_cost
        
        return {
            "job_name": job_name,
            "rows_processed": rows_processed,
            "duration_seconds": duration_seconds,
            "compute_cost": round(compute_cost, 4),
            "storage_cost": round(storage_cost, 4),
            "transfer_cost": round(transfer_cost, 4),
            "total_cost": round(total_cost, 4),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_cost_report(self, job_costs: List[Dict]) -> Dict:
        """Generate cost optimization report"""
        total_cost = sum(job["total_cost"] for job in job_costs)
        total_rows = sum(job["rows_processed"] for job in job_costs)
        total_duration = sum(job["duration_seconds"] for job in job_costs)
        
        # Calculate cost per row
        cost_per_1k_rows = (total_cost / total_rows * 1000) if total_rows > 0 else 0
        
        # Identify expensive jobs
        expensive_jobs = [job for job in job_costs if job["total_cost"] > 1.0]
        
        # Generate recommendations
        recommendations = []
        
        if cost_per_1k_rows > 0.01:
            recommendations.append("Consider batching rows to reduce per-row processing cost")
        
        if expensive_jobs:
            recommendations.append(f"Review {len(expensive_jobs)} expensive jobs for optimization opportunities")
        
        avg_duration = total_duration / len(job_costs) if job_costs else 0
        if avg_duration > 300:  # 5 minutes
            recommendations.append("Consider parallel processing for long-running jobs")
        
        return {
            "summary": {
                "total_jobs": len(job_costs),
                "total_cost": round(total_cost, 2),
                "total_rows_processed": total_rows,
                "total_duration_seconds": round(total_duration, 2),
                "cost_per_1k_rows": round(cost_per_1k_rows, 4),
                "average_job_duration": round(avg_duration, 2)
            },
            "expensive_jobs": expensive_jobs,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }


class MonitoringDashboard:
    """Monitoring and alerting for ETL pipeline"""
    
    def __init__(self):
        self.metrics = {
            "jobs_run": 0,
            "jobs_succeeded": 0,
            "jobs_failed": 0,
            "rows_processed": 0,
            "avg_duration": 0.0,
            "data_quality_score": 100.0
        }
        
    def record_job_completion(self, job_name: str, status: str, rows: int, duration: float, quality_score: float):
        """Record job completion metrics"""
        self.metrics["jobs_run"] += 1
        
        if status == "success":
            self.metrics["jobs_succeeded"] += 1
        else:
            self.metrics["jobs_failed"] += 1
        
        self.metrics["rows_processed"] += rows
        
        # Update average duration
        total_duration = self.metrics["avg_duration"] * (self.metrics["jobs_run"] - 1)
        self.metrics["avg_duration"] = (total_duration + duration) / self.metrics["jobs_run"]
        
        # Update quality score (weighted average)
        self.metrics["data_quality_score"] = (
            self.metrics["data_quality_score"] * 0.9 + quality_score * 0.1
        )
        
    def get_health_status(self) -> Dict:
        """Get overall pipeline health status"""
        success_rate = (
            self.metrics["jobs_succeeded"] / self.metrics["jobs_run"]
            if self.metrics["jobs_run"] > 0 else 1.0
        )
        
        health = "healthy"
        if success_rate < 0.95:
            health = "degraded"
        if success_rate < 0.9:
            health = "unhealthy"
        
        return {
            "status": health,
            "success_rate": round(success_rate * 100, 2),
            "jobs_run": self.metrics["jobs_run"],
            "jobs_failed": self.metrics["jobs_failed"],
            "data_quality_score": round(self.metrics["data_quality_score"], 2),
            "avg_duration": round(self.metrics["avg_duration"], 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_alerts(self) -> List[Dict]:
        """Generate alerts based on metrics"""
        alerts = []
        
        success_rate = (
            self.metrics["jobs_succeeded"] / self.metrics["jobs_run"]
            if self.metrics["jobs_run"] > 0 else 1.0
        )
        
        if success_rate < 0.9:
            alerts.append({
                "severity": "critical",
                "message": f"Job success rate ({success_rate:.1%}) below 90% threshold",
                "metric": "success_rate",
                "value": success_rate
            })
        
        if self.metrics["data_quality_score"] < 80:
            alerts.append({
                "severity": "warning",
                "message": f"Data quality score ({self.metrics['data_quality_score']:.1f}) below 80",
                "metric": "data_quality_score",
                "value": self.metrics["data_quality_score"]
            })
        
        if self.metrics["avg_duration"] > 300:
            alerts.append({
                "severity": "warning",
                "message": f"Average job duration ({self.metrics['avg_duration']:.1f}s) exceeds 5 minutes",
                "metric": "avg_duration",
                "value": self.metrics["avg_duration"]
            })
        
        return alerts


if __name__ == "__main__":
    # Example usage
    tracker = DataLineageTracker()
    
    # Add sources
    tracker.add_source("billing_db", "postgresql", {"host": "billing-db", "database": "billing"})
    tracker.add_source("user_db", "postgresql", {"host": "user-db", "database": "users"})
    
    # Add destination
    tracker.add_destination("data_warehouse", "snowflake", {"account": "xy12345", "database": "analytics"})
    
    # Track ETL job
    tracker.track_etl_job(
        "daily_subscription_sync",
        ["billing_db", "user_db"],
        ["deduplicate", "transform", "aggregate"],
        ["data_warehouse"]
    )
    
    # Save lineage
    tracker.save_lineage()
    
    print("Data lineage tracked successfully")
    print(json.dumps(tracker.get_lineage_graph(), indent=2))
