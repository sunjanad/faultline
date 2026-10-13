# Faultline

**Automated Counterexample Discovery Through Property-Based Testing**

Faultline is a testing tool that searches for inputs that cause software systems to violate defined behavioral properties. When it discovers a failure, it attempts to simplify the input into a smaller counterexample that makes the underlying problem easier to understand.

Instead of relying only on manually written test cases, Faultline generates a diverse set of inputs, evaluates them against specified properties, and records the failures it finds.

## Why Faultline?

Software can behave unexpectedly even when individual components appear to work correctly. Manually selected test cases may miss unusual inputs, boundary conditions, or interactions between values.

Faultline explores inputs systematically through a combination of predefined boundary cases and randomized generation. When a generated input violates a property, the tool attempts to reduce its complexity while preserving the failure.

The goal is not just to detect a failure, but to make that failure easier to investigate.

## How It Works

Faultline follows an experiment pipeline:

1. **Generate inputs:** Produce test cases using predefined boundary values and randomized values.
2. **Evaluate properties:** Run each unique input against the behavioral rules defined for the selected system.
3. **Detect violations:** Record inputs that violate one or more properties.
4. **Minimize counterexamples:** Attempt to simplify failing inputs while keeping the selected violation reproducible.
5. **Report results:** Display experiment metrics and failure records so users can investigate the results.

### Counterexample Simplification

A large failing input can be difficult to interpret. Faultline uses a bounded, greedy shrinking process to search for a simpler input that still violates the same property.

Its complexity score provides a heuristic for comparing inputs. It is not a direct measurement of human readability, and the shrinking process does not guarantee a globally minimal result.

## Built-In Demonstration Systems

Faultline currently includes three controlled demonstration systems. Each contains deliberately seeded defects so that the testing process can be evaluated against known failure conditions.

### 1. Shipping Price Calculator

Evaluates a shipping-price calculation using distance, weight, and express delivery.

Properties include valid inputs and distance monotonicity. The system includes a deliberately seeded pricing defect at high distances.

### 2. Scheduling Priority Rule

Evaluates a scheduling score using task priority and duration.

Properties include valid inputs and priority monotonicity. The system includes a deliberately seeded defect affecting high-priority tasks.

### 3. Resource Allocation

Evaluates how resources are allocated across a sequence of demands.

Properties include capacity limits, demand limits, and nonnegative allocations. The system contains a deliberately seeded allocation defect that can produce invalid results.

These systems are controlled test subjects for demonstrating Faultline's capabilities. They are not evidence that the tool has been validated against arbitrary real-world software.

## Understanding Experiment Results

Faultline reports several metrics:

- **Unique cases:** The number of distinct inputs evaluated.
- **Passing cases:** The number of unique inputs that passed all checked properties.
- **Failing cases:** The number of unique inputs that violated at least one property.
- **Property violations:** The total number of recorded property-violation instances. One input may violate multiple properties.
- **Runtime:** The measured time spent checking inputs and processing failures, including shrinking where applicable.

The distinction between failing cases and property violations matters: one failing input can produce more than one violation.

## Limitations

Faultline is an experimental prototype, and its current scope has important limitations:

- Testing is limited to the built-in demonstration systems and their implemented properties.
- Results depend on the properties defined for each system. An incorrect or incomplete property may fail to detect a defect.
- Randomized test generation can produce different inputs under different seeds.
- Counterexample shrinking is greedy and bounded, so it may not find the smallest possible failing input.
- The complexity score is a heuristic rather than a definitive measure of how understandable a counterexample is.
- Passing tests do not prove that a system is defect-free.
- The built-in systems contain deliberate defects for controlled demonstration and evaluation.

## Try Faultline

**Live application:** https://faultline-lab.streamlit.app/

The application includes an Overview, Experiment Lab, Failure Explorer, and Evaluation page. Users can run experiments on the built-in systems, inspect detected failures, compare original and minimized inputs, and review experiment results.

For reproducible comparisons, use the same system, experiment budget, and random seed.

## Project Status

Faultline is an actively developed prototype focused on automated test generation, behavioral property checking, and counterexample simplification.

The current implementation prioritizes transparent experiments and inspectable failure records over unrestricted testing of arbitrary programs.
