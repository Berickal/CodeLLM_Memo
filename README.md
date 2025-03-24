# Learned or Memorized? Quantifying Membership Advantage in Code LLMs

This repository provides tools to evaluate the performance of code language models (Code LLMs) on various benchmarks, including code generation, vulnerability detection, program repair, and more.

## Installation

To set up the environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

PS : For the generation phase, we recommend the installation of Ollama. Further details <a href="https://ollama.com/download">here</a>

## Usage

### Default Pipeline

Run the default pipeline to evaluate a model on a specific task:

```bash
python pipeline.py --task code_generation --model codellama --output output --metric ncd --iter 3
```

### Step-by-Step Process

#### 1. Collect Data

Load a single dataset:

```bash
python data/load_dataset.py --dataset xlcost --output output/xlcost
```

Load all datasets for a specific task:

```bash
python data/load_dataset.py --task code_generation --output output/code_generation
```

#### 2. Generate Answers

Generate answers using a model:

```bash
python generation.py --model codellama --folder output/xlcost --task code_generation --output gen/xlcost --iteration 3
```

#### 3. Evaluate Results

Evaluate the generated answers:

```bash
python evaluation.py --folder gen/ --metric ncd --output xlcost_codellama
```

## Project Structure

- **pipeline.py**: Orchestrates the entire pipeline from data loading to evaluation.
- **data/**: Contains scripts for loading datasets and applying perturbations.
  - `load_dataset.py`: Handles dataset loading for various benchmarks.
  - `perturbation.py`: Applies perturbations to input data.
  - `obfuscation.py`: Provides obfuscation techniques for code.
- **generation.py**: Generates answers using the specified model.
- **evaluation.py**: Evaluates the generated answers using various metrics.
- **utils.py**: Utility functions for data handling and code cleaning.

## Benchmarks

The repository supports the following tasks:
- **Code Generation (cg)**: Generate code from natural language descriptions.
- **Vulnerability Detection (vd)**: Identify vulnerabilities in code.
- **Program Repair (pr)**: Fix buggy code.
- **Code Summarization (cs)**: Summarize code into natural language.
- **Test Generation (tg)**: Generate test cases for code.

## Metrics

Supported evaluation metrics include:
- **Levenshtein Distance**
- **Cosine Similarity**
- **Normalized Compression Distance (NCD)**
- **ROUGE**

## Examples

### Code Generation Example

```bash
python pipeline.py --task code_generation --model codellama --output output --metric rouge --iter 5
```

### Vulnerability Detection Example

```bash
python pipeline.py --task vulnerability_detection --model codellama --output output --metric levenshtein --iter 3
```

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License.
