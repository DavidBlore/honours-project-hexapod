NB: The suffix number for the `.dat` experiment files indicates the failure scenario

### Failure Scenarios
1 - 1 failed leg
2 - 2 failed legs separated by 2
3 - 2 failed legs separated by 1
4 - 2 failed legs separated by 0

### Directory structure
experiments
├── adaptation_tests
│   ├── run_adapt_tests.py
│   ├── run_adapt_tests_cpg.py
│   ├── run_adapt_tests_cpg_base.py
│   ├── run_adapt_tests_cpg_base_best.py
│   └── run_tripod_tests.py
└── output
    ├── CPG                         <--- All CPG experiments output
    │   ├── 20k
    │   ├── 40k
    │   └── neat-no-adpatation
    └── REF                         <--- All Reference controller experiments output
        ├── 20k
        ├── 40k
        └── tripod-no-adapatation
