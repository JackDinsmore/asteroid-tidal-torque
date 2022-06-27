import numpy as np
import sys, os
sys.path.append("../../../density")
from core import UncertaintyTracker

N_RUNS = 48
DOFS = [9, 7, 5, 3, 2]
N_TRIALS = 5
MIN_RUN = 0

def average(dof, run):
    print(f"DOF: {dof}, run: {run}")
    unc_tracker = UncertaintyTracker()
    for trial_num in range(N_TRIALS):
        fname = "cast-{}-{}-rho-{:02}-map.npy".format(dof, trial_num, run)
        if not os.path.exists(fname):
            return None
        with open(fname, 'rb') as f:
            unc_tracker += UncertaintyTracker.load(f)
    density_map, uncertainty_map = unc_tracker.generate()
    if density_map is None:
        raise Exception("No samples in the unc tracker")
    true_map = np.ones_like(density_map)
    true_map[np.isnan(density_map)] = np.nan
    true_map /= np.nansum(true_map)

    deviation_map = density_map - true_map
    ratio_map = deviation_map / uncertainty_map
    maps = [
        deviation_map / density_map,
        uncertainty_map / density_map,
        ratio_map,
    ]
    return np.array([(
            np.nanpercentile(m, 100 - (100 - 68.27) / 2),
            np.nanpercentile(m, 100 - (100 - 95.45) / 2),
            np.nanpercentile(m, 50),
            np.nanpercentile(m, (100 - 95.45) / 2),
            np.nanpercentile(m, (100 - 68.27) / 2),
        ) for m in maps])

def single_plot(dof):
    global MIN_RUN
    avgs = []
    for run in range(N_RUNS):
        avg = average(dof, run)
        if avg is None:
            MIN_RUN = max(run, MIN_RUN)
            continue
        else:
            avgs.append(avg)
    return np.array(avgs)

def scan():
    results = np.array([single_plot(dof) for dof in DOFS])
    with open("finish.npy", 'wb') as f:
        np.save(f, results)

def draw():
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(ncols=1, nrows=3, sharex=True, figsize=(6, 8))
    axs[2].set_xlabel("sigma P")
    axs[0].set_ylabel("Deviation")
    axs[1].set_ylabel("Uncertainty")
    axs[2].set_ylabel("Ratio")

    xs = np.array([
        5.55495891e-09, 7.09682065e-09, 9.06664911e-09, 1.15832329e-08,
        1.47983320e-08, 1.89058298e-08, 2.41534250e-08, 3.08575685e-08,
        3.94225471e-08, 5.03648633e-08, 6.43443826e-08, 8.22041261e-08,
        1.05021108e-07, 1.34171284e-07, 1.71412525e-07, 2.18990629e-07,
        2.79774746e-07, 3.57430402e-07, 4.56640543e-07, 5.83387940e-07,
        7.45315967e-07, 9.52189535e-07, 1.21648395e-06, 1.55413722e-06,
        1.98551120e-06, 2.53661946e-06, 3.24069604e-06, 4.14019958e-06,
        5.28937375e-06, 6.75751836e-06, 8.63316841e-06, 1.10294331e-05,
        1.40908169e-05, 1.80019333e-05, 2.29986385e-05, 2.93822538e-05,
        3.75377368e-05, 4.79568958e-05, 6.12680478e-05, 7.82739087e-05,
        1.00000000e-04
    ]) * 3600 * 9

    os.system("scp jdinsmore@txe1-login.mit.edu:asteroid-tidal-torque/code/thresholds/fe/dof-scan/finish.npy .")

    with open("finish.npy", 'wb') as f:
        results = np.load(f)

    for i in range(3):
        for j, dof in enumerate(DOFS):
            axs[i].fill_between(xs, results[j, :,i,0], results[j, :,i,4], alpha=0.3, color=f"C{j}")
            axs[i].fill_between(xs, results[j, :,i,1], results[j, :,i,3], alpha=0.5, color=f"C{j}")
            axs[i].plot(xs, results[j, :,i,2], color=f"C{j}", label=str(dof))
    
    fig.tight_layout()
    fig.savefig("scan.png")
    #fig.savefig("scan.pdf")

if __name__ == "__main__":
    scan()
    #draw()