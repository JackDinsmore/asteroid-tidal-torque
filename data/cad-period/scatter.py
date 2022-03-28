# Goal: spawn a bunch of runs that cover the parameter space.
from matplotlib import pyplot as plt
import numpy as np

LOW_ORDER_INDEX = 1
BASE_NAME = f"cad"
LOW_CADENCE= 2 * 60
HIGH_CADENCE = 60 * 60
NUM_DIVISIONS = 48 # Run with 16 cores per process.
LOW_ORDER = [(0.39269908169, 0, -0.09766608), (0.39269908169, 0.05200629, -0.2021978)][LOW_ORDER_INDEX]
HIGH_ORDER = [0, 0, 0, 0, 0, 0, 0]

#PERIODS = [0.1, 0.5, 1, 5]
PERIODS = [5]

def get_text(cadence, period):
    return """0, 3
{}
5
1000
6000
{}, {}, {}
1.0
{}, {}, {}, {}, {}, {}, {}, {}, {}, {}
0.78539816339, 0.125, 0, 1, 1, 1, 1, 1, 1, 1
-0.78539816339, -0.125, -0.25, -1, -1, -1, -1, -1, -1, -1
1e-2, 1e-5""".format(cadence, 0.00006464182 * 9/period, 0.00012928364 * 9/period, -0.00012928364 * 9/period,
    LOW_ORDER[0], LOW_ORDER[1], LOW_ORDER[2], HIGH_ORDER[0], HIGH_ORDER[1],
    HIGH_ORDER[2], HIGH_ORDER[3], HIGH_ORDER[4], HIGH_ORDER[5], HIGH_ORDER[6])

for period in PERIODS:
    for ratio_index, cadence in enumerate(np.linspace(LOW_CADENCE, HIGH_CADENCE, NUM_DIVISIONS)):
        f = open("../../staged/{}-{}-{:02}.txt".format(BASE_NAME, period, ratio_index), 'w')
        f.write(get_text(cadence, period))
        f.close()
