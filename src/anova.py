from typing import Tuple
from scipy import stats
import statsmodels.stats.power as smp
import numpy as np
import logging
import random
from src.utils import Group, Experiment, CheckAssumptionsResult, TestResult

# Configure logging to save results
logging.basicConfig(filename='anova_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class ANOVAExperiment(Experiment):
    def check_assumptions(self) -> CheckAssumptionsResult:
        data_arrays = [group.get_data_array() for group in self.groups]

        # Normality Test (Shapiro-Wilk)
        normality_results = {group.name: stats.shapiro(group.get_data_array()).pvalue for group in self.groups}

        # Homogeneity of variance test
        variance_pvalue = stats.levene(*data_arrays).pvalue

        return CheckAssumptionsResult(
            normality={name: "Pass" if p > 0.05 else "Fail" for name, p in normality_results.items()},
            variance_homogeneity="Pass" if variance_pvalue > 0.05 else "Fail",
            variance_p=round(variance_pvalue, 3)
        )

    def calculate_effect_size(self) -> float:
        data_arrays = [group.get_data_array() for group in self.groups]
        all_data = np.concatenate(data_arrays)
        grand_mean = np.mean(all_data)
        ss_between = sum(len(group.data) * (np.mean(group.data) - grand_mean) ** 2 for group in self.groups)
        ss_total = sum((x - grand_mean) ** 2 for group in self.groups for x in group.data)
        return round(ss_between / ss_total, 3)

    def calculate_confidence_interval(self) -> Tuple[float, float]:
        return (0, 0)

    def perform_test(self) -> TestResult:
        assumptions = self.check_assumptions()
        data_arrays = [group.get_data_array() for group in self.groups]
        required_sample_size = 0

        t_stat, p_value = stats.f_oneway(*data_arrays)
        effect_size = self.calculate_effect_size()
        if effect_size == 0:
            logging.warning("Effect size is zero. No additional samples needed.")
        else:
            required_sample_size = smp.FTestAnovaPower().solve_power(effect_size=effect_size, alpha=self.alpha, power=self.power, k_groups=len(self.groups))
        confidence_interval = (0, 0)  # Placeholder for ANOVA

        conclusion = (
            "Reject the null hypothesis: Significant difference among groups."
            if p_value < self.alpha else
            "Fail to reject the null hypothesis: No significant difference among groups."
        )

        result = TestResult(
            test_type=self.test_type,
            statistic=round(t_stat, 3),
            p_value=round(p_value, 3),
            effect_size=effect_size,
            required_sample_size_per_group=required_sample_size,
            confidence_interval=confidence_interval,
            conclusion=conclusion,
            assumptions=assumptions
        )
        logging.info(result)
        return result

if __name__ == "__main__":
    group1 = Group(name="Group A")
    group2 = Group(name="Group B")
    group3 = Group(name="Group C")

    def fetch_data(group_name: str, i: int) -> int:
        if i % 5 == 0 or i % 6 == 0:
            return random.randint(75, 85)
        if group_name == "Group A":
            return random.randint(72, 82)
        elif group_name == "Group B":
            return random.randint(78, 88)
        elif group_name == "Group C":
            return random.randint(70, 90)
        return 0

    num_experiments=10
    alpha=0.05 / num_experiments
    experiment = ANOVAExperiment([group1, group2, group3], "anova", alpha=alpha)
    experiment.pre_register("Groups A, B and C have significantly different means")
    experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)