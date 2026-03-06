# Dubai Salik Toll Optimization

This project analyzes toll adoption behavior on Dubai’s Salik road pricing system using a combination of transportation economics, network simulation, and machine learning.

Most navigation systems treat toll usage as a binary constraint — either **avoid tolls** or **allow tolls**.  
However, toll adoption is often a **marginal economic decision**, where drivers may rationally choose to pay **some tolls but not others** depending on the time savings.

This project models that decision process on the **Dubai road network**.

---

# Project Objective

The goal of this project is to understand when drivers rationally adopt toll routes based on the trade-off between:

- travel time
- toll cost
- traffic congestion
- individual value of time

The analysis evaluates whether **non-binary toll routing decisions** emerge in realistic road networks.

---

# Methodology

The project follows a simulation pipeline:

1. **Road Network Construction**

Dubai's road network is extracted using **OSMnx**, producing a graph representation of the city.

2. **Toll Gate Mapping**

Salik toll gate coordinates are mapped onto the road network to detect toll crossings along routes.

3. **Route Generation**

For each origin–destination pair, multiple feasible routes are generated.

4. **Economic Cost Model**

Routes are evaluated using generalized travel cost:
Generalized Cost = Travel Time × Value of Time + Toll Cost

5. **Switching Analysis**

The simulation identifies the **Value-of-Time threshold** where drivers switch between toll and non-toll routes.

6. **Machine Learning Layer**

A classifier predicts the **probability of toll adoption** based on observable trip conditions.

---

# Key Results

The simulation produced several insights:

- **76%** of analyzed corridors contain multi-toll alternatives
- **57%** of route choices switch as Value-of-Time increases
- **9.8%** of toll decisions change under severe congestion
- Corridor sensitivity varies between **5% and 33%**

These findings show that toll adoption is **not binary** and depends strongly on economic trade-offs and traffic conditions.

---

# Repository Structure

src/            Core routing and cost models
data/           Salik gates and road network data
notebooks/      Experiments and visualizations
requirements.txt

---

# Technologies Used

- Python
- OSMnx
- NetworkX
- Pandas
- Scikit-learn
- Matplotlib

---

# Limitations

- Driver behavior is simulated rather than based on real toll transaction data
- Congestion is modeled using travel-time multipliers rather than live traffic data
- Only representative origin–destination corridors are evaluated

---

# Author

Hussam Jaber  
MSc Artificial Intelligence
