import numpy as np
from pandas import DataFrame

shelves = ["left", "right"]
rows = ["bottom", "top"]
positions = ["left", "center", "right"]

locations = DataFrame([(s, r, p) for s in shelves for r in rows for p in positions],
                      columns=["shelf", "row", "position"])
idxs = np.arange(len(locations), dtype=int)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Randomizer for Experiment Positions")
    parser.add_argument("n", type=int,
                        help=f"Number of Experiments. Must not exceed {len(locations)}.")

    args = parser.parse_args()
    placements = np.random.choice(idxs, size=args.n, replace=False)
    print(locations.loc[placements, :])
