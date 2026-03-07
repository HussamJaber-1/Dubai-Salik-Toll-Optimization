# Dubai Salik Toll Optimization

This project analyzes **toll adoption behavior in Dubai’s Salik road pricing system** using network simulation, transportation economics, and behavioral decision modeling.

Most navigation systems treat toll usage as a **binary constraint**:

- Avoid tolls
- Allow tolls

However, in reality, toll decisions are often **marginal economic choices**. Drivers may rationally choose to pay some tolls but not others depending on the time savings relative to cost.

This project models that decision process on the Dubai road network to evaluate whether **non-binary toll routing behavior naturally emerges**.

---

# Research Question

Do realistic urban road networks produce **multi-toll economic tradeoffs**, where drivers rationally choose between:

- slower free routes  
- partially tolled routes  
- fully tolled fast routes  

depending on their **value of time** and traffic conditions?

---

# Project Objective

The objective is to evaluate when drivers rationally adopt toll routes based on the trade-off between:

- travel time  
- toll cost  
- congestion severity  
- individual **Value of Time (VoT)**  

The project tests whether real road networks produce **economic switching points** where different driver types choose different routes.

---

# Methodology

The project follows a **simulation pipeline composed of five stages**.

## 1. Road Network Construction

Dubai’s road network is extracted using **OSMnx**, which converts OpenStreetMap data into a graph representation where:

- nodes represent intersections
- edges represent road segments

Each edge contains attributes such as:

- road length
- road classification
- travel time

---

## 2. Toll Gate Mapping

Salik toll gate coordinates are mapped onto the road network.

Each road segment near a toll gate is tagged with:

- `is_toll`
- `toll_gate`
- `near_toll`

This allows the routing algorithm to detect when routes cross toll infrastructure.

---

## 3. Route Generation

For each origin–destination corridor, multiple candidate routes are generated using **NetworkX shortest path algorithms**.

Several routing strategies are used:

- fastest routes (minimum travel time)
- shortest distance routes
- toll-penalized routes
- balanced toll strategies
- stochastic driver preference simulations

This produces a **diverse set of feasible travel options** for each trip.

---

## 4. Economic Cost Model

Each route is evaluated using a generalized travel cost function:

```
Generalized Cost = Travel Time × Value of Time + Toll Cost
```

Where:

- Travel Time is measured in minutes
- Value of Time (VoT) represents how much a driver values time savings
- Toll Cost reflects Salik gate pricing

This allows the model to represent **heterogeneous driver preferences**.

---

## 5. Switching Analysis

For competing routes, the model calculates the **break-even Value of Time** at which a driver switches from one route to another.

The switching threshold is defined as:

```
V = (C_B - C_A) / (T_A - T_B)
```

Where:

- **T_A , T_B** = route travel times
- **C_A , C_B** = toll costs

This produces a **behavioral switching curve across driver types**.

---

# Experiment Design

The simulation evaluates multiple travel corridors across Dubai, including:

- Marina → Downtown
- Marina → DXB Airport
- JLT → Deira
- Barsha → Downtown
- Marina → Mirdif
- Marina → Qusais

Each corridor is tested across multiple scenarios:

- different departure hours
- varying congestion conditions
- heterogeneous driver value-of-time distributions

---

# Key Results

The simulation produced several behavioral insights:

- **76%** of analyzed corridors contain multi-toll alternatives
- **57%** of route choices change as Value-of-Time increases
- **9.8%** of toll decisions change under severe congestion
- corridor sensitivity varies between **5% and 33%**

These results indicate that **toll adoption is not binary** and is instead driven by **economic tradeoffs between time and cost**.

---

# Example Tradeoff Structure

| Route Type | Travel Time | Toll Cost |
|------------|-------------|-----------|
| Free Route | 25 min | 0 AED |
| Partial Toll | 20 min | 8 AED |
| Full Toll | 17 min | 12 AED |

Different driver types choose different routes depending on their **Value of Time**.

---

# Repository Structure

```
Dubai-Salik-Toll-Optimization
│
├── data
│   ├── dubai.graphml
│   ├── salik_gates.csv
│   └── tradeoff_data.csv
│
├── notebooks
│   └── notebook_Final.ipynb
│
├── src
│   ├── routing.py
│   ├── toll_detector.py
│   ├── cost_model.py
│   └── analysis.py
│
├── app.py
├── requirements.txt
├── README.md
└── METHODOLOGY.md
```

---

# Technologies Used

- Python  
- OSMnx  
- NetworkX  
- Pandas  
- NumPy  
- Matplotlib  
- Scikit-learn  

These tools are used for:

- road network modeling
- route generation
- economic simulation
- data analysis
- visualization

---

# Limitations

Several simplifying assumptions are made:

- driver behavior is simulated rather than based on real Salik transaction data
- congestion is modeled using travel-time multipliers rather than live traffic feeds
- only representative origin–destination corridors are evaluated
- behavioral parameters (VoT distribution) are approximations

Future work could integrate:

- real traffic APIs
- historical toll usage data
- dynamic congestion models

---

# Future Work

Potential extensions of the project include:

- integration with **live traffic data**
- machine learning prediction of toll adoption
- personalized route recommendations
- reinforcement learning for route optimization
- urban toll pricing policy simulations

---

## Documentation

Detailed project documentation:

- Methodology → methodology.md

---

# Author

**Hussam Jaber**  
MSc Artificial Intelligence  
University of Birmingham
