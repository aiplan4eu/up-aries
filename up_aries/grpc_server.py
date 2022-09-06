"""GRPC Client for Unified Planning"""

import socket
import threading
from typing import IO, Callable, Optional

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


class GRPCPlanner(engines.engine.Engine, mixins.OneshotPlannerMixin):
    """GRPC Planner defintion"""

    # Class instances for each planner
    _instances = {}
    _ports = set()
    _lock = threading.Lock()

    def __init__(
        self,
        host: str = "localhost",
        port: Optional[int] = None,
        override: bool = False,
        kwargs: dict = {},
    ):
        self._host = host
        self._port = port
        self._override = override
        self._timeout_sec = kwargs.get("timeout_sec", 10)

        self._writer = ProtobufWriter()
        self._reader = ProtobufReader()

        # Setup channel
        self._channel = grpc.insecure_channel(
            f"{self._host}:{self._port}",
            options=(
                ("grpc.enable_http_proxy", 0),
                ("grpc.so_reuseport", 0),
            ),
        )
        if not self._grpc_server_on(self._channel):
            raise UPException(
                "The GRPC server is not available on port {}".format(self._port)
            )

        self._planner = grpc_api.UnifiedPlanningStub(self._channel)

    def __new__(cls, **kwargs):
        """Create a new instance of the GRPCPlanner class."""
        port = kwargs.get("port")

        if (port, cls) not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._ports.add(port)
                    cls._instances[(port, cls)] = super().__new__(cls)
                    return cls._instances[(port, cls)]
        elif kwargs.get("override", False):
            return super().__new__(cls)
        return cls._instances[(port, cls)]

    def __del__(self):
        self._channel.close()

        for instance in self._instances:
            if instance[1] == self:
                self._instances.pop(instance)
                break

    def _solve(
        self,
        problem: "up.model.AbstractProblem",
        callback: Optional[
            Callable[["up.engines.results.PlanGenerationResult"], None]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> "up.engines.results.PlanGenerationResult":
        """Solve a problem and return the solution."""

        # Assert that the problem is a valid problem
        assert isinstance(problem, up.model.Problem)

        proto_problem = self._writer.convert(problem)

        req = proto.PlanRequest(problem=proto_problem, timeout=timeout)
        response_stream = self._planner.planOneShot(req)
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

    def check_resources(self, host: str, port: int) -> bool:
        """Check if the port and host are available."""
        # Check if the host is available
        try:
            socket.gethostbyname(host)
        except socket.gaierror:
            raise UPException(
                "The host {} is not available. Please check the hostname.".format(host)
            )

        # Check if the port is available
        if port is not None:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((host, port))
            except OSError:
                raise UPException(
                    "The port {} is already in use. Please choose another port.".format(
                        port
                    )
                )

    def _grpc_server_on(self, channel) -> bool:
        try:
            grpc.channel_ready_future(channel).result(timeout=self._timeout_sec)
            return True
        except grpc.FutureTimeoutError:
            return False

    @classmethod
    def _get_available_port(cls) -> int:
        """Get available port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            return s.getsockname()[1]
