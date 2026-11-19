# Comparison methods

| File | What it is |
|---|---|
| `classical.py` | stock social-force controller, A* with pure pursuit, and the culture-blind reward of SAC-blind |
| `orca.py` | ORCA (optimal reciprocal collision avoidance), adapted to a car-like robot |
| `he2025.py` | the risk-field reward of SAC-risk (after He et al., 2025) |
| `attention_weighting.py` | the attention layer that sets the reward weights of SAC-Attn |
| `cone_filter.py` | the cone safety filter (the baseline for the swept-path filter) |

The tuned social force is in `navstack/sf_prior.py`. The classical drivers are tested with
`evaluation/eval_classical.py`.
