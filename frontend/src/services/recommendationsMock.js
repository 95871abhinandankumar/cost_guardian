// --- RECOMMENDATIONS DATA (AI Output for Action List & ROI) ---
export const RECOMMENDATIONS_MOCK_DATA = [
  // 1. Critical Compute Waste (High ROI)
  {
    recommendation_id: "REC-A7G8H",
    resource_id_impacted: "i-prod-web01",
    resource_type: "compute",
    flag_severity: "Critical",
    recommendation_type: "resize",
    current_monthly_cost: 450.00,
    projected_savings_monthly: 300.00,
    recommended_action: "VM has < 7% average CPU for 30 days. Resize from C5.large to T3.medium.",
    action_status: "pending",
    client_name: "Client Alpha"
  },
  // 2. High SaaS Waste (Easy ROI)
  {
    recommendation_id: "REC-B1K2L",
    resource_id_impacted: "slack-license-29384",
    resource_type: "saas_seat",
    flag_severity: "High",
    recommendation_type: "terminate",
    current_monthly_cost: 12.00,
    projected_savings_monthly: 12.00,
    recommended_action: "License unused in 90 days. Revoke the Slack seat.",
    action_status: "pending",
    client_name: "Client Beta"
  },
  // 3. Low Storage/Governance Issue (Low ROI, High Compliance)
  {
    recommendation_id: "REC-C3P4Q",
    resource_id_impacted: "s3-backup-archive",
    resource_type: "storage",
    flag_severity: "Low",
    recommendation_type: "reconfigure",
    current_monthly_cost: 3.00,
    projected_savings_monthly: 0.00,
    recommended_action: "Bucket lacks encryption policy. Recommend applying AES-256 for compliance.",
    action_status: "accepted",
    client_name: "Client Alpha"
  },
];