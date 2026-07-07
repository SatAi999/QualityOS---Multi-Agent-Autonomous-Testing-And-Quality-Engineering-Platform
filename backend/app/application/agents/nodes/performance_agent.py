import logging
from typing import Dict, Any
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.PerformanceAgent")

@trace_agent_execution("PerformanceAgent")
async def performance_agent_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Performance Agent.
    Generates load, stress, and spike test configurations using k6.
    """
    logger.info("Executing Performance Agent Node...")
    generated_code = state.get("generated_tests", {}).copy()
    
    k6_script = """import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 50 }, // Ramp up to 50 users
    { duration: '1m', target: 50 },  // Stay at 50 users
    { duration: '15s', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<200'], // 95% of requests must complete under 200ms
  },
};

export default function () {
  const url = 'http://localhost:8000/api/v1/auth/login';
  const payload = JSON.stringify({
    username: 'testadmin',
    password: 'AdminSecurePass123!',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const res = http.post(url, payload, params);
  check(res, {
    'login status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
"""
    generated_code["tests/performance/load_login.js"] = k6_script
    audit_msg = "Generated k6 load script measuring authentication endpoint latency under concurrency."
    
    return {
        "generated_tests": generated_code,
        "current_agent": "SecurityAgent",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
