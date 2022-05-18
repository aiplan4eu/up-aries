"""Unified Planning Integration for Aries"""
from enum import Enum, auto
from typing import IO, Callable, Optional, Union
import subprocess

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

    def __init__(self, params: dict = {}):
        self.run_server = params.get("run_server", False)

        self.executable = "./bin/aries_linux_amd64"
        # TODO: Add support for different OS

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
        ### If a problem is sent, for GRPC communication, we can solve the problem in two ways:
        ### - If the server is ran on a separate process, we can send the problem to the server and get a plan back
        ### - If not, we could encode the problem and call the server with the encoded problem
        ###  To enable the option for the above cases, we should be having a planner parameter `run_server`
        if self.run_server:
            self.process_id = subprocess.Popen([self.executable, "server"])
            # TODO: Add GRPC Client
        else:
            # Encode the problem
            encoded_problem = self.writer.convert(problem)
            command = f"{self.executable} {encoded_problem}"
            self.process_id = subprocess.run(command, shell=True, stdout=output_stream)
        
        raise NotImplementedError

    def destroy(self):
        self.process_id.kill()


get_env().factory.add_solver("Aries", "up_aries", "Aries")
