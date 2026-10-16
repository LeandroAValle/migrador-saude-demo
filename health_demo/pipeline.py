"""Illustrative migration state machine with no real network or patient data."""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

SEED = 20261016
SERVICES = ("Unidades", "Profissionais", "Equipes", "Atendimentos")
COUNTS = (8, 30, 12, 150)
PERIOD = "2026-09"


class WriteGuardError(RuntimeError):
    pass


def ensure_writable(environment: str) -> None:
    """Demonstrate fail-closed write authorization, even for the fake sender."""
    if environment != "sandbox":
        raise WriteGuardError("Ambiente somente leitura: envio bloqueado antes da operação")


def source_records() -> list[dict]:
    rng = random.Random(SEED)
    result = []
    for service, count in zip(SERVICES, COUNTS, strict=True):
        for index in range(1, count + 1):
            result.append({
                "key": f"{service[:3].upper()}-{index:04d}",
                "service": service,
                "reference": PERIOD,
                "unit": ("UBS Aurora", "UBS Horizonte", "UBS Vale")[index % 3],
                "requiredCode": "" if index % 31 == 0 else f"REF-{index:04d}",
                "syntheticValue": rng.randint(1, 9),
            })
    return result


def validate(record: dict) -> str | None:
    if not record["requiredCode"]:
        return "Referência obrigatória ausente na origem fictícia"
    return None


def simulate_final_result(record: dict) -> tuple[str, str]:
    """Acceptance is known only after the simulated consultation step."""
    sequence = int(record["key"].split("-")[-1])
    if sequence % 19 == 0:
        return "ERRO", "Destino simulado rejeitou a referência para revisão"
    return "SUCESSO", "Aceito após consulta simulada do lote"


def build_snapshot(environment: str = "sandbox") -> dict:
    ensure_writable(environment)
    source = source_records()
    if len({record["key"] for record in source}) != len(source):
        raise ValueError("Chaves duplicadas na origem fictícia")

    control = []
    for record in source:
        issue = validate(record)
        if issue:
            history = ["EXTRAIDO", "ERRO"]
            result = "ERRO"
        else:
            history = ["EXTRAIDO", "PENDENTE", "ENVIADO"]
            result, issue = simulate_final_result(record)
            history.append(result)
        control.append({
            "key": record["key"],
            "service": record["service"],
            "unit": record["unit"],
            "status": result,
            "history": history,
            "message": issue,
            "payloadPrepared": not bool(validate(record)),
        })

    status = Counter(item["status"] for item in control)
    by_service = [{
        "service": service,
        "total": sum(item["service"] == service for item in control),
        "success": sum(item["service"] == service and item["status"] == "SUCESSO" for item in control),
        "errors": sum(item["service"] == service and item["status"] == "ERRO" for item in control),
    } for service in SERVICES]
    ledger = [
        {"operation": "Gerar", "state": "CONCLUIDO", "processed": len(source), "total": len(source), "checkpoint": "Origem fictícia lida e validada"},
        {"operation": "Enviar", "state": "CONCLUIDO", "processed": sum(item["payloadPrepared"] for item in control), "total": sum(item["payloadPrepared"] for item in control), "checkpoint": "Lotes aceitos pelo simulador; ainda sem sucesso final"},
        {"operation": "Consultar", "state": "CONCLUIDO", "processed": sum(item["payloadPrepared"] for item in control), "total": sum(item["payloadPrepared"] for item in control), "checkpoint": "Resultados finais conciliados por registro"},
    ]
    snapshot = {
        "schemaVersion": 1,
        "period": PERIOD,
        "dataOrigin": "synthetic",
        "destination": "offline simulator",
        "environment": environment,
        "writeGuard": "sandbox only",
        "metrics": {
            "total": len(source),
            "success": status["SUCESSO"],
            "errors": status["ERRO"],
            "prepared": sum(item["payloadPrepared"] for item in control),
            "services": len(SERVICES),
        },
        "byService": by_service,
        "ledger": ledger,
        "control": control,
    }
    assert snapshot["metrics"]["total"] == snapshot["metrics"]["success"] + snapshot["metrics"]["errors"]
    assert all(item["processed"] == item["total"] for item in ledger)
    return snapshot


def export_snapshot(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_snapshot(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path
