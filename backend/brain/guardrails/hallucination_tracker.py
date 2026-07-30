"""
Hallucination Observation Tracker
==================================
hallucination_rate = flagged_responses / total_observed_responses
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Optional


@dataclass
class HallucinationObservation:
    observation_id: str
    timestamp: float
    session_id: Optional[str]
    agent_name: Optional[str]
    flagged: bool
    groundedness_score: Optional[float]
    reason: Optional[str] = None
    output_excerpt: Optional[str] = None


class HallucinationTracker:
    def __init__(self, log_path: str = "logs/hallucination_observations.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def observe(
        self,
        flagged: bool,
        groundedness_score: Optional[float] = None,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        reason: Optional[str] = None,
        output_excerpt: Optional[str] = None,
    ) -> HallucinationObservation:
        obs = HallucinationObservation(
            observation_id=str(uuid.uuid4()),
            timestamp=time.time(),
            session_id=session_id,
            agent_name=agent_name,
            flagged=flagged,
            groundedness_score=groundedness_score,
            reason=reason,
            output_excerpt=(output_excerpt or "")[:200] or None,
        )
        self._persist(obs)
        return obs

    def _persist(self, obs: HallucinationObservation) -> None:
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(obs)) + "\n")

    def load_observations(self) -> List[HallucinationObservation]:
        if not self.log_path.exists():
            return []
        observations = []
        with self.log_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                observations.append(HallucinationObservation(**json.loads(line)))
        return observations

    def hallucination_rate(
        self,
        since_timestamp: Optional[float] = None,
        agent_name: Optional[str] = None,
    ) -> dict:
        observations = self.load_observations()
        if since_timestamp is not None:
            observations = [o for o in observations if o.timestamp > since_timestamp]
        if agent_name is not None:
            observations = [o for o in observations if o.agent_name == agent_name]

        total = len(observations)
        flagged = sum(1 for o in observations if o.flagged)
        rate = (flagged / total) if total else None

        return {"total": total, "flagged": flagged, "rate": rate}