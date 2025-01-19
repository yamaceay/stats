from dataclasses import dataclass
from typing import Tuple
from scipy import stats
import statsmodels.api as sm
import logging
import random
import numpy as np
from src.utils import Group, Experiment, CheckAssumptionsResult, TestResult

# Configure logging to save results
logging.basicConfig(filename='regression_results.log', level=logging.INFO, format='%(asctime)s - %(message)s')

@dataclass
class RegressionCheckAssumptionsResult(CheckAssumptionsResult):
    normality: str
    variance_homogeneity: str
    variance_p: float
    normality_p: float
    homoscedasticity_p: float
    independence: str

class RegressionExperiment(Experiment):
    def check_assumptions(self) -> RegressionCheckAssumptionsResult:
        data_arrays = [group.get_data_array() for group in self.groups]
        X = sm.add_constant(data_arrays[0])  # Adding constant for intercept
        y = data_arrays[1]

        # Fit linear regression model
        model = sm.OLS(y, X).fit()
        residuals = model.resid

        # Normality check (Shapiro-Wilk test)
        normality_p = stats.shapiro(residuals).pvalue

        # Homoscedasticity (Breusch-Pagan test)
        _, homoscedasticity_p, _, _ = sm.stats.het_breuschpagan(residuals, X)

        # Check independence (Durbin-Watson test for autocorrelation)
        dw_stat = sm.stats.durbin_watson(residuals)
        independence_status = "Pass" if 1.5 < dw_stat < 2.5 else "Fail"

        return RegressionCheckAssumptionsResult(
            normality={"residuals": "Pass" if normality_p > 0.05 else "Fail"},
            variance_homogeneity="Pass" if homoscedasticity_p > 0.05 else "Fail",
            variance_p=homoscedasticity_p,
            normality_p=normality_p,
            homoscedasticity_p=homoscedasticity_p,
            independence=independence_status
        )

    def calculate_effect_size(self) -> float:
        data_arrays = [group.get_data_array() for group in self.groups]
        X = sm.add_constant(data_arrays[0])
        y = data_arrays[1]

        model = sm.OLS(y, X).fit()
        r_squared = model.rsquared
        return round(np.sqrt(r_squared), 3)  # Cohen's f^2

    def calculate_confidence_interval(self) -> Tuple[float, float]:
        data_arrays = [group.get_data_array() for group in self.groups]
        X = sm.add_constant(data_arrays[0])
        y = data_arrays[1]

        model = sm.OLS(y, X).fit()
        ci_lower, ci_upper = model.conf_int()[1]  # Confidence interval for the slope
        return round(ci_lower, 3), round(ci_upper, 3)

    def perform_test(self) -> TestResult:
        assumptions = self.check_assumptions()
        data_arrays = [group.get_data_array() for group in self.groups]
        X = sm.add_constant(data_arrays[0])
        y = data_arrays[1]

        model = sm.OLS(y, X).fit()
        p_value = model.pvalues[1]  # P-value for the slope coefficient
        t_stat = model.tvalues[1]   # T-statistic for the slope coefficient
        effect_size = self.calculate_effect_size()

        required_sample_size = 0  # Sample size calculation can be added later

        conclusion = (
            "Reject the null hypothesis: Significant relationship between variables."
            if p_value < self.alpha else
            "Fail to reject the null hypothesis: No significant relationship."
        )

        result = TestResult(
            test_type=self.test_type,
            statistic=round(t_stat, 3),
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
    group1 = Group(name="Independent Variable (X)")
    group2 = Group(name="Dependent Variable (Y)")

    synthetic_data = [(x, 2*x + random.gauss(0, 5)) for x in range(100)]
    X_INDEX = None

    def fetch_data(group_name: str, i: int) -> int:
        global X_INDEX
        if i % 5 == 0 or i % 6 == 0:
            if group_name == "Independent Variable (X)":
                X_INDEX = random.randint(0, len(synthetic_data) - 1)
                return synthetic_data[X_INDEX][0]
            elif group_name == "Dependent Variable (Y)":
                return synthetic_data[X_INDEX][1]
        else:
            if group_name == "Independent Variable (X)":
                return random.randint(0, 100)
            elif group_name == "Dependent Variable (Y)":
                return random.randint(0, 200)
        return 0  # Ensure all return statements return an expression

    num_experiments = 10
    alpha = 0.05 / num_experiments  # Bonferroni correction

    experiment = RegressionExperiment([group1, group2], "regression", alpha=alpha)
    experiment.pre_register("There is a significant relationship between X and Y")
    experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)