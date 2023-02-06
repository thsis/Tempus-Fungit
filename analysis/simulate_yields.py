import warnings

import numpy as np
import pandas as pd
from copy import copy
from src.utilities import get_abs_path
from colorama import Style, Fore

SIMULATION_MODE = "random"

BAG_WEIGHT = 1000
T_COLONIZATION = 6
T_FRUITING = 6

P_INFECTION = 0.25
P_INFECTION_PER_WEEK = 1 - (1 - P_INFECTION)**(1/T_COLONIZATION)

MAX_LIFETIME_YIELD = 0.5 * BAG_WEIGHT
YIELD_DECAY_MODE = "exponential"
# this is the only real-valued root of the polynomial x + x**2 + x**3. I.e.
YIELD_DECAY_RATE_PER_FLUSH = 0.54368


def sample_time(lam, mode="const"):
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


class Block:
    counter = 0

    def __init__(self):
        Block.counter += 1
        self.id = copy(Block.counter)
        self.age = 0
        self.age_at_last_harvest = None
        self.infected = False
        self.phase = "COLONIZATION"
        self.flush = 0
        self.substrate_weight = BAG_WEIGHT
        self.fruit_weight = 0
        self.yields = []

        self.time_to_colonize = sample_time(T_COLONIZATION, SIMULATION_MODE)
        self.time_to_fruit = sample_time(T_FRUITING, SIMULATION_MODE)
        self.max_lifetime_yield = sample_weight(MAX_LIFETIME_YIELD, SIMULATION_MODE)

    def __str__(self):
        return f"Block {self.id}"

    def __infect(self):
        if (self.phase == "COLONIZATION") and (np.random.random() <= P_INFECTION_PER_WEEK):
            self.infected = True

    def __grow(self):
        if (self.age > self.time_to_colonize) and (self.flush < 3) and not self.infected:
            t = self.__get_time_since_colonization_or_last_harvest()

            if YIELD_DECAY_MODE == "linear":
                self.fruit_weight = self.__get_linear_iteration_growth(t)
            elif YIELD_DECAY_MODE == "exponential":
                self.fruit_weight = self.__get_exponential_iteration_growth(t)

    def __get_time_since_colonization_or_last_harvest(self):
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
        yield_for_flush = MAX_LIFETIME_YIELD * YIELD_DECAY_RATE_PER_FLUSH ** (self.flush + 1)
        # calculate rate of growth: at the end of the fruit growth period, the maximum yield has to be achieved
        # however, this is impossible with the standard mathematical formulation
        # instead, we take the time it takes to achieve one gram less than the maximum possible yield
        rate = (1/yield_for_flush) ** (1/self.time_to_fruit)
        weight = np.round(yield_for_flush - yield_for_flush * rate**t)
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
            return fruit_weight

    def mature(self):
        self.age += 1
        self.__check_phase()
        self.__infect()
        self.__grow()

    def inspect(self):
        print(f"{self}")
        print("Health Status:",
              f"{Fore.RED}Infected{Style.RESET_ALL}" if self.infected else f"{Fore.GREEN}Healthy{Style.RESET_ALL}")
        print("Current Phase:",
              f"{Fore.YELLOW}{self.phase}{Style.RESET_ALL}")
        print("Current Flush:", self.flush)
        print(f"age: {self.age}")
        print(f"current weight: {self.fruit_weight}")
        print(f"past yields: {self.yields}")

    def destroy(self):
        pass


class Martha:
    counter = 0

    def __init__(self, capacity=np.inf):
        self.capacity = capacity
        self.contents = []
        self.id = copy(Martha.counter)

    def __str__(self):
        return f"Martha {self.id}"

    def insert_blocks(self, num_blocks):
        for _ in range(num_blocks):
            if self.get_total_number_of_blocks() <= self.capacity:
                block = Block()
                self.contents.append(block)
            else:
                warnings.warn(f"attempted to add more blocks than there is capacity in {self}.")

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


if __name__ == "__main__":
    martha = Martha()
    for i in range(51):
        martha.insert_blocks(5)
        iteration_yield = martha.harvest_blocks(lambda x: x.fruit_weight > 50)
        print(f"This weeks yield: {Fore.YELLOW}{iteration_yield}{Style.RESET_ALL}")
        martha.remove_blocks(lambda x: x.flush > 2 or x.infected)
        martha.pass_time()
        martha.inspect()

