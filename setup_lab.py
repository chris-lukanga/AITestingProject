"""First-run dependency setup, followed by the two-site launcher."""
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ('fastapi', 'uvicorn', 'httpx', 'dotenv', 'requests', 'pydantic', 'google.genai', 'tavily')


def main():
    if sys.version_info < (3, 12):
        print('Please install Python 3.12 or later, then run Start-Lab.cmd again.')
        return 1
    missing = []
    for name in REQUIRED:
        try:
            if importlib.util.find_spec(name) is None:
                missing.append(name)
        except ModuleNotFoundError:
            missing.append(name)
    if missing:
        import venv
        directory = ROOT / '.venv'
        python = directory / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
        print('First launch: installing the lab dependencies. This needs an internet connection.', flush=True)
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(directory)
        result = subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(ROOT / 'requirements.txt')], cwd=ROOT)
        if result.returncode:
            print('Setup could not finish. Check the connection and run the launcher again.')
            return result.returncode
        return subprocess.call([str(python), str(ROOT / 'run_lab.py')], cwd=ROOT)
    import run_lab
    return run_lab.main()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
