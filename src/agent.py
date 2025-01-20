from dotenv import load_dotenv
import os
load_dotenv()
import logging
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_report(summary_input: str, output_file="experiment_report.md"):
    """
    Generates a Markdown report summarizing the experiment results using an AI assistant.
    
    Args:
        experiment_results (List[ExperimentResults]): List of experiment results
        output_file (str): Path to save the Markdown report
    """
    
    # Prompt AI model to summarize findings
    prompt = f"""
    You are a data scientist expert. Based on the following experiment results, write a concise and professional Markdown report, including key statistical findings, interpretation, and recommendations.

    ### Experiment:
    {summary_input}

    ### Guidelines:
    - Provide a summary of key statistical findings.
    - Include conclusions based on p-values and effect sizes.
    - Highlight any potential issues or recommendations.
    - Use professional Markdown formatting.

    ### Output Report:
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an expert statistician."},
                        {"role": "user", "content": prompt}],
            max_tokens=1500
        )

        report_content = response.choices[0].message.content

        # Save report to a Markdown file
        with open(output_file, "w") as file:
            file.write(report_content)

        print(f"Report generated successfully: {output_file}")
        logging.info(f"Report generated: {output_file}")

    except Exception as e:
        logging.error(f"Error generating report: {e}")
        print(f"Error generating report: {e}")