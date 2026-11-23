import numpy as np
import matplotlib.pyplot as plt


def trimf(x, a, b, c):
    """Triangle with feet a and c and peak b. a == b or b == c makes a shoulder."""
    x = np.asarray(x, dtype=float)
    left = np.ones_like(x) if a == b else np.clip((x - a) / (b - a), 0, 1)
    right = np.ones_like(x) if b == c else np.clip((c - x) / (c - b), 0, 1)
    return np.minimum(left, right)


D_range, T_range, Percent_range , C_range= np.linspace(0, 5, 51), np.linspace(0, 10, 101), np.linspace(0, 400, 401), np.linspace(0, 100, 101)

# Try this: change the 26 in "hot" to 20, then rerun Question 3 and compare.
D_sets = {"low": trimf(D_range, 0, 0, 1.5), "medium": trimf(D_range, 0.5, 2.5, 4.5), "high": trimf(D_range, 3.5, 5, 5)}
T_sets = {"low": trimf(T_range, 0, 0, 3), "medium": trimf(T_range, 1, 5, 9), "high": trimf(T_range, 7, 10, 10)}
Percent_sets = {"low": trimf(Percent_range, 0, 0, 100), "medium": trimf(Percent_range, 50, 200, 350), "high": trimf(Percent_range, 300, 400, 400)}
C_sets = {"low": trimf(C_range, 0, 0, 40), "medium": trimf(C_range, 20, 50, 80), "high": trimf(C_range, 60, 100, 100)}  


def degree(universe, membership, value):
    """Membership degree of one crisp value."""
    return float(np.interp(value, universe, membership))

rules = {
    ("low", "low", "low"): "high",
    ("low", "low", "medium"): "high",
    ("low", "low", "high"): "medium",

    ("low", "medium", "low"): "high",
    ("low", "medium", "medium"): "medium",
    ("low", "medium", "high"): "medium",

    ("low", "high", "low"): "medium",
    ("low", "high", "medium"): "low",
    ("low", "high", "high"): "low",

    ("medium", "low", "low"): "high",
    ("medium", "low", "medium"): "medium",
    ("medium", "low", "high"): "medium",

    ("medium", "medium", "low"): "medium",
    ("medium", "medium", "medium"): "medium",
    ("medium", "medium", "high"): "low",

    ("medium", "high", "low"): "low",
    ("medium", "high", "medium"): "low",
    ("medium", "high", "high"): "low",

    ("high", "low", "low"): "medium",
    ("high", "low", "medium"): "low",
    ("high", "low", "high"): "low",

    ("high", "medium", "low"): "low",
    ("high", "medium", "medium"): "low",
    ("high", "medium", "high"): "low",

    ("high", "high", "low"): "low",
    ("high", "high", "medium"): "low",
    ("high", "high", "high"): "low"
}

def fuzzify(value, universe, fuzzy_sets):
    degrees = {}

    for label, membership in fuzzy_sets.items():
        degrees[label] = degree(universe, membership, value)

    return degrees

def evaluate_rules(D_degree, T_degree, P_degree, rules):

    firing_strengths = {}

    for conditions, output in rules.items():

        d_label, t_label, p_label = conditions

        strength = min(
            D_degree[d_label],
            T_degree[t_label],
            P_degree[p_label]
        )

        firing_strengths[conditions] = {
            "output": output,
            "strength": strength
        }

    return firing_strengths

def aggregate_rules(results):

    output_strengths = {
        "low": 0,
        "medium": 0,
        "high": 0
    }

    for result in results.values():

        output = result["output"]
        strength = result["strength"]

        output_strengths[output] = max(
            output_strengths[output],
            strength
        )
    return output_strengths

def get_aggregated_output(aggregated, C_sets):

    output_membership = np.zeros_like(C_range)

    for label, strength in aggregated.items():

        clipped = np.minimum(C_sets[label], strength)

        output_membership = np.maximum(
            output_membership,
            clipped
        )

    return output_membership

def defuzzify(final_membership):

    numerator = np.sum(C_range * final_membership)
    denominator = np.sum(final_membership)

    if denominator == 0:
        return 0

    compatibility = numerator / denominator

    return compatibility

def calculate_compatibility(distance, time, percentage):

    #1. fuzzification
    D_degree = fuzzify(distance, D_range, D_sets)
    T_degree = fuzzify(time, T_range, T_sets)
    P_degree = fuzzify(percentage, Percent_range, Percent_sets)

    #2. rule evaluation
    results = evaluate_rules(
        D_degree,
        T_degree,
        P_degree,
        rules
    )

    #3. aggregation
    aggregated = aggregate_rules(results)

    #4. generate aggregated output membership
    final_membership = get_aggregated_output(aggregated, C_sets)

    #5 defuzzification
    compatibility = defuzzify(final_membership)

    return compatibility


# Visualise Membership Functions

# fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# plots = [
#     (axes[0, 0], "Detour Distance (km)", D_range, D_sets),
#     (axes[0, 1], "Detour Time (minutes)", T_range, T_sets),
#     (axes[1, 0], "Detour Percentage (%)", Percent_range, Percent_sets),
#     (axes[1, 1], "Compatibility Score", C_range, C_sets)
# ]

# for ax, title, universe, sets in plots:

#     for name, membership in sets.items():
#         ax.plot(universe, membership, label=name)

#     ax.set_title(title)
#     ax.set_xlabel("Value")
#     ax.set_ylabel("Membership Degree")
#     ax.set_ylim(0, 1.05)
#     ax.legend()
#     ax.grid()

# plt.tight_layout()
# plt.show()


# visualize Aggregated Output

# plt.plot(C_range, final_membership)
# plt.xlabel("Compatibility Score")
# plt.ylabel("Membership Degree")
# plt.title("Aggregated Output")
# plt.show()


