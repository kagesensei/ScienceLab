# ScienceLab

Science experiments done entirely in software, so nothing living gets hurt.

Inspired by [Alternatives to Animal Testing (IEEE Spectrum)](https://spectrum.ieee.org/alternatives-to-animal-testing).

## Roadmap

1. **Neuroscience** (now): build neurons from the equations up, then break them on purpose.
2. **Forensic pathology** (next): when a simulated system fails, ask what went wrong, why,
   what the consequences are, and whether it can heal. If it "dies," estimate time of death
   from body cooling and work out the cause.
3. **Lab platform** (later): more modules for the rest of the family.

## Layout

```
src/sciencelab/      reusable models (import as `sciencelab.*`)
  neuro/hh.py        Hodgkin-Huxley neuron
experiments/         notebooks, one numbered folder per topic
  neuro/01_a_neuron_from_scratch.ipynb
tests/               checks that the models behave like the real science says
data/                downloaded datasets (git-ignored)
```

## Setup (Windows, PowerShell)

```powershell
python -m venv .venv            # skip if .venv already exists
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\jupyter-lab.exe
```

## A note on "animal-free"

The models here run without harming anything. Some underlying science did come from animal
work (Hodgkin and Huxley used squid axons in 1952), and much public neuroscience data is from
mice. Where there's a choice, this project prefers human-derived data, such as tissue donated
during surgery or cell-based lab assays.
