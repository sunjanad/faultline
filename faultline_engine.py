
"""
Faultline testing engine.

The built-in systems contain deliberate defects for demonstration.
This is a controlled test lab, not a general-purpose code scanner.
"""

from dataclasses import dataclass, field
from collections import Counter
import hashlib
import json
import random
import time


VERSION = "0.3.0"


def fingerprint(value):
    """Return a stable fingerprint for a test case."""
    raw = json.dumps(value, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def complexity(value):
    """
    Estimate structural and numeric complexity.

    Dictionary keys are excluded because the keys describe the
    fixed input structure, not the values being minimized.
    This score is a heuristic, not a measure of readability.
    """
    if isinstance(value, bool):
        return 1

    if isinstance(value, dict):
        return sum(complexity(v) for v in value.values())

    if isinstance(value, list):
        return len(value) + sum(complexity(v) for v in value)

    if isinstance(value, (int, float)):
        return abs(value)

    if isinstance(value, str):
        return len(value)

    if value is None:
        return 0

    return len(str(value))


@dataclass
class Failure:
    property_name: str
    original_case: dict
    minimized_case: dict
    explanation: str
    original_complexity: float
    minimized_complexity: float
    shrink_attempts: int


@dataclass
class ExperimentResult:
    subject: str
    seed: int
    requested_tests: int
    unique_cases_checked: int
    passing_cases: int
    failing_cases: int = 0
    failure_records: list = field(default_factory=list)
    property_counts: Counter = field(default_factory=Counter)
    elapsed_seconds: float = 0.0


# --------------------------------------------------
# CONTROLLED SYSTEMS WITH DELIBERATE DEFECTS
# --------------------------------------------------

def shipping_price(distance, weight, express):
    if distance < 0 or weight < 0:
        raise ValueError(
            "Distance and weight must be nonnegative."
        )

    price = 4.0 + 0.7 * distance + 0.35 * weight

    if express:
        price *= 1.8

    # Deliberate defect.
    if distance > 100:
        price *= 0.55

    return round(price, 2)


def scheduling_score(priority, duration):
    if priority < 0 or duration < 0:
        raise ValueError("Inputs must be nonnegative.")

    score = 10 * priority - 0.25 * duration

    # Deliberate defect.
    if priority >= 8:
        score -= 25

    return score


def allocate_resources(capacity, demands):
    if capacity < 0 or any(d < 0 for d in demands):
        raise ValueError("Inputs must be nonnegative.")

    allocations = []
    remaining = capacity

    for demand in demands:
        # Deliberate defect.
        if demand > remaining and demand > capacity / 2:
            allocation = demand
        else:
            allocation = min(demand, remaining)

        allocations.append(allocation)
        remaining -= allocation

    return allocations


# --------------------------------------------------
# PROPERTY CHECKS
# --------------------------------------------------

def check_shipping(case):
    low = case["distance_low"]
    high = case["distance_high"]
    weight = case["weight"]
    express = case["express"]

    if min(low, high, weight) < 0 or low > high:
        return [{
            "property": "valid_inputs",
            "message": (
                "Inputs must be nonnegative and distances ordered."
            ),
        }]

    p_low = shipping_price(low, weight, express)
    p_high = shipping_price(high, weight, express)

    if p_high < p_low:
        return [{
            "property": "distance_monotonicity",
            "message": (
                f"Distance increased from {low} to {high}, "
                f"but price fell from ${p_low:.2f} "
                f"to ${p_high:.2f}."
            ),
        }]

    return []


def check_scheduling(case):
    low = case["priority_low"]
    high = case["priority_high"]
    duration = case["duration"]

    if min(low, high, duration) < 0 or low > high:
        return [{
            "property": "valid_inputs",
            "message": (
                "Inputs must be nonnegative and priorities ordered."
            ),
        }]

    s_low = scheduling_score(low, duration)
    s_high = scheduling_score(high, duration)

    if s_high < s_low:
        return [{
            "property": "priority_monotonicity",
            "message": (
                f"Priority increased from {low} to {high}, "
                f"but score fell from {s_low:.2f} "
                f"to {s_high:.2f}."
            ),
        }]

    return []


def check_resources(case):
    capacity = case["capacity"]
    demands = case["demands"]

    if capacity < 0 or any(d < 0 for d in demands):
        return [{
            "property": "valid_inputs",
            "message": "Capacity and demands must be nonnegative.",
        }]

    allocations = allocate_resources(capacity, demands)
    problems = []

    if sum(allocations) > capacity:
        problems.append({
            "property": "capacity_respected",
            "message": (
                f"Total allocation {sum(allocations)} exceeds "
                f"capacity {capacity}. Allocations: {allocations}."
            ),
        })

    if any(a > d for a, d in zip(allocations, demands)):
        problems.append({
            "property": "demand_respected",
            "message": f"Allocations {allocations} exceed a demand.",
        })

    if any(a < 0 for a in allocations):
        problems.append({
            "property": "nonnegative_allocations",
            "message": f"Negative allocation found: {allocations}.",
        })

    return problems


# --------------------------------------------------
# TEST GENERATORS
# --------------------------------------------------

def generate_shipping(rng):
    boundaries = [0, 1, 2, 10, 50, 99, 100, 101, 102, 150, 200]

    if rng.random() < 0.45:
        low = rng.choice(boundaries)
        high = rng.choice([x for x in boundaries if x >= low])
    else:
        low = rng.randint(0, 200)
        high = rng.randint(low, 250)

    return {
        "distance_low": low,
        "distance_high": high,
        "weight": rng.choice(
            [0, 1, 5, 20, rng.randint(0, 100)]
        ),
        "express": rng.choice([False, True]),
    }


def generate_scheduling(rng):
    boundaries = [0, 1, 2, 7, 8, 9, 10, 20]

    if rng.random() < 0.5:
        low = rng.choice(boundaries)
        high = rng.choice([x for x in boundaries if x >= low])
    else:
        low = rng.randint(0, 20)
        high = rng.randint(low, 25)

    return {
        "priority_low": low,
        "priority_high": high,
        "duration": rng.choice(
            [0, 1, 10, 60, 120, rng.randint(0, 200)]
        ),
    }


def generate_resources(rng):
    capacity = rng.choice(
        [0, 1, 2, 5, 10, 20, rng.randint(0, 100)]
    )

    demands = [
        rng.choice([
            0,
            1,
            2,
            capacity // 2,
            capacity,
            capacity + 1,
            rng.randint(0, capacity + 10),
        ])
        for _ in range(rng.randint(1, 6))
    ]

    return {"capacity": capacity, "demands": demands}


SUBJECTS = {
    "Shipping price": {
        "description": (
            "Increasing distance should not lower price."
        ),
        "generate": generate_shipping,
        "check": check_shipping,
        "seeded": [{
            "distance_low": 100,
            "distance_high": 101,
            "weight": 0,
            "express": False,
        }],
    },
    "Scheduling rule": {
        "description": (
            "Increasing priority should not lower score."
        ),
        "generate": generate_scheduling,
        "check": check_scheduling,
        "seeded": [{
            "priority_low": 7,
            "priority_high": 8,
            "duration": 0,
        }],
    },
    "Resource allocation": {
        "description": (
            "Total allocation must not exceed capacity."
        ),
        "generate": generate_resources,
        "check": check_resources,
        "seeded": [{
            "capacity": 10,
            "demands": [8, 8],
        }],
    },
}


# --------------------------------------------------
# COUNTEREXAMPLE SHRINKING
# --------------------------------------------------

def numeric_reductions(number):
    """Generate smaller nonnegative numeric values."""
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        return []

    candidates = [0, 1, number / 2, number - 1]
    output = []

    for value in candidates:
        if isinstance(number, int):
            value = int(value)

        if 0 <= value < number and value not in output:
            output.append(value)

    return output


def simplify_candidates(value):
    """Generate structural and numeric simplifications."""
    if isinstance(value, dict):
        for key, old in value.items():
            for smaller in numeric_reductions(old):
                candidate = dict(value)
                candidate[key] = smaller
                yield candidate

            for smaller in simplify_candidates(old):
                candidate = dict(value)
                candidate[key] = smaller
                yield candidate

    elif isinstance(value, list):
        if len(value) > 1:
            for i in range(len(value)):
                yield value[:i] + value[i + 1:]

        for i, old in enumerate(value):
            for smaller in numeric_reductions(old):
                candidate = list(value)
                candidate[i] = smaller
                yield candidate

            for smaller in simplify_candidates(old):
                candidate = list(value)
                candidate[i] = smaller
                yield candidate


def shrink_case(case, check, property_name, max_attempts=1000):
    """
    Greedily simplify a failing case while preserving its property
    violation. The attempt limit counts every candidate examined.
    """
    current = json.loads(json.dumps(case))
    attempts = 0

    def preserves(candidate):
        try:
            return any(
                issue["property"] == property_name
                for issue in check(candidate)
            )
        except (ValueError, TypeError, KeyError, ZeroDivisionError):
            return False

    while attempts < max_attempts:
        old_complexity = complexity(current)
        improved = False

        for candidate in simplify_candidates(current):
            if attempts >= max_attempts:
                break

            attempts += 1

            if complexity(candidate) >= old_complexity:
                continue

            if preserves(candidate):
                current = candidate
                improved = True
                break

        if not improved:
            break

    return current, attempts


# --------------------------------------------------
# EXPERIMENT RUNNER
# --------------------------------------------------

def run_experiment(
    subject_name,
    number_of_tests=500,
    seed=42,
    shrink_limit=1000,
):
    if subject_name not in SUBJECTS:
        raise ValueError("Unknown test subject.")

    if not 1 <= number_of_tests <= 10000:
        raise ValueError(
            "Test count must be between 1 and 10000."
        )

    if shrink_limit < 1:
        raise ValueError("Shrink limit must be at least 1.")

    subject = SUBJECTS[subject_name]
    rng = random.Random(seed)

    result = ExperimentResult(
        subject=subject_name,
        seed=seed,
        requested_tests=number_of_tests,
        unique_cases_checked=0,
        passing_cases=0,
    )

    cases = list(subject["seeded"])
    cases.extend(
        subject["generate"](rng)
        for _ in range(number_of_tests)
    )

    seen = set()
    start = time.perf_counter()

    for case in cases:
        key = fingerprint(case)

        if key in seen:
            continue

        seen.add(key)
        result.unique_cases_checked += 1

        problems = subject["check"](case)

        if not problems:
            result.passing_cases += 1
            continue

        # Count each distinct failing input once, even if it violates
        # more than one property.
        result.failing_cases += 1

        for problem in problems:
            name = problem["property"]
            result.property_counts[name] += 1

            minimized, attempts = shrink_case(
                case,
                subject["check"],
                name,
                max_attempts=shrink_limit,
            )

            result.failure_records.append(
                Failure(
                    property_name=name,
                    original_case=case,
                    minimized_case=minimized,
                    explanation=problem["message"],
                    original_complexity=complexity(case),
                    minimized_complexity=complexity(minimized),
                    shrink_attempts=attempts,
                )
            )

    result.elapsed_seconds = time.perf_counter() - start
    return result


# --------------------------------------------------
# REPORT SERIALIZATION
# --------------------------------------------------

def result_to_dict(result):
    property_violations = sum(result.property_counts.values())

    return {
        "tool": "Faultline",
        "version": VERSION,
        "subject": result.subject,
        "seed": result.seed,
        "requested_tests": result.requested_tests,
        "unique_cases_checked": result.unique_cases_checked,
        "passing_cases": result.passing_cases,
        "failing_cases": result.failing_cases,
        "property_violation_records": property_violations,
        "elapsed_seconds": round(result.elapsed_seconds, 4),
        "property_counts": dict(result.property_counts),
        "failures": [
            {
                "property": failure.property_name,
                "original_case": failure.original_case,
                "minimized_case": failure.minimized_case,
                "explanation": failure.explanation,
                "original_complexity": failure.original_complexity,
                "minimized_complexity": failure.minimized_complexity,
                "shrink_attempts": failure.shrink_attempts,
            }
            for failure in result.failure_records
        ],
        "limitations": [
            "Built-in example systems contain deliberate defects.",
            "Results depend on the specified properties.",
            "Shrinking is greedy and bounded.",
            "Complexity is a heuristic, not a human readability measure.",
            "Passing tests do not prove defect-free behavior.",
            "Runtime measures experiment checking and shrinking, "
            "not the initial generation of all test cases.",
        ],
    }
