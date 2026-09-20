# Deep Reinforcement Learning Repository

Hands-on reproductions and visualizers following *Foundations of Deep Reinforcement Learning* (Laura Graesser and Wah Loon Keng).

## Project Structure

```text
reinforcement_learning/
├── chapters/
│   ├── chapter_02_reinforce/
│   │   ├── reinforce_minimal.py         # Code 2.1 translation for modern Gymnasium
│   │   ├── reinforce_improved.py        # Baseline mean-centering & entropy bonus
│   │   ├── train_and_evaluate.py        # Figure 2.4 reproduction (Baseline vs No-Baseline)
│   │   ├── visualize.py                 # Exports trajectories & animated GIF
│   │   ├── generate_visualizer.py       # Standalone interactive Canvas visualizer generator
│   │   └── artifacts/                   # Output figures, weights, animations, & HTML
│   │       ├── cartpole_data.json
│   │       ├── cartpole_trained.gif
│   │       ├── cartpole_visualizer.html
│   │       └── reinforce_comparison.png
│   └── (future chapters: 03, 04, ...)
├── requirements.txt
├── README.md
└── .venv/
```

---

## Chapter 2: REINFORCE (Policy Gradients)

### Quickstart

Activate the virtual environment:
```bash
source .venv/bin/activate
```

Run minimal REINFORCE:
```bash
python chapters/chapter_02_reinforce/reinforce_minimal.py
```

Run improved REINFORCE (with baseline return standardization & entropy bonus):
```bash
python chapters/chapter_02_reinforce/reinforce_improved.py
```

Run comparative experiment (Baseline vs No-Baseline) and generate comparison plot:
```bash
python chapters/chapter_02_reinforce/train_and_evaluate.py
```

Train agent, export weights/trajectories, and generate demonstration GIF:
```bash
python chapters/chapter_02_reinforce/visualize.py
```

Generate and open the interactive visualizer in your browser:
```bash
python chapters/chapter_02_reinforce/generate_visualizer.py
open chapters/chapter_02_reinforce/artifacts/cartpole_visualizer.html
```
