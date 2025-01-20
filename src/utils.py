import numpy as np
import logging
from dataclasses import dataclass
from typing import Tuple, List, Callable

# Configure logging to save results
logging.basicConfig(filename='statistical_tests.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class CheckAssumptionsResult:
    pass

@dataclass
class TestResult:
    test_type: str
    statistic: float
    p_value: float
    effect_size: float
    required_sample_size_per_group: int
    confidence_interval: Tuple[float, float]
    conclusion: str
    assumptions: CheckAssumptionsResult

@dataclass
class BootstrapAnalysisResult:
    bootstrap_mean_diff: float
    bootstrap_CI: Tuple[float, float]

class Group:
    def __init__(self, name="Group"):
        self.data = []
        self.name = name

    def add_data(self, value):
        self.data.append(value)

    def get_data_array(self):
        return np.array(self.data)

    def __str__(self):
        return f"{self.name}: {self.data}"
    
@dataclass
class ExperimentInfo:
    groups: List[str]
    alpha: float
    power: float
    test_type: str
    confidence: float
    bootstrap_confidence: float
    hypothesis: str

    def __str__(self):
        return (f"ExperimentInfo:\n"
                f"  Groups: {self.groups}\n"
                f"  Alpha: {self.alpha}\n"
                f"  Power: {self.power}\n"
                f"  Test Type: {self.test_type}\n"
                f"  Confidence: {self.confidence}\n"
                f"  Bootstrap Confidence: {self.bootstrap_confidence}\n"
                f"  Hypothesis: {self.hypothesis}")

@dataclass
class ExperimentResults:
    experiment_number: int
    sample_sizes: List[int]
    statistic: float
    p_value: float
    effect_size: float
    confidence_interval: Tuple[float, float]
    bootstrap_mean_diff: float
    bootstrap_CI: Tuple[float, float]
    conclusion: str

    def __str__(self):
        return (f"ExperimentResults:\n"
                f"  Experiment Number: {self.experiment_number}\n"
                f"  Sample Sizes: {self.sample_sizes}\n"
                f"  Statistic: {self.statistic}\n"
                f"  P-value: {self.p_value}\n"
                f"  Effect Size: {self.effect_size}\n"
                f"  Confidence Interval: {self.confidence_interval}\n"
                f"  Bootstrap Mean Difference: {self.bootstrap_mean_diff}\n"
                f"  Bootstrap CI: {self.bootstrap_CI}\n"
                f"  Conclusion: {self.conclusion}")

@dataclass
class AggregatedExperimentResults:
    bonferroni_corrected_alpha: float
    significant_results: int
    num_experiments: int
    overall_conclusion: str

    def __str__(self
                ):
        return (f"AggregatedExperimentResults:\n"
                f"  Bonferroni Corrected Alpha: {self.bonferroni_corrected_alpha}\n"
                f"  Significant Results: {self.significant_results}\n"
                f"  Number of Experiments: {self.num_experiments}\n"
                f"  Overall Conclusion: {self.overall_conclusion}")

class Experiment:
    def __init__(self, groups: List[Group], test_type: str, alpha=0.05, power=0.8, confidence=0.95, bootstrap_confidence=0.95, correct_alpha=False, num_experiments=1):
        self.groups = groups
        self.test_type = test_type
        self.alpha = alpha
        self.power = power
        self.confidence = confidence
        self.bootstrap_confidence = bootstrap_confidence
        self.num_experiments = num_experiments

    def check_assumptions(self) -> CheckAssumptionsResult:
        # TODO: Implement this method
        return None

    def calculate_effect_size(self) -> float:
        # TODO: Implement this method
        return 0.0

    def calculate_confidence_interval(self) -> Tuple[float, float]:
        # TODO: Implement this method
        return tuple(None, None)

    def perform_test(self) -> TestResult:
        # TODO: Implement this method
        return None

    def pre_register(self, hypothesis: str) -> None:
        experiment_info = ExperimentInfo(
            groups=[group.name for group in self.groups],
            alpha=self.alpha,
            power=self.power,
            test_type=self.test_type,
            confidence=self.confidence,
            bootstrap_confidence=self.bootstrap_confidence,
            hypothesis=hypothesis
        )
        logging.info(f"Pre-registered experiment: \n{experiment_info}")
        print(f"Experiment pre-registered: \n{experiment_info}")
        return experiment_info

    def bootstrap_analysis(self, num_bootstraps=1000) -> BootstrapAnalysisResult:
        data_arrays = [group.get_data_array() for group in self.groups]
        boot_diffs = []
        for _ in range(num_bootstraps):
            boot_samples = [np.random.choice(data, size=len(data), replace=True) for data in data_arrays]
            boot_diffs.append(np.mean(boot_samples[0]) - np.mean(boot_samples[1]))

        ci_lower, ci_upper = np.percentile(boot_diffs, [(1-self.bootstrap_confidence)/2*100, (1+self.bootstrap_confidence)/2*100])
        return BootstrapAnalysisResult(
            bootstrap_mean_diff=float(np.mean(boot_diffs)),
            bootstrap_CI=(round(ci_lower, 3), round(ci_upper, 3))
        )
    
    def aggregate_results(self, p_values: List[float], num_experiments: int) -> AggregatedExperimentResults:
        # Bonferroni Correction
        bonferroni_corrected_alpha = 1 - (1 - self.alpha) ** num_experiments

        # Determine if overall result is significant
        significant_results = sum(1 for p in p_values if p < bonferroni_corrected_alpha)
        overall_conclusion = "Significant" if significant_results > 0 else "Not Significant"

        aggregated_results = AggregatedExperimentResults(
            bonferroni_corrected_alpha=bonferroni_corrected_alpha,
            significant_results=significant_results,
            num_experiments=num_experiments,
            overall_conclusion=overall_conclusion
        )

        print(f"\nBonferroni Corrected Alpha: {bonferroni_corrected_alpha:.5f}")
        print(f"Number of significant results: {significant_results}/{num_experiments}")
        print(f"Overall Conclusion: {overall_conclusion}")

        # Logging results
        logging.info(aggregated_results)

        return aggregated_results

    def run_experiment_multiple_times(self, fetch_data: Callable[[str, int], float], num_experiments=5, num_data_points=100) -> None:
        p_values = []
        experiment_results_list = []
        for i in range(num_experiments):
            for group in self.groups:
                group.data.clear()
            for _ in range(num_data_points):
                for group in self.groups:
                    group.add_data(fetch_data(group.name, i))

            results = self.perform_test()
            confidence_interval = self.calculate_confidence_interval()
            bootstrap_results = self.bootstrap_analysis()
            p_values.append(results.p_value)

            experiment_results = ExperimentResults(
                experiment_number=i + 1,
                sample_sizes=[len(group.data) for group in self.groups],
                statistic=results.statistic,
                p_value=results.p_value,
                effect_size=results.effect_size,
                confidence_interval=confidence_interval,
                bootstrap_mean_diff=bootstrap_results.bootstrap_mean_diff,
                bootstrap_CI=bootstrap_results.bootstrap_CI,
                conclusion=results.conclusion
            )
            print(experiment_results)
            experiment_results_list.append(experiment_results)

        # Call the aggregate_results method
        aggregated_results = self.aggregate_results(p_values, num_experiments)
        return experiment_results_list, aggregated_results