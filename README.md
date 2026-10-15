# ScienceLab

After reading the IEEE Spectrum article [Alternatives to Animal Testing](https://spectrum.ieee.org/alternatives-to-animal-testing),
I was fascinated by the idea of using code to perform science experiments without hurting a living
creature! So I created this to flex my interest in Life Sciences harmlessly. I'll focus a lot on
neuroscience and whatever my pre-med daughters are studying!

## Roadmap

1. **Neuroscience** (now): build neurons from the equations up, then break them on purpose.
2. **Forensic pathology** (next): when a simulated system fails, ask what went wrong, why,
   what the consequences are, and whether it can heal. If it "dies," estimate time of death
   from body cooling and work out the cause.
3. **Lab platform** (later): more modules for the rest of the family.

## Experiments

| # | Notebook | What you'll see |
|---|---|---|
| 01 | [A neuron from scratch](experiments/neuro/01_a_neuron_from_scratch.ipynb) | Spikes, thresholds, refractory periods, and what happens when channels, potassium, or temperature go wrong |

## Layout

```
src/sciencelab/      reusable models (import as `sciencelab.*`)
  neuro/hh.py        Hodgkin-Huxley neuron
experiments/         notebooks, one folder per topic
tests/               checks that the models behave like the real science says
data/                downloaded datasets (git-ignored)
```

## Setup

Requires Python 3.11+. On Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\jupyter-lab.exe
```

On macOS/Linux, use `.venv/bin/` instead of `.\.venv\Scripts\`.

## Ground rules

- **Animal-free.** The models run without harming anything. Some underlying science did come
  from animal work (Hodgkin and Huxley used squid axons in 1952), and much public neuroscience
  data is from mice. Where there's a choice, this project prefers human-derived data, such as
  tissue donated during surgery or cell-based lab assays.
- **Open source and public data only.** Every tool is open source, and every dataset is public,
  with its source and license noted where it's used.
- **No personal or health data.** Nothing here contains PII or PHI about anyone. Any data
  recorded for the project comes from things like environmental sensors, never from people.

## Disclaimer

This is a learning project. The models are simplified, and nothing here is medical advice or a
diagnostic tool.

## License

Code is released under the [MIT License](LICENSE). Public datasets keep their own licenses.