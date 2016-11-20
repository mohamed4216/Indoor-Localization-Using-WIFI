import json
import sys

import matplotlib.pyplot as plt

def plot_hoge(filename):
    goals = json.load(open(filename))
    prs = sorted([g['priority'] for g in goals])
    plt.plot(prs)
    plt.ylim(0, 50)
    return prs

if __name__ == '__main__':
    for fn in sys.argv[1:]:
        plot_hoge(fn)
    plt.savefig('hoge.pdf')
