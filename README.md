# Learned or Memorized ? Quantifying Membership Advantage in Code LLMs

## Default

```bash 
#install requirements
pip install requirements.txt
#Evaluate set of benchmarks on model
python pipeline.py --task code_generation --model codellama --output output --metric ncd --iter 3
```

## Step by step
You can proced the process step by step
### Collect data

```bash 
#Load a single dataset
python data/load_dataset.py --dataset xlcost --output output/xlcost

#Load all dataset by task
python data/load_dataset.py --task code_generation --output output/code_generation
```


### Generate answers

```bash 
python generation.py --model codellama --folder output/xlcost --task code_generation --output gen/xlcost --iteration 3
```

### Evaluation

```bash 
python evaluation.py --folder gen/ --metric ncd --output xlcost_codellama
```
