# Aries integration for unified-planning

[Aries](https://github.com/plaans/aries) is an automated planner targeting hierarchical and temporal problems. The objective of Aries is to model and solve hierarchical problems with advanced temporal features and optimization metrics. It relies on the proximity of these with scheduling problems to propose a compilation into a constraint satisfaction formalism. Solving exploits a custom combinatorial solver that leverages the concept of optional variables in scheduling solvers as well as the clause learning mechanisms of SAT solvers.

## Status

Integration into the AIPlan4EU project is ongoing, synchronized with the effort for augmenting the modeling capabilities of the unified-planning library to model hierarchical problems.

## Planning approaches of UP supported

- *Problem kind*: Hierarchical planning
- *Operative mode*: One shot planning


## Installation

To install the library from PyPi, run the following command:

```bash
python3 -m pip install up-aries
```

To install alternative versions of the library, visit the [releases page](https://github.com/plaans/aries/releases/) and download the corresponding tar file.
