# Statistical Hypothesis Testing Framework

This project provides a framework for conducting statistical hypothesis testing using **ANOVA** and **t-tests**, with features such as power analysis, multiple comparison corrections (Bonferroni), bootstrap analysis, and assumption checks.

## Features

- **T-Test and ANOVA Support:**  
  Perform independent t-tests and one-way ANOVA tests with automatic logging and result reporting.
- **Assumption Checks:**  
  Normality and homogeneity of variance checks before running tests.
- **Effect Size Calculation:**  
  Measures such as Cohen’s \( d \) and Eta squared.
- **Power Analysis:**  
  Calculate required sample sizes to ensure meaningful results.
- **Bootstrap Analysis:**  
  Estimate confidence intervals using resampling techniques.
- **Bonferroni Correction:**  
  Adjust for multiple comparisons to control family-wise error rate.
- **Experiment Automation:**  
  Run multiple experiments and analyze overall significance.

---

## Project Structure

```
src/
│-- anova.py         # ANOVA test implementation
│-- ttest.py         # T-test implementation
│-- utils.py         # Shared utility functions and experiment
protocol.md      # Comprehensive guide on statistical hypothesis
README.md        # This file
pyproject.toml   # Dependency management
uv.lock          # Dependency lock file
```

---

## Installation

To set up the project using `uv` and `astral`, follow these steps:

1. **Install `uv`:**

  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

2. **Sync dependencies:**

  Use the `uv.lock` file to install the required dependencies:

  ```sh
  uv sync
  ```

3. **Verify the installation:**

  Ensure all dependencies are installed correctly by running:

  ```sh
  uv tool install ruff
  ruff check
  ```

4. **Optional: Add OpenAI Key**

  If you plan to use the OpenAI API for generating text, you can add your API key to the `.env` file:

  ```sh
  OPENAI_API=your-api-key
  ``` 

5. **Run the T-Test Experiment:**

  ```sh
  uv run -m src.ttest
  ```

You should now have all the necessary dependencies installed and can proceed with using the framework.

---

## Usage

### Running a T-Test Experiment

You can run a t-test experiment to compare two groups:

```python
from ttest import TTestExperiment, Group

group1 = Group(name="Group A")
group2 = Group(name="Group B")

def fetch_data(group_name: str, i: int) -> int:
    return random.randint(70, 90) if group_name == "Group A" else random.randint(75, 95)

num_experiments = 10
alpha = 0.05 / num_experiments  # Bonferroni correction

experiment = TTestExperiment([group1, group2], "ttest", alpha=alpha)
experiment.pre_register("Group B will have a higher average score than Group A")
experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)
```

### Running an ANOVA Experiment

To run a one-way ANOVA across multiple groups:

```python
from anova import ANOVAExperiment, Group

group1 = Group(name="Group A")
group2 = Group(name="Group B")
group3 = Group(name="Group C")

def fetch_data(group_name: str, i: int) -> int:
    return random.randint(72, 82) if group_name == "Group A" else random.randint(78, 88) if group_name == "Group B" else random.randint(70, 90)

num_experiments = 10
alpha = 0.05 / num_experiments  # Bonferroni correction

experiment = ANOVAExperiment([group1, group2, group3], "anova", alpha=alpha)
experiment.pre_register("Groups A, B, and C have significantly different means")
experiment.run_experiment_multiple_times(fetch_data, num_experiments=num_experiments)
```

---

## Configuration

### Parameters

The experiments can be customized by adjusting the following parameters:

| Parameter          | Description                                | Default |
|-------------------|--------------------------------------------|---------|
| `alpha`            | Significance level                        | 0.05    |
| `power`            | Statistical power                         | 0.8     |
| `confidence`       | Confidence level for intervals             | 0.95    |
| `bootstrap_confidence` | Confidence level for bootstrap analysis | 0.95    |
| `num_experiments`  | Number of repeated experiments             | 5       |

Example of setting parameters:

```python
experiment = TTestExperiment(
    [group1, group2],
    "ttest",
    alpha=0.01, 
    power=0.9, 
    confidence=0.99
)
```

## Logging

Experiment results are automatically logged in:

- `anova_results.log` (ANOVA tests)
- `t_test_results.log` (T-tests)

Each entry includes:

- Test statistic and p-value
- Effect size
- Assumption check results
- Bootstrap analysis results

---

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-new-analysis`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push the branch (`git push origin feature-new-analysis`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License.