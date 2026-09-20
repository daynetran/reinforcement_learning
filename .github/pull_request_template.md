<!--
PR TITLE CONVENTION:
Format: [Title][Subtitle][x/n] <Description in 7 words or less, Title Case>
If part of a stack, [x/n] is mandatory (e.g., [1/5]).

Examples:
- [Ch02][Minimal][1/5] Implement Minimal REINFORCE Algorithm
- [Ch02][Improved][2/5] Implement Baseline And Entropy Bonus
- [Ch02][Experiment][3/5] Reproduce Figure 2.4 Baseline Comparison
- [Ch02][Visualizer][4/5] Add Policy Visualizers And Web Simulator
- [Ch02][Docs][5/5] Add Chapter 2 Reference PDF
-->

## 📝 Summary
<!-- What does this PR implement? What chapter or concept from 'Foundations of Deep RL' does it cover? -->

## 🔬 Type of Change
- [ ] New Algorithm Implementation (e.g., policy gradients, value-based, actor-critic)
- [ ] Algorithmic Improvement (e.g., baseline subtraction, entropy regularization, GAE)
- [ ] Experiment & Evaluation (e.g., learning curve comparison, benchmark reproduction)
- [ ] Visualization & Tooling (e.g., trajectory export, GIF generation, web simulator)
- [ ] Refactoring / Documentation / Code Quality

## 🧠 Algorithmic Details & Hyperparameters
- **Environment**: e.g., `CartPole-v1`
- **Key Hyperparameters**:
  - Learning Rate ($\alpha$): 
  - Discount Factor ($\gamma$): 
  - Hidden Dimension: 
  - Baseline / Regularization (if applicable): 

## 📊 Empirical Results & Verification
<!-- Include evaluation reward metrics, learning curve plots, or demonstration GIFs -->
- **Evaluation Reward**: e.g., `500.0 +/- 0.0` over 10 test episodes
- **Artifacts Generated**:
  - [ ] Comparison plot (`*.png`)
  - [ ] Trajectory data (`*.json`)
  - [ ] Demonstration GIF (`*.gif`)
  - [ ] Interactive simulator (`*.html`)

## 🧪 How to Test & Reproduce
```bash
# Activation & execution commands
source .venv/bin/activate
python chapters/chapter_XX/...
```

## ✅ Checklist
- [ ] Code adheres to PEP 8 and passes linter (`ruff check chapters/`).
- [ ] Pythonic docstrings (PEP 257) included for all new functions and classes.
- [ ] Random seed specified for reproducibility.
- [ ] Output artifacts directed to chapter `artifacts/` folder.
- [ ] Documentation updated if applicable.
