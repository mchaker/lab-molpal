from argparse import ArgumentParser
from dataclasses import dataclass, field
from pathlib import Path
import pickle
from typing import Optional, Union

import numpy as np

from experiment import Experiment, IncompleteExperimentError
from utils import *

@dataclass
class Dataset:
    split: float
    model: str
    metric: str
    N: int
    num_acquired: List[int]
    avg: np.ndarray
    smis: np.ndarray
    scores: np.ndarray
    reps: int = field(init=False)
    num_iters: int = field(init=False)

    def __post_init__(self):
        self.reps = len(self.avg)
        self.num_iters = len(self.num_acquired)

        avg = self.avg
        self.avg = np.empty((avg.shape[1], 2))
        self.avg[:, 0], self.avg[:, 1] = avg.mean(0), avg.std(0)

        smis = self.smis
        self.smis = np.empty((smis.shape[1], 2))
        self.smis[:, 0], self.smis[:, 1] = smis.mean(0), smis.std(0)

        scores = self.scores
        self.scores = np.empty((scores.shape[1], 2))
        self.scores[:, 0], self.scores[:, 1] = scores.mean(0), scores.std(0)

    def __str__(self):
        header = f"| {self.split:0.1%} | {self.model.upper()} | {self.metric.upper()} | TOP-{self.N} |"
        border = f"+{'-'*(len(header)-2)}+"

        width = len("Points acquired") + 2
        rows = []
        rows.append(
            f"{'Points acquired': >0{width}}: {', '.join(map(str, self.num_acquired))}"
        )
        rows.append(
            f"{'Average': >0{width}}: {Dataset.format_reward_array(self.avg, 2)}"
        )
        rows.append(f"{'SMILES': >0{width}}: {Dataset.format_reward_array(self.smis)}")
        rows.append(
            f"{'Scores': >0{width}}: {Dataset.format_reward_array(self.scores)}"
        )

        return "\n".join((border, header, border, *rows))

    def get_reward(self, reward: str) -> np.ndarray:
        try:
            return {
                "AVG": self.avg,
                "SCORES": self.scores,
                "SMILES": self.smis
            }[reward.upper()]
        except KeyError:
            raise ValueError(f"Invalid reward! got: {reward}")

    @staticmethod
    def format_reward_array(X: np.ndarray, precision: int = 1) -> str:
        means, sds = zip(*X.tolist())
        return ", ".join(
            [
                f"{mean:0.{precision}%} ({sd:0.{precision}%})"
                for mean, sd in zip(means, sds)
            ]
        )

def save_dataset(d: Dataset, filepath: Optional[Union[str, Path]] = None):
    pkl_file = filepath or f"{d.split:0.3f}-{d.model}-{d.metric}-top{d.N}.pkl"
    pickle.dump(d, open(pkl_file, "wb"))

    return pkl_file

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--split", type=float)
    parser.add_argument("--model")
    parser.add_argument("--metric")
    parser.add_argument(
        "-e",
        "--experiments",
        "--expts",
        nargs="+",
        help='the top-level directory generated by the MolPAL run. I.e., the directory with the "data" and "chkpts" directories',
    )
    parser.add_argument(
        "-l",
        "--library",
        help="the library file used for the corresponding MolPAL run.",
    )
    parser.add_argument(
        "--true-csv", help="a CSV file containing the true scoring data"
    )
    parser.add_argument("--smiles-col", type=int, default=0)
    parser.add_argument("--score-col", type=int, default=1)
    parser.add_argument("--no-title-line", action="store_true", default=False)
    parser.add_argument(
        "--maximize",
        action="store_true",
        default=False,
        help="whether the objective for which you are calculating performance should be maximized.",
    )
    parser.add_argument(
        "-N",
        type=int,
        help="the number of top scores from which to calculate the reward",
    )
    parser.add_argument("-o", "--output", help="the output filepath")

    args = parser.parse_args()
    args.title_line = not args.no_title_line

    smis = extract_smis(args.library, args.smiles_col, args.title_line)
    d_smi_idx = {smi: i for i, smi in enumerate(smis)}

    d_smi_score = build_true_dict(
        args.true_csv, args.smiles_col, args.score_col, args.title_line, args.maximize
    )

    true_smis_scores = sorted(d_smi_score.items(), key=lambda kv: kv[1])[::-1]
    true_top_k = true_smis_scores[: args.N]

    rewardss = []
    incomplete_experiments = []
    for expt_dir in args.experiments:
        e = Experiment(expt_dir, d_smi_idx)
        rewardss.append(
            [e.calculate_reward(i, true_top_k, True) for i in range(e.num_iters)]
        )
        try:
            len(e)
        except IncompleteExperimentError:
            incomplete_experiments.append(expt_dir)

    if len(incomplete_experiments) > 0:
        print("There are incomplete experiments!")
        min_iters = min(len(r) for r in rewardss)
        rewardss = [r[:min_iters] for r in rewardss]
        print(
            f"Results will for dataset will be truncated to shortest experiment ({min_iters})."
        )
    rewardss = np.array(rewardss)

    d = Dataset(
        args.split,
        args.model,
        args.metric,
        args.N,
        e.num_acquired,
        rewardss[:,:,0],
        rewardss[:,:,1],
        rewardss[:,:,2],
    )

    print(d)
    if args.output:
        print(f"Saved dataset to {save_dataset(d, args.output)}")
