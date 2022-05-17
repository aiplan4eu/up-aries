"""Unified Planning Integration for Aries"""
from enum import Enum, auto
from typing import IO, Callable, Optional, Union

import unified_planning as up
from unified_planning.environment import get_env
from unified_planning.exceptions import UPException
from unified_planning.grpc.proto_reader import ProtobufReader
from unified_planning.grpc.proto_writer import ProtobufWriter
from unified_planning.model import problem_kind as PROBLEM_KIND
from unified_planning.solvers import Solver


class OptimalityGuarantee(Enum):
    SATISFICING = auto()
    SOLVED_OPTIMALLY = auto()


class Aries(Solver):
    """Represents the solver interface."""

    reader = ProtobufReader()
    writer = ProtobufWriter()

    @property
    def name(self) -> str:
        return "aries"

    @staticmethod
    def is_oneshot_planner() -> bool:
        return True

    @staticmethod
    def satisfies(optimality_guarantee: Union[OptimalityGuarantee, str]) -> bool:
        # TODO: Optimality Integrity
        return super().satisfies(optimality_guarantee)

    @staticmethod
    def is_plan_validator() -> bool:
        return False

    @staticmethod
    def is_grounder() -> bool:
        return False

    def ground(self, problem: "up.model.Problem") -> "up.solvers.results.GroundingResu":
        raise UPException("Aries does not support grounding")

    def validate(
        self, problem: "up.model.Problem", plan: "up.plan.Plan"
    ) -> "up.solvers.results.ValidationRes":
        raise UPException("Aries does not support validation")

    @staticmethod
    def supports(problem_kind: "up.model.ProblemKind") -> bool:
        return bool(
            problem_kind
            in [
                PROBLEM_KIND.full_temporal_kind,
                PROBLEM_KIND.basic_temporal_kind,
                PROBLEM_KIND.object_fluent_kind,
                PROBLEM_KIND.hierarchical_kind,
            ]
        )

    def solve(
        self,
        problem: "up.model.Problem",
        callback: Optional[
            Callable[["up.solvers.results.PlanGenerationResult"], None]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> "up.solvers.results.PlanGenerationResult":
        # TODO: Solve problem
        raise NotImplementedError

    def destroy(self):
        # TODO: Destroy Aries server
        pass


get_env().factory.add_solver("Aries", "up_aries", "Aries")
