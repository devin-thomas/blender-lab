"""Generate public capability cards, tickets and matrices from one reviewed spec."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "experiments.json"


def validate(spec):
    if spec.get("schemaVersion") != 2:
        raise ValueError("Expected experiment specification schemaVersion 2")
    labs = spec["experiments"]
    expected = [f"BL-{number:03d}" for number in range(1, 97)]
    if [lab["id"] for lab in labs] != expected:
        raise ValueError("Catalog must preserve the ordered BL-001 through BL-096 IDs")
    cores = spec["coreTickets"]
    if [core["id"] for core in cores] != [f"CORE-{number:03d}" for number in range(1, 17)]:
        raise ValueError("Expected 16 stable core ticket IDs")
    for core in cores:
        if core.get("state") not in {"specified", "partial", "implemented"}:
            raise ValueError(f"{core['id']} has an unknown core implementation state")
        if not core.get("work") or not core.get("checks") or not core.get("recovery"):
            raise ValueError(f"{core['id']} needs work, checks and recovery")
    required = {"id", "title", "category", "moment", "mechanism", "api_leads", "controls",
                "interaction", "fixture", "ownership", "checks", "dependencies", "profiles",
                "budget", "fallback", "limitations", "milestone", "sources", "states",
                "implementation", "verification", "evidence", "card", "control", "api_qualification"}
    profiles = {profile.split(":", 1)[0] for profile in spec["executionProfiles"]}
    milestones = {milestone["id"] for milestone in spec["milestones"]}
    state_values = {
        "implementation": {"specified", "implementing", "implemented"},
        "automated": {"not-run", "passed", "bounded-outcomes-passed", "failed", "unavailable"},
        "editor": {"not-run", "operator-smoke-passed", "human-journey-passed", "failed", "unavailable"},
        "visual": {"not-run", "previews-inspected", "human-art-accepted", "failed", "unavailable"},
        "downstream": {"not-run", "named-receiver-passed", "failed", "unavailable"},
    }
    for lab in labs:
        if required - lab.keys():
            raise ValueError(f"{lab['id']} lacks {sorted(required - lab.keys())}")
        if len(lab["interaction"]) < 3 or not lab["controls"] or not lab["api_leads"]:
            raise ValueError(f"{lab['id']} needs a real journey, controls and API leads")
        if len(lab["checks"]["positive"]) < 2 or len(lab["checks"]["negative"]) < 2:
            raise ValueError(f"{lab['id']} needs outcome and failure checks")
        if any(not isinstance(value, str) or not value.strip() for value in [*lab["interaction"],
               *lab["checks"]["positive"], *lab["checks"]["negative"], *lab["api_leads"], *lab["limitations"]]):
            raise ValueError(f"{lab['id']} has an empty or invalid contract item")
        allowed_hosts = set(spec["allowedSourceHosts"])
        if not lab["sources"] or any(not source["url"].startswith("https://") or urlparse(source["url"]).hostname not in allowed_hosts
                                     or not source.get("scope") or not source.get("confidence") for source in lab["sources"]):
            raise ValueError(f"{lab['id']} needs primary-source references")
        if not lab["profiles"] or set(lab["profiles"]) - profiles:
            raise ValueError(f"{lab['id']} has unknown or empty execution profiles")
        if lab["milestone"] not in milestones:
            raise ValueError(f"{lab['id']} has an unknown milestone")
        if set(lab["states"]) != set(state_values):
            raise ValueError(f"{lab['id']} has an incomplete state contract")
        for key, allowed in state_values.items():
            if lab["states"][key] not in allowed:
                raise ValueError(f"{lab['id']} has unknown {key} state")
        if lab["implementation"] != "implemented" and any(lab["states"][key] not in {"not-run", "unavailable"}
                                                       for key in state_values if key != "implementation"):
            raise ValueError(f"{lab['id']} cannot claim outcome evidence before implementation")
        for item in lab["controls"]:
            if {"name", "type", "default", "range", "purpose"} - item.keys():
                raise ValueError(f"{lab['id']} has an incomplete control contract")
            if not item["name"] or not isinstance(item["range"], str) or not item["range"]:
                raise ValueError(f"{lab['id']} has an empty control name/range")
            default, kind = item["default"], item["type"]
            valid = ((kind == "number" and isinstance(default, (int, float)) and not isinstance(default, bool) and math.isfinite(default))
                     or (kind == "integer" and isinstance(default, int) and not isinstance(default, bool))
                     or (kind == "string" and isinstance(default, str))
                     or (kind == "boolean" and isinstance(default, bool))
                     or (kind == "enum" and isinstance(item.get("options"), list) and bool(item["options"])
                         and any(type(default) is type(option) and default == option
                                 or isinstance(default, (int, float)) and not isinstance(default, bool)
                                 and isinstance(option, (int, float)) and not isinstance(option, bool) and default == option
                                 for option in item["options"])))
            if not valid:
                raise ValueError(f"{lab['id']} control {item['name']} has a default/type mismatch")
            for bound in ("minimum", "maximum"):
                if bound in item and (kind not in {"number", "integer"} or not isinstance(item[bound], (int, float))
                                      or isinstance(item[bound], bool) or not math.isfinite(item[bound])):
                    raise ValueError(f"{lab['id']} has invalid numeric control bounds")
            if "minimum" in item and "maximum" in item and item["minimum"] > item["maximum"]:
                raise ValueError(f"{lab['id']} has reversed control bounds")
            if ("minimum" in item and default < item["minimum"]) or ("maximum" in item and default > item["maximum"]):
                raise ValueError(f"{lab['id']} control default is outside its bounds")
        if set(lab["budget"]) != {"preview", "qualification", "limits"} or not all(lab["budget"].values()):
            raise ValueError(f"{lab['id']} has incomplete execution budgets")
        if lab["implementation"] != lab["states"]["implementation"]:
            raise ValueError(f"{lab['id']} implementation states disagree")
        if lab["card"] != f"docs/experiments/{lab['id']}.md":
            raise ValueError(f"{lab['id']} card must use the stable generated path")
    graph = {entry["id"]: entry["dependencies"] for entry in [*cores, *labs]}
    visiting, visited = set(), set()

    def visit(identity):
        if identity not in graph:
            raise ValueError(f"Unknown dependency {identity}")
        if identity in visiting:
            raise ValueError(f"Dependency cycle at {identity}")
        if identity in visited:
            return
        visiting.add(identity)
        for dependency in graph[identity]:
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in graph:
        visit(identity)
    for route in spec["routes"]:
        if any(identity not in expected for identity in route["labs"]):
            raise ValueError(f"Route {route['title']} references an unknown lab")


def bullets(values):
    return "\n".join(f"- {value}" for value in values)


def dependency_links(lab, prefix):
    links = []
    for identity in lab["dependencies"]:
        path = f"{prefix}tickets/{identity}.md" if identity.startswith("CORE") else f"{prefix}docs/experiments/{identity}.md"
        links.append(f"[{identity}]({path})")
    return ", ".join(links) or "None"


def card(lab):
    controls = "\n".join(f"| {item['name']} | {item['type']} | {item['default']} | {item['range']} | {item['purpose']} |" for item in lab["controls"])
    sources = "\n".join(f"- [{source['scope']}]({source['url']}) - {source['confidence']}" for source in lab["sources"])
    states = "; ".join(f"{key}: `{value}`" for key, value in lab["states"].items())
    interaction = "\n".join(f"{number}. {step}" for number, step in enumerate(lab["interaction"], 1))
    return f"""# {lab['id']} - {lab['title']}

Generated from [specs/experiments.json](../../specs/experiments.json); edit the specification and regenerate.

**Category:** {lab['category']}. **Milestone:** {lab['milestone']}.

**The moment:** {lab['moment']}

## Mechanism and source leads

{lab['mechanism']}

{bullets(lab['api_leads'])}

API entries are implementation leads. {lab['api_qualification']} API member existence is narrower than lab implementation or outcome qualification.

## Try it

{interaction}

| Control | Type | Default | Bounds / choices | Purpose |
|---|---|---|---|---|
{controls}

These controls describe the target contract. Implemented controls use the actual sidebar/CLI documented in [OPERATIONS](../OPERATIONS.md); specified cards do not imply those controls already exist.

## Fixture, scope and reset

**Original fixture:** {lab['fixture']}

**Ownership:** {lab['ownership']}

## Qualification

{lab['checks'].get('evidence_scope', 'These are target acceptance requirements; each check requires its own actual result before promotion.')}

Positive outcomes:

{bullets(lab['checks']['positive'])}

Negative and recovery outcomes:

{bullets(lab['checks']['negative'])}

Execution profiles: {', '.join(f'`{profile}`' for profile in lab['profiles'])}.

Preview budget: {lab['budget']['preview']}

Qualification budget: {lab['budget']['qualification']}

Hard limit: {lab['budget']['limits']}

**Fallback:** {lab['fallback']}

Limits:

{bullets(lab['limitations'])}

## Delivery and evidence

Dependencies: {dependency_links(lab, '../../')}.

{states}.

Evidence summary: [BUILD_STATUS](../BUILD_STATUS.md). `not-run` is not a pass; future checks in this card remain acceptance requirements until a receipt is reviewed.

Tickets: [{lab['id']}-A](../../tickets/{lab['id']}-A.md), [{lab['id']}-B](../../tickets/{lab['id']}-B.md).

## Primary sources

{sources}
"""


def ticket(lab, phase):
    implement = phase == "A"
    heading = "Implement the editable capability" if implement else "Qualify outcomes and recovery"
    state = lab["implementation"] if implement else lab["verification"]
    deps = dependency_links(lab, "../")
    if not implement:
        deps += f", [{lab['id']}-A]({lab['id']}-A.md)"
    tasks = (lab["interaction"] + [f"Expose {control['name']}: {control['range']}; {control['purpose']}" for control in lab["controls"]]) if implement else lab["checks"]["positive"] + lab["checks"]["negative"]
    return f"""# {lab['id']}-{phase} - {heading}

Generated from [the specification](../specs/experiments.json). State: `{state}`.

## Problem and payoff

{lab['moment']}

Capability authority: [{lab['title']}](../docs/experiments/{lab['id']}.md). Milestone: {lab['milestone']}. Dependencies: {deps}.

## Work

{bullets(tasks)}

## Data boundary

Fixture: {lab['fixture']}

{lab['ownership']}

## Completion evidence

{'Deliver a scoped builder/operation, meaningful controls, an unavailable explanation for unsupported profiles, and a cheap inspectable preview. A source implementation does not complete the B ticket.' if implement else 'Run the declared outcomes on a recorded Blender build, inspect a cheap preview, exercise recovery, and record exact source/job/artifact identities. Editor, GPU, external and downstream gates remain separate.'}

{lab['checks'].get('evidence_scope', 'The listed checks remain target acceptance requirements until individually exercised.')}

Profiles: {', '.join(lab['profiles'])}. Budget: {lab['budget']['qualification']}. Limit: {lab['budget']['limits']}.

Fallback: {lab['fallback']}

{bullets(lab['limitations'])}

Current gate states: {json.dumps(lab['states'], sort_keys=True)}. Read [BUILD_STATUS](../docs/BUILD_STATUS.md); do not infer execution from this ticket's existence.
"""


def outputs(spec):
    labs, cores = spec["experiments"], spec["coreTickets"]
    result = {}
    result["catalog.json"] = json.dumps({"schemaVersion": 2, "testedBaseline": spec["testedBaseline"], "experiments": labs}, indent=2) + "\n"
    for lab in labs:
        result[lab["card"]] = card(lab)
        for phase in ("A", "B"):
            result[f"tickets/{lab['id']}-{phase}.md"] = ticket(lab, phase)
    for core in cores:
        deps = ", ".join(f"[{identity}]({identity}.md)" for identity in core["dependencies"]) or "None"
        result[f"tickets/{core['id']}.md"] = f"""# {core['id']} - {core['title']}

Generated from [the specification](../specs/experiments.json). State: `{core['state']}`. Dependencies: {deps}.

## Problem

{core['problem']}

## Contract

{bullets(core['work'])}

## Acceptance

{bullets(core['checks'])}

## Failure and recovery

{core['recovery']}

## Evidence boundary

{core['evidence']}
"""
    categories = list(dict.fromkeys(lab["category"] for lab in labs))
    index = ["# Capability catalog", "", "96 scoped capability contracts span Blender authoring, production, interchange and automation. Generated from [the reviewed specification](../../specs/experiments.json). Implementation and qualification are separate; a specified card is an unavailable capability with a real plan, not shipped behavior.", "", "[Capability matrix](../CAPABILITY_MATRIX.md), [milestones](../MILESTONES.md), [roadmap](../ROADMAP.md), [ticket board](../../tickets/README.md)."]
    for category in categories:
        index.extend(["", f"## {category}", "", "| ID | Capability | User payoff | Implementation | Qualification |", "|---|---|---|---|---|"])
        for lab in labs:
            if lab["category"] == category:
                index.append(f"| [{lab['id']}]({lab['id']}.md) | {lab['title']} | {lab['moment']} | {lab['implementation']} | {lab['verification']} |")
    result["docs/experiments/INDEX.md"] = "\n".join(index) + "\n"
    matrix = ["# Capability matrix", "", "Generated from [specs/experiments.json](../specs/experiments.json). Profiles are requirements, not evidence that a host was qualified. API leads are recorded separately in each card. Budgets are original planning caps, not measured performance promises.", "", "| ID | Category | Mechanism | Profiles | Milestone | Implementation | Automated / editor / visual / downstream |", "|---|---|---|---|---|---|---|"]
    for lab in labs:
        gate = " / ".join(lab["states"][key] for key in ("automated", "editor", "visual", "downstream"))
        matrix.append(f"| [{lab['id']}](experiments/{lab['id']}.md) | {lab['category']} | {lab['mechanism']} | {', '.join(lab['profiles'])} | {lab['milestone']} | {lab['implementation']} | {gate} |")
    matrix.extend(["", "## Profile boundaries", "", bullets(spec["executionProfiles"]), "", "## Category coverage", "", "| Category | Contracts |", "|---|---|"])
    matrix.extend(f"| {category} | {count} |" for category, count in Counter(lab["category"] for lab in labs).items())
    result["docs/CAPABILITY_MATRIX.md"] = "\n".join(matrix) + "\n"
    milestones = ["# Delivery milestones", "", "A milestone completes only when its selected implementation, outcome, recovery and appropriate editor/visual/downstream gates have evidence. The catalog's breadth is a plan, not a claim that all 96 labs run today.", ""]
    for milestone in spec["milestones"]:
        included = [lab["id"] for lab in labs if lab["milestone"] == milestone["id"]]
        milestones.extend([f"## {milestone['id']} - {milestone['title']}", "", milestone["payoff"], "", f"Scope: {', '.join(included)}.", "", "Exit gates:", "", bullets(milestone["gates"]), "", f"Unavailable behavior: {milestone['fallback']}", ""])
    result["docs/MILESTONES.md"] = "\n".join(milestones)
    roadmap = ["# Living Blender roadmap", "", "The authoritative [specification](../specs/experiments.json) defines 96 substantive capability contracts, 16 core delivery tickets and two tickets per lab. [Catalog](experiments/INDEX.md), [matrix](CAPABILITY_MATRIX.md), and [milestones](MILESTONES.md) expose the scope and actual states. The six original labs remain the verified foundation; expansion is explicitly staged.", "", "## Production routes", ""]
    for route in spec["routes"]:
        roadmap.extend([f"### {route['title']}", "", route["moment"], "", " -> ".join(f"[{identity}](experiments/{identity}.md)" for identity in route["labs"]), "", route["gate"], ""])
    roadmap.extend(["## Foundation work", "", "Core delivery is a real work stream rather than invisible glue:", "", "| Ticket | Contract | State |", "|---|---|---|"])
    roadmap.extend(f"| [{core['id']}](../tickets/{core['id']}.md) | {core['title']} | {core['state']} |" for core in cores)
    roadmap.extend(["", "## Sequencing and evidence", "", "Follow the acyclic lab/core dependencies in the source. Qualification never advances merely because an API member exists or an A ticket is merged. Start with small original fixtures and cheap previews; use explicit profiles for expensive simulations, disk-heavy caches, GPU qualification and external tools. Every unimplemented catalog entry explains its missing mechanism and next gate. The local no-cloud route stays useful throughout expansion.", "", "## Change policy", "", "Edit the specification, run `python scripts/generate_catalog.py`, then `python scripts/generate_catalog.py --check`. Regeneration preserves stable IDs and statuses. Add outcome/recovery receipts before changing evidence states. Keep private plans, raw personal media and private dependencies outside the public source and package."])
    result["docs/ROADMAP.md"] = "\n".join(roadmap) + "\n"
    tickets = ["# Implementation and qualification queue", "", "Generated from [the authoritative spec](../specs/experiments.json). 16 core tickets plus 192 lab tickets. A implements the inspectable capability; B proves bounded outcomes and recovery. The lab/core dependency graph is checked for unknown nodes and cycles by the generator.", "", "## Core", "", "| ID | Contract | State |", "|---|---|---|"]
    tickets.extend(f"| [{core['id']}]({core['id']}.md) | {core['title']} | {core['state']} |" for core in cores)
    tickets.extend(["", "## Labs", "", "| Capability | Implement | Qualify | Milestone |", "|---|---|---|---|"])
    tickets.extend(f"| {lab['id']} {lab['title']} | [{lab['implementation']}]({lab['id']}-A.md) | [{lab['verification']}]({lab['id']}-B.md) | {lab['milestone']} |" for lab in labs)
    result["tickets/README.md"] = "\n".join(tickets) + "\n"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when generated files drift; do not write")
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    validate(spec)
    drift = []
    for relative, content in outputs(spec).items():
        path = ROOT / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            drift.append(relative)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if args.check and drift:
        raise SystemExit("Generated catalog drift:\n" + "\n".join(drift))
    print(f"{'Checked' if args.check else 'Generated'} 96 labs, 192 lab tickets, 16 core tickets and matrices; DAG valid")


if __name__ == "__main__":
    main()
