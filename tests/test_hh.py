"""Sanity checks against well-known Hodgkin-Huxley behavior."""

from dataclasses import replace

import numpy as np
import pytest

from sciencelab.neuro import HHParams, count_spikes, simulate, step_current


def test_rests_near_minus_65_without_input() -> None:
    r = simulate(t_stop=30.0)
    assert np.allclose(r.V, -65.0, atol=0.1)


def test_weak_pulse_does_not_fire() -> None:
    r = simulate(stimulus=step_current(2.0, start=5.0, duration=1.0), t_stop=30.0)
    assert count_spikes(r.V) == 0


def test_strong_pulse_fires_one_spike_that_overshoots_zero() -> None:
    r = simulate(stimulus=step_current(20.0, start=5.0, duration=1.0), t_stop=30.0)
    assert count_spikes(r.V) == 1
    assert 30.0 < r.V.max() < 50.0  # peaks below E_Na = +50 mV


def test_sustained_current_gives_repetitive_firing() -> None:
    r = simulate(stimulus=step_current(10.0, start=0.0, duration=200.0), t_stop=200.0)
    assert count_spikes(r.V) >= 10


def test_blocking_sodium_channels_abolishes_spiking() -> None:
    blocked = replace(HHParams(), g_Na=0.0)
    r = simulate(blocked, stimulus=step_current(20.0, start=5.0, duration=1.0), t_stop=30.0)
    assert count_spikes(r.V) == 0


def test_currents_balance_once_settled() -> None:
    r = simulate(t_stop=100.0)
    total = r.I_Na + r.I_K + r.I_L
    assert abs(total[-1]) < 1e-4


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"dt": 0.0}, "dt must be"),
        ({"dt": 5.0}, "dt must be"),
        ({"t_stop": -1.0}, "t_stop must be"),
        ({"params": HHParams(C_m=0.0)}, "C_m must be positive"),
        ({"params": HHParams(g_K=-1.0)}, "conductances cannot be negative"),
    ],
)
def test_bad_inputs_are_rejected(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        simulate(**kwargs)  # type: ignore[arg-type]
