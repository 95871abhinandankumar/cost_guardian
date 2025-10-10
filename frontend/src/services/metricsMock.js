// --- CORE METRICS DATA (Input for Charts: Utilization, Cost, Time Series) ---
export const METRICS_MOCK_DATA = [
  // Resource 1: CRITICAL ANOMALY (High Cost / Low Utilization - Target for Scatter Plot)
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

  // Resource 3: IDLE WASTE (SaaS License - High Savings Opportunity)
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

  // Resource 5: STORAGE (for Allocation/Treemap)
  {
    timestamp_day: "2025-10-08",
    resource_id: "s3-backup-archive",
    service_name_simplified: "S3-Storage",
    billing_tag_owner: "team:infra",
    unblended_cost_usd: 0.05,
    utilization_score: 0.01,
    resource_type: "storage"
  },
];