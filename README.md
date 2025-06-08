# Combinatorial Optimization (MO824) - Assignment 1

- [Original Brief](enunciado.pdf)
- ~~Report~~ (Incomplete)

---

### 1 Goal

Apply **Lagrangian relaxation** solved with the **sub-gradient method** to obtain **dual and primal bounds** for an integer-linear program.

Work in teams of **2 - 3 students**. Teams will be drawn at random; pairs get a small bonus because they have fewer people.

---

### 2 Problem description

#### 2.1 k-Similar Travelling Salesmen Problem (kSTSP)

Given an undirected complete graph $G=(V,E)$ with two non-negative cost sets
$c^{1}_{e},\;c^{2}_{e}$ for every edge $e\in E$, find **two Hamiltonian cycles of minimum total cost** such that at least **k** edges are common to both tours.

* $k = |V|$ → the tours must be identical.
* $k = 0$ → the tours are completely independent.

A compact ILP model is:

$$
\begin{aligned}
\min\;&\sum_{k\in\{1,2\}}\sum_{e\in E} c^{k}_{e}\,x^{k}_{e} &&(1)\\[2pt]
\text{s.t. }&\sum_{e\in\delta(i)} x^{k}_{e}=2 &&\forall i\in V,\;\forall k\in\{1,2\} &&(2)\\
&\sum_{e\in E(S)} x^{k}_{e}\le |S|-1 &&\forall S\subset V,\;\forall k\in\{1,2\} &&(3)\\
&x^{k}_{e}\;\ge\;z_{e} &&\forall e\in E,\;\forall k\in\{1,2\} &&(4)\\
&\sum_{e\in E} z_{e}\;\ge\;k &&(5)\\
&x^{k}_{e},\,z_{e}\in\{0,1\} &&\forall e\in E,\;\forall k\in\{1,2\} &&(6)
\end{aligned}
$$

* $x^{k}_{e}=1$ if edge $e$ is used by salesman $k$.
* $z_{e}=1$ if edge $e$ is used by **both** salesmen.
* $\delta(i)$: edges incident to vertex $i$.
* $E(S)$: edges with both endpoints in $S$.

(2) enforces degree 2, (3) kills subtours, (4) ties shared-edge variables to the tours, (5) guarantees at least $k$ common edges.

---

### 3 Assignment requirements

#### 3.1 Formulate the relaxation

Propose, write, and justify a **Lagrangian relaxation** of the kSTSP. Clearly state which constraint set you relax.

#### 3.2 Instance generation

Same 12 instances as Assignment 2:

* $|V|\in\{100,150,200,250\}$
* $k\in\{0,\;|V|/2,\;|V|\}$

A text file supplies integer coordinates $(x^{1}_{i},y^{1}_{i},x^{2}_{i},y^{2}_{i})$ for $i=1,\dots,250$.
For each edge $e=(i,j)$:

$$
\begin{aligned}
c^{1}_{e}&=\Bigl\lceil\sqrt{(x^{1}_{i}-x^{1}_{j})^{2}+(y^{1}_{i}-y^{1}_{j})^{2}}\Bigr\rceil,\\
c^{2}_{e}&=\Bigl\lceil\sqrt{(x^{2}_{i}-x^{2}_{j})^{2}+(y^{2}_{i}-y^{2}_{j})^{2}}\Bigr\rceil.
\end{aligned}
$$

Use the **first $|V|$ lines** for an instance with $|V|$ vertices.

#### 3.3 Sub-gradient method

Solve the **Lagrangian dual** with the sub-gradient algorithm.

#### 3.4 Lagrangian heuristic

Design a **Lagrangian heuristic** that converts a relaxed solution into a feasible kSTSP tour pair, yielding a **primal (upper) bound**.

#### 3.5 Experiments

For each instance:

1. Run the sub-gradient method, applying the heuristic at every iteration.
2. Separately, solve the full 2-tour ILP (model above) with a 30-minute cap, recording:

   * best lower/upper bounds,
   * linear relaxation at root,
   * wall-clock time.

Limit **both** approaches to **30 minutes** per instance.

#### 3.6 Submission

Deliver:

* **Source code**
* **Report** (\~5 pages) containing

  * **Lagrangian model**
  * **Pseudocode** of your sub-gradient implementation
  * **Pseudocode** of your Lagrangian heuristic
  * **Results table** — for each instance: best lower bound, best upper bound, runtime (sub-gradient+heuristic) and, for the ILP, LP relaxation, best lower/upper, runtime
  * **Analysis** — interpret the numbers

#### 3.7 Grading criteria

| Area                    | What counts                                                |
| ----------------------- | ---------------------------------------------------------- |
| **Writing**             | Clear, concise, well-structured text                       |
| **Models & Algorithms** | Correct definitions, variables, constraints                |
| **Experiments**         | Sound implementation, reproducibility, instance generation |
| **Analysis**            | Insightful discussion backed by tables/plots               |

---

### 4 References

1. **Gurobi TSP example**: [https://www.gurobi.com/documentation/9.0/examples/tsp\_java.html](https://www.gurobi.com/documentation/9.0/examples/tsp_java.html)
2. **Concorde TSP solver**: [https://www.math.uwaterloo.ca/tsp/concorde.html](https://www.math.uwaterloo.ca/tsp/concorde.html)
