import os
from io import RawIOBase
from pathlib import Path
import shlex
from typing import Any, Callable, List

from fsspec import AbstractFileSystem

from environment import Environment
from e2b import Sandbox

from runners import DockerWorker
from utils import get_ancestor_dirs


class E2BFile(RawIOBase):
    def __init__(self, sandbox: Sandbox, path: os.PathLike, mode: str):
        self.sandbox = sandbox
        self.path = path
        self.mode = mode
    
    def read(self, size=-1) -> bytes:
        bs = self.sandbox.download_file(str(self.path))
        if size == -1:
            return bs
        return bs[:size]
    
    def readinto(self, b):
        bs = self.sandbox.download_file(str(self.path))
        b[:len(bs)] = bs
        return bs

    def write(self, b):
        self.sandbox.filesystem.write_bytes(str(self.path), b)
        return len(b)
    
    def readable(self) -> bool:
        return "r" in self.mode or "+" in self.mode

    def writable(self) -> bool:
        return "w" in self.mode or "+" in self.mode or "a" in self.mode


class E2BFilesystem(AbstractFileSystem):
    def __init__(self, sandbox: Sandbox, base: os.PathLike = Path("")):
        self._sandbox = sandbox
        self.base = base

    def _full_path(self, path: str) -> str:
        return f"{self._sandbox.get_hostname()}/{self.base}/{path}"
    
    def open(self, path: str, mode: str = 'r', **kwargs: Any) -> Any:
        return E2BFile(self._sandbox, self.base / Path(path), mode)
    
    def ls(self, path='', detail=True, **kwargs):
        return [p.name for p in self._sandbox.filesystem.list(path)]

    def mkdir(self, path: str, create_parents=True, **kwargs):
        if create_parents:
            for adir in get_ancestor_dirs(Path(path)):
                self._sandbox.filesystem.make_dir(str(adir))
        self._sandbox.filesystem.make_dir(path)
    
    def exists(self, path: str, **kwargs) -> bool:
        p = Path(path)
        result = path in self.ls(str(p.parent))
        print(result)
        return result
    

def make_e2b_terminal_environment(worker: DockerWorker) -> Callable[[str], Environment]:
    def make(environment_name: str) -> Environment:
        sandbox = Sandbox(template=worker.get_image_tag(), cwd="/")
        fs = E2BFilesystem(sandbox)
        fs.mkdir("/input", create_parents=True)
        fs.mkdir("/output", create_parents=True)
        messages = []
        # print("LS:", list(map(lambda k: str(k), fs.ls("/output"))))

        def exec(cmd: List[str], on_stdouterr: Callable[[bytes], None] | None):
            def output(o: bytes):
                if on_stdouterr is not None:
                    on_stdouterr(o)

            sandbox.process.start_and_wait(
                " ".join(map(shlex.quote, cmd)),
                on_stdout=lambda out: output(out.line.encode()),
                on_stderr=lambda out: output(out.line.encode())
            )

        def shutdown():
            Sandbox.kill(sandbox_id=sandbox.id)
            sandbox.close()

        return Environment(
            get_fs=lambda: E2BFilesystem(sandbox),
            shutdown=shutdown,
            exec=exec
        )
    
    return make
