from dataclasses import dataclass
from typing import Tuple
from scipy import stats
import logging
import random
import numpy as np
from src.utils import Group, Experiment, CheckAssumptionsResult, TestResult

# Configure logging to save results
logging.basicConfig(filename='chi_squared_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class ChiSquaredCheckAssumptionsResult(CheckAssumptionsResult):
    assumption_status: str
    min_expected: float

class ChiSquaredExperiment(Experiment):
    def check_assumptions(self) -> CheckAssumptionsResult:
        data_arrays = [np.bincount(group.get_data_array(), minlength=2) for group in self.groups]

        # Expected frequency should not be too small
        contingency_table = np.vstack(data_arrays)
        _, expected_freq = np.histogram(contingency_table, bins=len(self.groups))
        min_expected = np.min(expected_freq)
        assumption_status = "Pass" if min_expected >= 5 else "Fail"

        return ChiSquaredCheckAssumptionsResult(assumption_status, min_expected)

    def calculate_effect_size(self) -> float:
        # Effect size for chi-square test (Cramér's V)
        contingency_table = np.vstack([np.bincount(group.get_data_array(), minlength=2) for group in self.groups])
        chi2, _, _, _ = stats.chi2_contingency(contingency_table)
        n = np.sum(contingency_table)
        min_dim = min(contingency_table.shape) - 1
        return round(np.sqrt(chi2 / (n * min_dim)), 3)

    def calculate_confidence_interval(self) -> Tuple[float, float]:
        return (0, 0)  # Not commonly computed for chi-square tests

    def perform_test(self) -> TestResult:
        assumptions = self.check_assumptions()
        contingency_table = np.vstack([np.bincount(group.get_data_array(), minlength=2) for group in self.groups])

        chi2_stat, p_value, _, _ = stats.chi2_contingency(contingency_table)
        effect_size = self.calculate_effect_size()

        required_sample_size = 0  # Sample size planning isn't usually applicable to chi-squared tests

        conclusion = (
            "Reject the null hypothesis: There is an association between the groups."
            if p_value < self.alpha else
            "Fail to reject the null hypothesis: No significant association."
        )

        result = TestResult(
            test_type=self.test_type,
            statistic=round(chi2_stat, 3),
            p_value=round(p_value, 3),
            effect_size=effect_size,
            required_sample_size_per_group=required_sample_size,
            confidence_interval=self.calculate_confidence_interval(),
            conclusion=conclusion,
            assumptions=assumptions
        )
        logging.info(result)
        return result

if __name__ == "__main__":
    group1 = Group(name="Group A")
    group2 = Group(name="Group B")

    def fetch_data(group_name: str, i: int) -> int:
        if i % 5 == 0 or i % 6 == 0:
            return random.choice([0, 1])
        if group_name == "Group A":
            return random.choice([0, 1, 1, 0, 1])
        return random.choice([0, 0, 1, 0, 1])

    num_experiments = 10
    alpha = 0.05 / num_experiments  # Bonferroni correction

    experiment = ChiSquaredExperiment([group1, group2], "chi_squared", alpha=alpha)
    experiment.pre_register("Group A and B will have significantly different distributions")
    experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)