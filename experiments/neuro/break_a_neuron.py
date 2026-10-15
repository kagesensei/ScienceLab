"""Break a neuron from the command line and compare it to a healthy one.

Examples:
    python experiments/neuro/break_a_neuron.py --na 0.3          # 70% of sodium channels blocked
    python experiments/neuro/break_a_neuron.py --ek -50          # high potassium outside the cell
    python experiments/neuro/break_a_neuron.py --temp 30         # heat
    python experiments/neuro/break_a_neuron.py --na 0.5 --temp 20 --pulse 40
"""

from __future__ import annotations

import argparse
from dataclasses import replace

import matplotlib.pyplot as plt

from sciencelab.neuro import HHParams, HHResult, count_spikes, simulate, step_current

STUCK_ABOVE_MV = -55.0  # a healthy cell returns to about -65 mV after a spike


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--na", type=float, default=1.0, help="fraction of sodium channels left (0-1)")
    p.add_argument("--k", type=float, default=1.0, help="fraction of potassium channels left (0-1)")
    p.add_argument("--ek", type=float, default=-77.0, help="potassium reversal potential, mV")
    p.add_argument("--temp", type=float, default=6.3, help="temperature, °C")
    p.add_argument("--pulse", type=float, default=20.0, help="stimulus strength, µA/cm²")
    p.add_argument("--width", type=float, default=1.0, help="stimulus duration, ms")
    p.add_argument("--t-stop", type=float, default=30.0, help="simulation length, ms")
    p.add_argument("--no-plot", action="store_true", help="print results only")
    return p.parse_args()


def verdict(r: HHResult) -> str:
    spikes = count_spikes(r.V)
    stuck = r.V[-1] > STUCK_ABOVE_MV
    if spikes == 0:
        return "STUCK depolarized, cannot fire" if stuck else "SILENCED, no spike"
    if stuck:
        return f"fired {spikes}x then got STUCK (depolarization block)"
    return f"fires normally ({spikes} spike{'s' if spikes > 1 else ''})"


def report(label: str, r: HHResult) -> None:
    print(f"{label:<9} peak {r.V.max():6.1f} mV | ends at {r.V[-1]:6.1f} mV | {verdict(r)}")


def main() -> None:
    a = parse_args()
    healthy = HHParams()
    broken = replace(
        healthy,
        g_Na=healthy.g_Na * a.na,
        g_K=healthy.g_K * a.k,
        E_K=a.ek,
        temperature_c=a.temp,
    )
    stim = step_current(a.pulse, start=5.0, duration=a.width)
    ok = simulate(healthy, stim, t_stop=a.t_stop)
    bad = simulate(broken, stim, t_stop=a.t_stop)

    report("healthy", ok)
    report("modified", bad)
    if a.no_plot:
        return

    plt.plot(ok.t, ok.V, "k", alpha=0.4, label="healthy")
    plt.plot(bad.t, bad.V, "r", label=f"na={a.na} k={a.k} ek={a.ek} temp={a.temp}")
    plt.ylim(-100, 60)
    plt.xlabel("time (ms)")
    plt.ylabel("membrane voltage (mV)")
    plt.title(verdict(bad))
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()


if __name__ == "__main__":
    main()
