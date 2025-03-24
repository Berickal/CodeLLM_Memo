import sys, os, utils, argparse, evaluation, generation
sys.path.append('./data')
import load_dataset
import matplotlib.pyplot as plt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, required=True)
    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--model", type=str, required=False)
    parser.add_argument("--output", type=str, required=False)
    parser.add_argument("--metric", type=str, required=False, default='ncd')
    parser.add_argument("--iter", type=int, required=False, default=3)

    args = parser.parse_args()

    dataset, model, output, metric, task, iter = args.dataset, args.model, args.output, args.metric, args.task, args.iter

    load_dataset.load(dataset, task, output)
    generation.generate(model, output, f'out/{output}', task, iter)

    sub_fol, sens = os.listdir(f'out/{output}'), []
    for fol in sub_fol:
        try:
            sens.append(evaluation.get_sensitivity_distribution(f'{fol}/{sub_fol}', metric))
        except Exception:
            sens.append([])
            continue
    
    plt.rcParams["figure.figsize"] = (10.5, 5.5)
    plt.rcParams.update({'font.size': 18})
    
    fig, ax = plt.subplots(ncols=1, nrows=1)
    ax.boxplot(sens, showfliers=False)
    ax.set_xticks(list(range(len(sub_fol))), sub_fol, rotation=45)
    ax.grid()
    ax.set_title(fol)
    ax.set_xlabel('Model')
    ax.set_ylabel('Sensitivity')
    
    plt.savefig(f'{output}.pdf', bbox_inches='tight')
    