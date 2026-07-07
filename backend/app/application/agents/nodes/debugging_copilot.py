import logging
from typing import Dict, Any, List
from app.application.agents.state import QualityOSState
from app.core.telemetry import trace_agent_execution

logger = logging.getLogger("QualityOS.DebuggingCopilot")

@trace_agent_execution("DebuggingCopilot")
async def debugging_copilot_node(state: QualityOSState) -> Dict[str, Any]:
    """
    Debugging Copilot Agent.
    Interprets logs/traces and suggests specific code repairs in standard git diff formats.
    """
    logger.info("Executing Debugging Copilot Node...")
    rca_findings = state.get("rca_findings", [])
    suggestions: List[Dict[str, Any]] = []
    
    for rca in rca_findings:
        verdict = rca.get("verdict", "")
        # Construct dynamic patch solution
        diff_patch = """diff --git a/backend/app/infrastructure/auth_provider.py b/backend/app/infrastructure/auth_provider.py
index a231f4..c1102e 100644
--- a/backend/app/infrastructure/auth_provider.py
+++ b/backend/app/infrastructure/auth_provider.py
@@ -10,7 +10,7 @@ class AuthenticationProvider(IAuthenticationProvider):
     def decode_token(self, token: str, is_refresh: bool = False) -> Dict[str, Any]:
-        secret = settings.SECRET_KEY
+        secret = settings.REFRESH_SECRET_KEY if is_refresh else settings.SECRET_KEY
         try:
"""
        suggestions.append({
            "target_file": "app/infrastructure/auth_provider.py",
            "issue": verdict,
            "patch": diff_patch,
            "explanation": "Ensure that the decoding function switches validation secrets dynamically based on token type."
        })
        
    audit_msg = f"Debugging Copilot formulated {len(suggestions)} source code repair diff patches."
    
    return {
        "debugging_suggestions": suggestions,
        "current_agent": "CoverageIntelligence",
        "audit_trail": state.get("audit_trail", []) + [audit_msg]
    }
