#!/usr/bin/env python3
"""Unified Planning Integration for Aries"""
import os
import subprocess
from enum import Enum, auto
import time
from typing import IO, Callable, Optional, Union

import grpc
import unified_planning as up
import unified_planning.engines.mixins as mixins
import unified_planning.grpc.generated.unified_planning_pb2 as proto
import unified_planning.grpc.generated.unified_planning_pb2_grpc as grpc_api
from unified_planning import engines
from unified_planning.engines.results import PlanGenerationResultStatus
from unified_planning.exceptions import UPException
from unified_planning.grpc.proto_reader import ProtobufReader
from unified_planning.grpc.proto_writer import ProtobufWriter

from .executor import Executor

class OptimalityGuarantee(Enum):
    SATISFICING = auto()
    SOLVED_OPTIMALLY = auto()


class GRPCPlanner(engines.engine.Engine, mixins.OneshotPlannerMixin):
    """
    This class is the interface of a generic gRPC planner
    that can be contacted at a given host and port.
    """

    def __init__(self, host: str = "localhost", port: Optional[int] = None):
        engines.engine.Engine.__init__(self)
        mixins.OneshotPlannerMixin.__init__(self)
        self._host = host
        self._port = port
        self._writer = ProtobufWriter()
        self._reader = ProtobufReader()

    def _solve(
        self,
        problem: "up.model.AbstractProblem",
        callback: Optional[
            Callable[["up.engines.results.PlanGenerationResult"], None]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> "up.engines.results.PlanGenerationResult":
        assert isinstance(problem, up.model.Problem)
        proto_problem = self._writer.convert(problem)
        with grpc.insecure_channel(f"{self._host}:{self._port}") as channel:
            planner = grpc_api.UnifiedPlanningStub(channel)
            req = proto.PlanRequest(problem=proto_problem, timeout=timeout)
            response_stream = planner.planOneShot(req)
            for response in response_stream:
                response = self._reader.convert(response, problem)
                assert isinstance(response, up.engines.results.PlanGenerationResult)
                if (
                    response.status == PlanGenerationResultStatus.INTERMEDIATE
                    and callback is not None
                ):
                    callback(response)
                else:
                    return response


class Aries(GRPCPlanner):
    """Represents the solver interface."""

    reader = ProtobufReader()
    writer = ProtobufWriter()

    def __init__(self, params: dict = {}, stdout: Optional[IO[str]] = None):
        self.run_server = params.get("run_server", False)

        if stdout is None:
            self.stdout = open(os.devnull, "w")

        self.executable = os.path.join(
            os.path.dirname(__file__), Executor()()
        )

        print(
            f"Launching Aries with executable: {self.executable} (logs are redirected to {self.stdout})"
        )
        self.process_id = subprocess.Popen(
            self.executable, stdout=self.stdout, stderr=self.stdout, shell=True
        )
        time.sleep(0.1)
        super().__init__(host="localhost", port=params.get("port", 2222))

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
        supported_kind = up.model.ProblemKind()
        supported_kind.set_problem_class("ACTION_BASED")  # type: ignore
        supported_kind.set_problem_class("HIERARCHICAL")  # type: ignore
        supported_kind.set_time("CONTINUOUS_TIME")  # type: ignore
        supported_kind.set_time("INTERMEDIATE_CONDITIONS_AND_EFFECTS")  # type: ignore
        supported_kind.set_time("TIMED_EFFECT")  # type: ignore
        supported_kind.set_time("TIMED_GOALS")  # type: ignore
        supported_kind.set_time("DURATION_INEQUALITIES")  # type: ignore
        # supported_kind.set_numbers('DISCRETE_NUMBERS') # type: ignore
        # supported_kind.set_numbers('CONTINUOUS_NUMBERS') # type: ignore
        supported_kind.set_typing("FLAT_TYPING")  # type: ignore
        supported_kind.set_typing("HIERARCHICAL_TYPING")  # type: ignore
        supported_kind.set_conditions_kind("NEGATIVE_CONDITIONS")  # type: ignore
        supported_kind.set_conditions_kind("DISJUNCTIVE_CONDITIONS")  # type: ignore
        supported_kind.set_conditions_kind("EQUALITY")  # type: ignore
        # supported_kind.set_fluents_type('NUMERIC_FLUENTS') # type: ignore
        supported_kind.set_fluents_type("OBJECT_FLUENTS")  # type: ignore

        return problem_kind <= supported_kind


    def destroy(self):
        self.process_id.kill()

    def __del__(self):
        self.destroy()

