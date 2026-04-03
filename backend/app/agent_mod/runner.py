from __future__ import annotations

import argparse

from app.agent_mod.config import BACKEND_DIR, ROOT_DIR
from app.agent_mod.gates import gate_g1, gate_g2, gate_g6
from app.agent_mod.models import GateResult, RunContext
from app.agent_mod.probes import gate_g4
from app.agent_mod.runtime import gate_g3
from app.agent_mod.snapshot import gate_g5


def print_gate(gate: GateResult) -> None:
    print(f"\n[{gate.gate}] {'PASS' if gate.passed else 'FAIL'}")
    for c in gate.checks:
        print(f" - {'OK' if c.passed else 'KO'} | {c.name} | {c.details}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PROMETEO Agent Mod V1")
    parser.add_argument("--files", nargs="*", default=[], help="file modificati")
    parser.add_argument("--skip-runtime", action="store_true", help="salta G3")
    parser.add_argument("--snapshot", action="store_true", help="forza snapshot")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    context = RunContext(
        root_dir=str(ROOT_DIR),
        backend_dir=str(BACKEND_DIR),
        files=args.files,
        skip_runtime=args.skip_runtime,
        snapshot=args.snapshot,
    )

    gates: list[GateResult] = []

    g1 = gate_g1(context)
    gates.append(g1)
    print_gate(g1)

    g2 = gate_g2(context)
    gates.append(g2)
    print_gate(g2)

    g3 = gate_g3(context)
    gates.append(g3)
    print_gate(g3)

    g4 = gate_g4(context)
    gates.append(g4)
    print_gate(g4)

    g5 = gate_g5(context, gates)
    gates.append(g5)
    print_gate(g5)

    g6 = gate_g6(gates[:-1])
    gates.append(g6)
    print_gate(g6)

    return 0 if g6.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
