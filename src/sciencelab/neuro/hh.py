"""Hodgkin-Huxley model of a single patch of excitable membrane.

This is the 1952 model that earned Hodgkin and Huxley the Nobel Prize: four
coupled differential equations that explain how a neuron fires an action
potential. Units throughout:

    voltage      mV
    time         ms
    current      uA/cm^2   (current per unit membrane area)
    conductance  mS/cm^2
    capacitance  uF/cm^2
    temperature  degrees C

The membrane equation is

    C_m dV/dt = I_stim - g_Na m^3 h (V - E_Na) - g_K n^4 (V - E_K) - g_L (V - E_L)

and each gate x in {m, h, n} opens and closes with voltage-dependent rates:

    dx/dt = phi * (alpha_x(V) (1 - x) - beta_x(V) x)

where phi scales the rates with temperature (Q10 = 3, measured at 6.3 C).

Parameters use the modern sign convention (resting potential ~ -65 mV).
They come from squid giant axon recordings, so treat absolute numbers as a
teaching model, not a human neuron.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp

Stimulus = Callable[[float], float]


@dataclass(frozen=True)
class HHParams:
    """Membrane properties. Change one with dataclasses.replace(p, g_Na=...)."""

    C_m: float = 1.0  # membrane capacitance
    g_Na: float = 120.0  # max sodium conductance
    g_K: float = 36.0  # max potassium conductance
    g_L: float = 0.3  # leak conductance
    E_Na: float = 50.0  # sodium reversal potential
    E_K: float = -77.0  # potassium reversal potential
    E_L: float = -54.387  # leak reversal potential (chosen so rest is -65 mV)
    temperature_c: float = 6.3  # the squid experiments were run at 6.3 C
    q10: float = 3.0  # rate speed-up per 10 C of warming

    @property
    def phi(self) -> float:
        return self.q10 ** ((self.temperature_c - 6.3) / 10.0)


@dataclass
class HHResult:
    """Time series from one simulation run."""

    t: np.ndarray
    V: np.ndarray
    m: np.ndarray
    h: np.ndarray
    n: np.ndarray
    I_stim: np.ndarray
    params: HHParams

    @property
    def I_Na(self) -> np.ndarray:
        p = self.params
        return p.g_Na * self.m**3 * self.h * (self.V - p.E_Na)

    @property
    def I_K(self) -> np.ndarray:
        p = self.params
        return p.g_K * self.n**4 * (self.V - p.E_K)

    @property
    def I_L(self) -> np.ndarray:
        p = self.params
        return p.g_L * (self.V - p.E_L)


def _vtrap(x: float, k: float) -> float:
    """x / (1 - exp(-x/k)), safe at x = 0 where the limit is k."""
    u = x / k
    if abs(u) < 1e-6:
        return k * (1.0 + u / 2.0)
    return x / -math.expm1(-u)


def alpha_m(V: float) -> float:
    return 0.1 * _vtrap(V + 40.0, 10.0)


def beta_m(V: float) -> float:
    return 4.0 * math.exp(-(V + 65.0) / 18.0)


def alpha_h(V: float) -> float:
    return 0.07 * math.exp(-(V + 65.0) / 20.0)


def beta_h(V: float) -> float:
    return 1.0 / (1.0 + math.exp(-(V + 35.0) / 10.0))


def alpha_n(V: float) -> float:
    return 0.01 * _vtrap(V + 55.0, 10.0)


def beta_n(V: float) -> float:
    return 0.125 * math.exp(-(V + 65.0) / 80.0)


def steady_state(V: float) -> tuple[float, float, float]:
    """Gate values (m, h, n) a cell would settle to if held at voltage V."""
    m = alpha_m(V) / (alpha_m(V) + beta_m(V))
    h = alpha_h(V) / (alpha_h(V) + beta_h(V))
    n = alpha_n(V) / (alpha_n(V) + beta_n(V))
    return m, h, n


def step_current(amplitude: float, start: float = 5.0, duration: float = 1.0) -> Stimulus:
    """A square pulse of injected current, like an electrode in the lab."""

    def stim(t: float) -> float:
        return amplitude if start <= t < start + duration else 0.0

    return stim


def no_current(t: float) -> float:
    return 0.0


def simulate(
    params: HHParams | None = None,
    stimulus: Stimulus = no_current,
    t_stop: float = 50.0,
    dt: float = 0.01,
    V0: float = -65.0,
) -> HHResult:
    """Integrate the model from rest and return the full time course."""
    p = params or HHParams()
    phi = p.phi

    def rhs(t: float, y: np.ndarray) -> list[float]:
        V, m, h, n = y
        I_ion = (
            p.g_Na * m**3 * h * (V - p.E_Na)
            + p.g_K * n**4 * (V - p.E_K)
            + p.g_L * (V - p.E_L)
        )
        return [
            (stimulus(t) - I_ion) / p.C_m,
            phi * (alpha_m(V) * (1.0 - m) - beta_m(V) * m),
            phi * (alpha_h(V) * (1.0 - h) - beta_h(V) * h),
            phi * (alpha_n(V) * (1.0 - n) - beta_n(V) * n),
        ]

    t_eval = np.arange(0.0, t_stop + dt / 2, dt)
    sol = solve_ivp(
        rhs,
        (0.0, t_eval[-1]),
        [V0, *steady_state(V0)],
        t_eval=t_eval,
        max_step=dt * 5,  # small enough to never step over a short pulse
        rtol=1e-6,
        atol=1e-8,
    )
    if not sol.success:
        raise RuntimeError(f"Integration failed: {sol.message}")

    V, m, h, n = sol.y
    return HHResult(
        t=sol.t,
        V=V,
        m=m,
        h=h,
        n=n,
        I_stim=np.array([stimulus(t) for t in sol.t]),
        params=p,
    )


def count_spikes(V: np.ndarray, threshold: float = 0.0) -> int:
    """Number of upward crossings of the threshold voltage."""
    above = V >= threshold
    return int(np.count_nonzero(~above[:-1] & above[1:]))
