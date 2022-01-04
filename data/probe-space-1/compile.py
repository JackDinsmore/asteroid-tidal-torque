# Goal: spawn a bunch of runs that cover the parameter space.
from matplotlib import pyplot as plt
import numpy as np
import os
import matplotlib as mpl
mpl.rcParams['text.usetex'] = True

names = []
points = []
file_names = os.listdir()
file_names.sort()

DIFF_EXPECTED_FACTOR = [1e-2, 1e-5, 1e-4]
END_LENGTH = 100

# Fill points
for bare in file_names:
    if not os.path.isdir(bare):
        continue
    f = open("{0}/{0}.txt".format(bare), 'r')
    max_j, max_l = f.readline().split(", ")
    max_j, max_l = (int(max_j), int(max_l))
    num_fits = [int(i) for i in f.readline().split(', ')]
    cadence = int(f.readline())
    impact_parameter = int(f.readline())
    radius = float(f.readline())
    speed = float(f.readline())
    spin = [float(x) for x in f.readline().split(',')]
    jlms = [float(x) for x in f.readline().split(',')]
    theta_true = [float(x) for x in f.readline().split(',')]
    theta_high = [float(x) for x in f.readline().split(',')]
    theta_low = [float(x) for x in f.readline().split(',')]
    SIGMA = float(f.readline())
    f.close()
    names.append(bare)
    points.append(theta_true)
points = np.array(points)

plt.figure()
for i, point in enumerate(points):
    success_count = 0
    for file in os.listdir(names[i]):
        if file[-11:] == "samples.npy":
            success_count += 1
    plt.text(x=point[1], y=point[2], s=str(success_count))
plt.title("Distribution of parameter points")
plt.xlim(-0.15, 0.15)
plt.ylim(-0.28, 0.03)
plt.show()

# Plot pdfs
def plot_pdf(index):
    side_length = int(-0.5 + np.sqrt(1 + 8 * len(names)) / 2)
    fig = plt.figure(constrained_layout=True, figsize=(10, 7))
    gs = fig.add_gridspec(side_length, 2 * side_length)
    ax_min = 0
    ax_max = 0
    axs = []
    for i in range(side_length):
        for j in range(side_length):
            if i < j:
                continue
            ax = fig.add_subplot(gs[i, (side_length-i)+2*j-1:(side_length-i)+2*j+1])
            ax.set_axis_off()
            #ax.set_yticklabels([])
            axs.append(ax)

            name_index = j + i * (i+1) // 2

            data = []# file, means
            for file in os.listdir(names[name_index]):
                if not file[-11:] == "samples.npy": continue
                array = np.loadtxt("{}/{}".format(names[name_index], file))[index]
                means = np.mean(array)
                data.append((file, means))

            ### I took this apart
            sys.exit()

            # plot the minimizing array
            if min_dist is None or min_dist > DIFF_THRESHOLD[index]:
                continue
            array = np.loadtxt("{}/{}".format(names[name_index], min_file))[index] - points[name_index][index]
            _, bins, _ = ax.hist(array, bins=12, fill=False, density=True)
            ax_min = min(ax_min, np.min(bins))
            ax_max = max(ax_max, np.max(bins))
            ax.text(x=0.05, y=0.9, s="{}".format(name_index), transform=ax.transAxes)
            ax.axvline(x=0, color='b')

    for i, ax in enumerate(axs):
        ax.set_xlim(ax_min, ax_max)
        #if i < len(names) - side_length:
        #    ax.set_xticklabels([])

    fig.savefig("theta-{}-hists.png".format(index))

def covariance():
    side_length = int(-0.5 + np.sqrt(1 + 8 * len(names)) / 2)
    X = []
    Y = []
    cov_data = []
    corr_data = []
    sigma1_data = []
    sigma2_data = []
    for i, y in enumerate(np.linspace(0, -0.25, side_length)):
        cov_data_line = []
        corr_data_line = []
        sigma1_data_line = []
        sigma2_data_line = []
        X_line = []
        Y_line = []
        delta = 0.25 / side_length / 2 * (side_length - i - 1)
        for j, x in enumerate(np.linspace(-0.125+delta, 0.125+delta, side_length)):
            index = i * (i + 1) // 2 + j
            if i < j:
                cov = np.array([[np.nan, np.nan], [np.nan, np.nan]])
            elif j == 0 or j == i or i == side_length - 1:
                cov = np.array([[np.nan, np.nan], [np.nan, np.nan]])
            else:
                # Which data file is the given coords?
                data = [] # file, diffs, covs
                for file in os.listdir(names[index]):
                    if not file[-11:] == "samples.npy": continue
                    with open(f"{names[index]}/{file}", 'rb') as f:
                        #print(f"{names[index]}/{file}")
                        arrays = np.load(f).transpose()#[:,:,-END_LENGTH:]
                        if arrays.shape[1] == 0:
                            continue
                        arrays = arrays.reshape(arrays.shape[0], arrays.shape[1] * arrays.shape[2])
                        diffs = np.mean(arrays, axis=1) - points[index]
                        cov = np.cov(arrays[1], arrays[2]) / SIGMA**2
                    data.append((file, diffs, cov))

                weights = [np.sum((data_row[1] / DIFF_EXPECTED_FACTOR) ** 2 ) for data_row in data]
                if len(weights) == 0:
                    cov = np.array([[np.nan, np.nan], [np.nan, np.nan]])
                else:
                    min_index = np.argmin(weights)
                    _, _, cov = data[min_index]
                
            corr = cov[0][1] / np.sqrt(cov[0][0] * cov[1][1])
            cov_data_line.append(cov[0][1])
            corr_data_line.append(corr)
            sigma1_data_line.append(np.sqrt(cov[0][0]))
            sigma2_data_line.append(np.sqrt(cov[1][1]))

            if not np.isnan(corr):
                print(np.sqrt(cov[0][0]), names[index])

            X_line.append(x)
            Y_line.append(y)
        cov_data.append(cov_data_line)
        corr_data.append(corr_data_line)
        sigma1_data.append(sigma1_data_line)
        sigma2_data.append(sigma2_data_line)
        X.append(X_line)
        Y.append(Y_line)


    plt.figure(figsize=(8, 6))
    c = plt.contourf(X, Y, cov_data)
    axc = plt.colorbar(c)
    axc.set_label("$\\textrm{Cov}(\\theta_2, \\theta_3)/\\sigma_\\theta^2$")
    plt.xlim(-0.125, 0.125)
    plt.ylim(-0.25, 0)
    plt.xlabel("$\\theta_2$")
    plt.ylabel("$\\theta_3$")
    plt.title("Covariance between shape parameters")
    plt.savefig("cov.png")


    plt.figure(figsize=(8, 6))
    c = plt.contourf(X, Y, corr_data)
    axc = plt.colorbar(c)
    axc.set_label("$\\textrm{Corr}(\\theta_2, \\theta_3)$")
    plt.xlim(-0.125, 0.125)
    plt.ylim(-0.25, 0)
    plt.xlabel("$\\theta_2$")
    plt.ylabel("$\\theta_3$")
    plt.title("Correlation between shape parameters")
    plt.savefig("corr.png")

    plt.figure(figsize=(8, 6))
    c = plt.contourf(X, Y, sigma1_data)
    axc = plt.colorbar(c)
    plt.xlim(-0.125, 0.125)
    plt.ylim(-0.25, 0)
    axc.set_label("$\\sigma(\\theta_2)/\\sigma_\\theta$")
    plt.xlabel("$\\theta_2$")
    plt.ylabel("$\\theta_3$")
    plt.title("Variance of $\\theta_2$")
    plt.savefig("theta-2-sigma.png")

    plt.figure(figsize=(8, 6))
    c = plt.contourf(X, Y, sigma2_data)
    axc = plt.colorbar(c)
    plt.xlim(-0.125, 0.125)
    plt.ylim(-0.25, 0)
    axc.set_label("$\\sigma(\\theta_3)/\\sigma_\\theta$")
    plt.xlabel("$\\theta_2$")
    plt.ylabel("$\\theta_3$")
    plt.title("Variance of $\\theta_3$")
    plt.savefig("theta-3-sigma.png")


if __name__ == "__main__":
    covariance()
    plt.show()
    #plot_pdf(1)
    #plt.show()
    #plot_pdf(2)
    #plt.show()
