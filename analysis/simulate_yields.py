import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from copy import copy
from src.utilities import get_abs_path, unnest_df
from colorama import Style, Fore
from dataclasses import dataclass
from tqdm import trange


def sample_time(lam, mode):
    if mode == "const":
        return lam
    elif mode == "random":
        # avoid blocks that flush immediately (and later on division by zero)
        return np.random.poisson(lam - 1) + 1
    else:
        raise ValueError(f"{mode} not recognized, select one of {{'const', 'random'}}.")


def sample_weight(mean, std=None, mode="const"):
    if mode == "const":
        return mean
    elif mode == "random":
        return np.random.normal(loc=mean, scale=std)


@dataclass
class BlockRecord:
    block_id: int
    age: int
    phase: str
    infected: bool
    flush: int
    substrate_weight: float
    fruit_weight: float
    harvested: float

    def __init__(self, block_id, age, phase, infected, flush, substrate_weight, fruit_weight, harvested=0):
        self.block_id = block_id
        self.age = age
        self.phase = phase
        self.infected = infected
        self.flush = flush
        self.substrate_weight = substrate_weight
        self.fruit_weight = fruit_weight
        self.harvested = harvested

    def __str__(self):
        identifier = f"Block {self.block_id}"
        health_status = f"{Fore.RED}Infected{Style.RESET_ALL}" if self.infected else f"{Fore.GREEN}Healthy{Style.RESET_ALL}"
        current_phase = f"{Fore.YELLOW}{self.phase}{Style.RESET_ALL}"
        out = "\n".join([f"{identifier}",
                         f"Health Status: {health_status}",
                         f"Cuffent Phase: {current_phase}",
                         f"Current Flush: {self.flush}",
                         f"Current Age: {self.age}",
                         f"Current Weight: {self.fruit_weight}"])
        return out


class Block:
    counter = 0

    def __init__(self, simulation_mode, yield_decay_mode, bag_weight, max_lifetime_factor,
                 mean_t_colonization, mean_t_fruiting, p_infection):
        Block.counter += 1
        self.id = copy(Block.counter)
        self.age = 0
        self.age_at_last_harvest = None
        self.infected = False
        self.phase = "COLONIZATION"
        self.flush = 0
        self.substrate_weight = bag_weight
        self.fruit_weight = 0
        self.harvested = 0
        self.yields = []
        self.simulation_mode = simulation_mode
        self.bag_weight = bag_weight
        self.max_lifetime_factor = max_lifetime_factor
        self.max_lifetime_yield = self.max_lifetime_factor * self.bag_weight
        self.yield_decay_mode = yield_decay_mode
        self.time_to_colonize = sample_time(mean_t_colonization, self.simulation_mode)
        self.p_infection_per_week = 1 - (1 - p_infection) ** (1 / self.time_to_colonize)
        self.time_to_fruit = sample_time(mean_t_fruiting, self.simulation_mode)
        self.max_lifetime_yield = sample_weight(self.max_lifetime_yield, self.simulation_mode)

    def __str__(self):
        return f"Block {self.id}"

    def __infect(self):
        if (self.phase == "COLONIZATION") and (np.random.random() <= self.p_infection_per_week):
            self.infected = True

    def __grow(self):
        if (self.age > self.time_to_colonize) and (self.flush < 3) and not self.infected:
            t = self.get_time_since_colonization_or_last_harvest()

            if self.yield_decay_mode == "linear":
                self.fruit_weight = self.__get_linear_iteration_growth(t)
            elif self.yield_decay_mode == "exponential":
                self.fruit_weight = self.__get_exponential_iteration_growth(t)

    def get_time_since_colonization_or_last_harvest(self):
        if self.flush == 0:
            t = self.age - self.time_to_colonize
        else:
            t = self.age - self.age_at_last_harvest
        return t

    def __get_linear_iteration_growth(self, t):
        # first flush is 3 times larger than third, second flush is twice as large as third
        yield_for_flush = max(3 - self.flush, 0) / 6 * self.max_lifetime_yield
        prop_growing_cycle = min(t / self.time_to_fruit, 1)
        weight = np.round(yield_for_flush * prop_growing_cycle)
        return weight

    def __get_exponential_iteration_growth(self, t):
        # this is the only real-valued root of the polynomial x + x**2 + x**3. I.e.
        yield_decay_rate_per_flush = 0.54368
        yield_for_flush = self.max_lifetime_yield * yield_decay_rate_per_flush ** (self.flush + 1)
        # calculate rate of growth: at the end of the fruit growth period, the maximum yield has to be achieved
        # however, this is impossible with the standard mathematical formulation
        # instead, we take the time it takes to achieve one gram less than the maximum possible yield
        rate = (1/yield_for_flush) ** (1/self.time_to_fruit)
        progress = min(self.time_to_fruit, t)
        weight = np.round(yield_for_flush - yield_for_flush * rate**progress)
        return weight

    def __check_phase(self):
        if not self.infected:
            if self.age > self.time_to_colonize:
                self.phase = "FRUITING"

    def harvest(self):
        if self.infected:
            return 0
        else:
            fruit_weight = copy(self.fruit_weight)
            self.fruit_weight = 0
            self.flush += 1
            self.age_at_last_harvest = copy(self.age)
            self.yields.append(fruit_weight)
            self.harvested = fruit_weight
            return fruit_weight

    def mature(self):
        self.age += 1
        self.__check_phase()
        self.__infect()
        self.__grow()

    def inspect(self):
        record = BlockRecord(block_id=self.id,
                             age=self.age,
                             phase=self.phase,
                             infected=self.infected,
                             flush=self.flush,
                             substrate_weight=self.substrate_weight,
                             fruit_weight=self.fruit_weight,
                             harvested=copy(self.harvested))
        self.harvested = 0
        return record


class Martha:
    counter = 0

    def __init__(self, capacity=None, block_kwargs=None):
        self.capacity = capacity if capacity else np.inf
        self.contents = []
        self.id = copy(Martha.counter)
        self.block_kwargs = block_kwargs if block_kwargs else {}

    def __str__(self):
        return f"Martha {self.id}"

    def insert_blocks(self, num_blocks):
        for _ in range(num_blocks):
            if self.get_total_number_of_blocks() < self.capacity:
                block = Block(**self.block_kwargs)
                self.contents.append(block)

    def harvest_blocks(self, strategy, *args, **kwargs):
        res = [b.harvest() for b in self.contents if strategy(b, *args, **kwargs)]
        return sum(res)

    def remove_blocks(self, strategy, *args, **kwargs):
        for i, b in enumerate(self.contents):
            if strategy(b, *args, **kwargs):
                self.contents.pop(i)

    def get_total_yield(self):
        return sum(b.fruit_weight for b in self.contents)

    def get_total_number_of_blocks(self):
        return len(self.contents)

    def inspect(self):
        print(f"{self}")
        print(f"there are currently {self.get_total_number_of_blocks()} block(s) in {self.id}")
        for b in self.contents:
            b.inspect()
        print(f"the total yield would be {self.get_total_yield()} g if all blocks where harvested.")
        print("*" * 80)

    def pass_time(self):
        for b in self.contents:
            b.mature()

    def get_status(self):
        status = pd.DataFrame([b.inspect() for b in self.contents])
        return status


def harvest_after_j_weeks(block, j):
    return block.phase == "FRUITING" and block.get_time_since_colonization_or_last_harvest() >= j


def remove_after_infection_or_k_flushes(block, k):
    return block.infected or block.flush >= k


def simulate(replications, capacity, weeks, blocks, harvest_strategy, harvest_kwargs, remove_strategy, remove_kwargs,
             block_kwargs=None):
    out = []
    block_kwargs = block_kwargs if block_kwargs else {}
    for i in trange(replications, ncols=80):
        martha = Martha(capacity=capacity, block_kwargs=block_kwargs)
        for w in range(weeks):
            martha.insert_blocks(blocks)
            martha.harvest_blocks(harvest_strategy, **harvest_kwargs)

            status = (martha
                      .get_status()
                      .assign(replication=i,
                              week=w))
            out.append(status)
            martha.remove_blocks(remove_strategy, **remove_kwargs)
            martha.pass_time()
    col_order = ["replication", "week", "block_id", "substrate_weight", "age",
                 "phase", "infected", "flush", "fruit_weight", "harvested"]
    return pd.concat(out).loc[:, col_order]


def main(args):
    block_kwargs = {
        "simulation_mode": args.simulation_mode,
        "yield_decay_mode": args.yield_decay_mode,
        "bag_weight": args.bag_weight,
        "max_lifetime_factor": args.max_lifetime_factor,
        "mean_t_colonization": args.mean_t_colonization,
        "mean_t_fruiting": args.mean_t_fruiting,
        "p_infection": args.p_infection}

    data = simulate(replications=args.replications,
                    capacity=args.capacity,
                    weeks=args.weeks,
                    blocks=args.blocks,
                    harvest_strategy=harvest_after_j_weeks, harvest_kwargs={"j": args.grow_time},
                    remove_strategy=remove_after_infection_or_k_flushes, remove_kwargs={"k": args.remove_after_flush},
                    block_kwargs=block_kwargs)

    harvests = (data
                .groupby(["replication", "week"])
                .agg({"harvested": "sum", "fruit_weight": "sum"})
                .reset_index())

    blocks = (data
              .groupby(["replication", "week"])
              .agg({"block_id": ["nunique", "max"], "infected": "sum"})
              .pipe(unnest_df)
              .rename(columns={"block_id_nunique": "number_of_blocks",
                               "block_id_max": "last_block",
                               "infected_sum": "number_of_infected_blocks"})
              .assign(prev_last_block=lambda x: x.last_block.shift(),
                      number_of_new_blocks=lambda x: x.last_block - x.prev_last_block)
              .reset_index())

    p_harvest = sns.boxplot(data=harvests, x="week", y="harvested")
    plt.show()
    p_block_total = sns.boxplot(data=blocks, x="week", y="number_of_blocks")
    plt.show()
    p_block_infected = sns.boxplot(data=blocks, x="week", y="number_of_infected_blocks")
    plt.show()
    p_block_new = sns.boxplot(data=blocks, x="week", y="number_of_new_blocks")
    plt.show()

    if args.outfile:
        data.to_csv(get_abs_path("data", f"{args.outfile}.csv"))
        p_harvest.figure.savefig(get_abs_path("analysis", "figures", f"{args.outfile}_harvest.png"))
        p_block_total.figure.savefig(get_abs_path("analysis", "figures", f"{args.outfile}_blocks_total.png"))
        p_block_infected.figure.savefig(get_abs_path("analysis", "figures", f"{args.outfile}_blocks_infected.png"))
        p_block_new.figure.savefig(get_abs_path("analysis", "figures", f"{args.outfile}_blocks_new.png"))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulation-mode", default="const")
    parser.add_argument("--yield-decay-mode", default="linear")
    parser.add_argument("--bag-weight", default=1000, type=float)
    parser.add_argument("--max-lifetime-factor", default=0.25, type=float)
    parser.add_argument("--mean-t-colonization", default=4, type=float)
    parser.add_argument("--mean-t-fruiting", default=2, type=float)
    parser.add_argument("--p-infection", default=0.25, type=float)
    parser.add_argument("--replications", default=100, type=int)
    parser.add_argument("--weeks", default=52, type=int)
    parser.add_argument("--blocks", default=8, type=int)
    parser.add_argument("--capacity", default=None, type=int)
    parser.add_argument("--grow-time", default=2, type=int)
    parser.add_argument("--remove-after-flush", default=3, type=int)
    parser.add_argument("--outfile", default=None)

    ARGS = parser.parse_args()
    main(ARGS)