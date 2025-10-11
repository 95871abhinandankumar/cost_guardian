export const METRICS_MOCK_DATA = [
  // Resource 1: CRITICAL ANOMALY (High Cost / Low Utilization)
  {
    timestamp_day: "2025-10-08",
    resource_id: "i-prod-web01",
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:data",
    unblended_cost_usd: 15.00,
    utilization_score: 0.07,
    resource_type: "compute"
  },
  {
    timestamp_day: "2025-10-07",
    resource_id: "i-prod-web01",
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:data",
    unblended_cost_usd: 15.00,
    utilization_score: 0.06,
    resource_type: "compute"
  },

  // Resource 2: HEALTHY RESOURCE (Medium Cost / Normal Utilization)
  {
    timestamp_day: "2025-10-08",
    resource_id: "rds-db-alpha",
    service_name_simplified: "RDS-DB",
    billing_tag_owner: "team:api",
    unblended_cost_usd: 8.00,
    utilization_score: 0.55,
    resource_type: "db"
  },

  // Resource 3: IDLE WASTE (SaaS License)
  {
    timestamp_day: "2025-10-08",
    resource_id: "slack-license-29384",
    service_name_simplified: "Slack-License",
    billing_tag_owner: "team:finance",
    unblended_cost_usd: 0.40,
    utilization_score: 0.00,
    resource_type: "saas_seat"
  },

  // Resource 4: HIGH UTILIZATION
  {
    timestamp_day: "2025-10-08",
    resource_id: "i-batch-etl05",
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:data",
    unblended_cost_usd: 20.00,
    utilization_score: 0.98,
    resource_type: "compute"
  },

  // Resource 5: STORAGE
  {
    timestamp_day: "2025-10-08",
    resource_id: "s3-backup-archive",
    service_name_simplified: "S3-Storage",
    billing_tag_owner: "team:infra",
    unblended_cost_usd: 0.05,
    utilization_score: 0.01,
    resource_type: "storage"
  },

  // Resource 6: HIGH COST REFERENCE (Healthy Outlier)
  {
    timestamp_day: "2025-10-08",
    resource_id: "db-cluster-ana",
    service_name_simplified: "RDS-DB",
    billing_tag_owner: "team:finance",
    unblended_cost_usd: 166.67,
    utilization_score: 0.90,
    resource_type: "db"
  },

  // Resource 7: UNTAGGED WASTE (Governance Target)
  {
    timestamp_day: "2025-10-08",
    resource_id: "s3-anon-log-293",
    service_name_simplified: "S3-Storage",
    // FIX: Explicitly defined as a string to satisfy the Metric interface
    billing_tag_owner: "owner:unknown",
    unblended_cost_usd: 5.00,
    utilization_score: 0.0,
    resource_type: "storage"
  },

  // Historical data points for trend chart (simulating 30-day utilization changes)
  // FIX: Ensured all fields are explicitly included to avoid 'undefined' error
  {
    timestamp_day: "2025-09-10",
    resource_id: "i-hist-01",
    resource_type: "compute",
    utilization_score: 0.30,
    unblended_cost_usd: 10,
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:history"
  },
  {
    timestamp_day: "2025-09-20",
    resource_id: "i-hist-02",
    resource_type: "compute",
    utilization_score: 0.45,
    unblended_cost_usd: 10,
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:history"
  },
  {
    timestamp_day: "2025-09-30",
    resource_id: "i-hist-03",
    resource_type: "compute",
    utilization_score: 0.55,
    unblended_cost_usd: 10,
    service_name_simplified: "EC2-Compute",
    billing_tag_owner: "team:history"
  },
];