# Rebuild the paper's tables and check its numbers

```bash
python paper/build_paper_tables.py     # LaTeX tables -> paper/output/, with a check of every number
python paper/audit_paper_numbers.py    # checks the headline numbers of the text (OK / FAIL)
```

| File | What it does |
|---|---|
| `build_paper_tables.py` | builds the data tables of the paper and supplement from `results/`, `ros2/paper_data/` and `real_robot/data/` |
| `audit_paper_numbers.py` | checks the numbers quoted in the text, such as 0 contacts in 42,500 planner-guided episodes |
| `make_stack_figure.py` | draws the stack overview figure |
| `make_routes_figure.py` | draws the prayer-room routes of the geometric and cultural planners |

Both scripts read the paper's results in `results/`. To use your own runs instead, set
`HOSPITALNAV_RESULTS=runs`. See [docs/07_reproduce_the_paper.md](../docs/07_reproduce_the_paper.md).
