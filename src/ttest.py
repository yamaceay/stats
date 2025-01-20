from dataclasses import dataclass
from typing import Tuple
from scipy import stats
import statsmodels.stats.power as smp
import numpy as np
import logging
import random
from src.utils import Group, Experiment, CheckAssumptionsResult, TestResult
from src.agent import generate_report

# Configure logging to save results
logging.basicConfig(filename='t_test_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class TTestCheckAssumptionsResult(CheckAssumptionsResult):
    normality: dict
    variance_homogeneity: str
    variance_p: float

class TTestExperiment(Experiment):
    def check_assumptions(self) -> CheckAssumptionsResult:
        data_arrays = [group.get_data_array() for group in self.groups]

        # Normality Test (Shapiro-Wilk)
        normality_results = {group.name: stats.shapiro(group.get_data_array()).pvalue for group in self.groups}

        # Homogeneity of variance test
        variance_pvalue = stats.levene(*data_arrays).pvalue

        return TTestCheckAssumptionsResult(
            normality={name: "Pass" if p > 0.05 else "Fail" for name, p in normality_results.items()},
            variance_homogeneity="Pass" if variance_pvalue > 0.05 else "Fail",
            variance_p=round(variance_pvalue, 3)
        )

    def calculate_effect_size(self) -> float:
        data_arrays = [group.get_data_array() for group in self.groups]
        
        mean_diff = np.mean(data_arrays[0]) - np.mean(data_arrays[1])
        pooled_std = np.sqrt((np.std(data_arrays[0], ddof=1) ** 2 + np.std(data_arrays[1], ddof=1) ** 2) / 2)
        return round(mean_diff / pooled_std, 3) if pooled_std != 0 else 0

    def calculate_confidence_interval(self) -> Tuple[float, float]:
        data_arrays = [group.get_data_array() for group in self.groups]
        
        mean_diff = np.mean(data_arrays[0]) - np.mean(data_arrays[1])
        se = np.sqrt(np.var(data_arrays[0], ddof=1) / len(data_arrays[0]) + np.var(data_arrays[1], ddof=1) / len(data_arrays[1]))
        df = len(data_arrays[0]) + len(data_arrays[1]) - 2
        t_critical = stats.t.ppf((1 + self.confidence) / 2, df)
        margin_of_error = t_critical * se
        return round(mean_diff - margin_of_error, 3), round(mean_diff + margin_of_error, 3)

    def perform_test(self) -> TestResult:
        assumptions = self.check_assumptions()
        data_arrays = [group.get_data_array() for group in self.groups]
        required_sample_size = 0

        t_stat, p_value = stats.ttest_ind(data_arrays[0], data_arrays[1], equal_var=(assumptions.variance_homogeneity == "Pass"))
        effect_size = self.calculate_effect_size()
        if effect_size > 0:
            logging.warning("Effect size is zero. No additional samples needed.")
        else:
            required_sample_size = smp.TTestIndPower().solve_power(effect_size=effect_size, alpha=self.alpha, power=self.power)
        confidence_interval = self.calculate_confidence_interval()

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

    def fetch_data(group_name: str, i: int) -> int:
        if group_name == "Group A":
            return random.randint(75, 88)
        elif group_name == "Group B":
            return random.randint(78, 85)
        return 0

    num_experiments=10
    alpha=0.1 / num_experiments
    experiment = TTestExperiment([group1, group2], "ttest", alpha=alpha)
    experiment_info = experiment.pre_register("Group B will have a higher average score than Group A")
    experiment_results, aggregated_experiment_results = experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)

    summary_input = f"**Experiment Hypothesis:** {experiment_info.hypothesis}"
    summary_input += "\n\n**Experiment Results:**" + "\n\n".join(str(result) for result in experiment_results)
    summary_input += f"\n\n**Overall conclusion:**\n\n {aggregated_experiment_results.overall_conclusion}"
    generate_report(summary_input)
