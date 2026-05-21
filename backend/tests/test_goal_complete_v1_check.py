from __future__ import annotations

import shutil
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_executable(path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_goal_complete_v1_check_does_not_require_local_scadenze_file(tmp_path):
    repo = tmp_path / "repo"
    scripts_dir = repo / "scripts"
    session_dir = repo / "data" / "local_reports" / "session_memory"
    fake_bin = tmp_path / "bin"
    scripts_dir.mkdir(parents=True)
    session_dir.mkdir(parents=True)
    fake_bin.mkdir()

    shutil.copyfile(
        str(REPO_ROOT / "scripts/goal_complete_v1_check.sh"),
        scripts_dir / "goal_complete_v1_check.sh",
    )

    _write_executable(
        fake_bin / "git",
        """#!/usr/bin/env bash
set -euo pipefail
if [ "$1" = "ls-files" ]; then
  exit 0
fi
if [ "$1" = "check-ignore" ]; then
  exit 0
fi
exit 0
""",
    )
    _write_executable(fake_bin / "python3", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(fake_bin / "make", "#!/usr/bin/env bash\nexit 0\n")
    _write_executable(fake_bin / "npm", "#!/usr/bin/env bash\nexit 0\n")

    result = subprocess.run(
        ["/bin/bash", str(scripts_dir / "goal_complete_v1_check.sh")],
        cwd=repo,
        env={
            "PATH": f"{fake_bin}:/usr/bin:/bin",
            "PROMETEO_GOAL_TMPDIR": str(tmp_path / "goal_tmp"),
        },
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "session memory directory present" in result.stdout
    assert "RESULT=PASS" in result.stdout
