from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from io import StringIO
import json
from pathlib import Path
import shlex
import subprocess
from tempfile import TemporaryDirectory
from typing import Any, Callable, List, TypeVar
from fsspec import AbstractFileSystem

from commands import OpenInterpreterCommand
from runners import DockerWorker
from utils import LocalBasedFS


@dataclass(frozen=True)
class Executing:
    kill: Callable[[], None]
    wait: Callable[[], None]


@dataclass(frozen=True)
class Environment(ABC):
    get_fs: Callable[[], AbstractFileSystem]
    shutdown: Callable[[], None]
    # List[str], (str -> Any) | None -> None
    exec: Callable[[List[str], Callable[[bytes], Any] | None], None]

    @contextmanager
    def use(self):
        yield
        self.shutdown()

    
def make_docker_environment(worker: DockerWorker) -> Callable[[str], Environment]:
    def make(environment_name: str) -> Environment:
        base_dir = TemporaryDirectory()
        input_dir = base_dir.name / Path("input")
        output_dir = base_dir.name / Path("output")
        input_dir.mkdir(parents=True)
        output_dir.mkdir(parents=True)

        run_cmd = [
            "docker", "run", "-td",
            "-v", f"{input_dir}:/input",
            "-v", f"{output_dir}:/output",
            "--name", environment_name, worker.get_image_tag(),
        ]
        start_process = subprocess.run(
            run_cmd,
            stdout=subprocess.PIPE)
        assert start_process.stdout is not None
        container_pid = start_process.stdout.decode().strip()

        def exec(args: List[str], on_stdouterr: Callable[[bytes], Any] | None):
            def output(o: bytes):
                if on_stdouterr is not None:
                    on_stdouterr(o)

            cmd = ["docker", "exec", container_pid, "python", "-m", "worker.run", *args]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            assert p.stdout is not None

            while p.poll() is None:
                output(p.stdout.readline())
            output(p.stdout.read())

        def shutdown():
            subprocess.run(["docker", "kill", container_pid])
            base_dir.cleanup()

        return Environment(
            get_fs=lambda: LocalBasedFS(base_dir.name),
            exec=exec,
            shutdown=shutdown
        )

    return make


