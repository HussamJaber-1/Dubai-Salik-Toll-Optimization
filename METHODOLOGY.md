Methodology

This project analyzes toll adoption behavior in Dubai’s Salik road pricing system using a simulation-based methodology that combines transportation network modeling, economic decision theory, and machine learning.

The goal is to understand how drivers choose between free and tolled routes when faced with tradeoffs between travel time and toll cost. In many navigation systems, toll usage is treated as a binary option where drivers either avoid tolls entirely or allow them freely. However, in practice, drivers often make marginal economic decisions, sometimes choosing to pay for certain tolls but not others depending on the time savings involved.

To investigate this behavior, a full simulation pipeline was constructed using a graph representation of Dubai’s road network. The system generates multiple candidate routes between origins and destinations, evaluates them under different traffic conditions, and simulates driver decisions using a generalized cost model.

The methodology consists of the following stages:
	1.	Environment configuration and experiment design
	2.	Road network construction
	3.	Toll gate detection and tagging
	4.	Origin–destination corridor selection
	5.	Route generation
	6.	Congestion modeling
	7.	Simulation experiment construction
	8.	Economic route choice modeling
	9.	Behavioral switching analysis
	10.	Congestion sensitivity analysis
	11.	Break-even value-of-time analysis
	12.	Machine learning dataset construction
	13.	Predictive modeling of toll adoption
	14.	Model evaluation and interpretation
	15.	Binary versus multi-option routing analysis

Each stage is described in detail below.

⸻

1. Environment Configuration and Experiment Design

The experiment begins by defining the core parameters controlling the simulation.

Three representative departure hours are used:

8 – morning peak commuting period
14 – midday off-peak period
18 – evening peak commuting period

These hours were chosen to capture typical daily traffic variations without requiring continuous time simulation.

Driver heterogeneity is modeled using six possible values of time (VOT):

0.2 AED per minute
0.5 AED per minute
1.0 AED per minute
2.0 AED per minute
4.0 AED per minute
6.0 AED per minute

These values represent different driver types ranging from highly price-sensitive travelers to highly time-sensitive commuters.

The experiment also defines three congestion scenarios:

Baseline – normal traffic conditions
Mild – moderate congestion
Severe – heavy congestion

These scenarios allow the model to evaluate how traffic conditions influence toll adoption behavior.

Several route-generation parameters are also defined:

Three deterministic shortest paths are generated for each corridor.
Three additional routes are generated using penalized rerouting.
Six routes are generated using stochastic travel-time perturbations.

This produces a diverse set of candidate routes while keeping computation manageable.

A global random seed is used to ensure reproducibility of results.

⸻

2. Road Network Construction

The Dubai road network is extracted using the OSMnx library and stored as a directed graph.

In this graph representation:

Nodes represent road intersections or endpoints.
Edges represent road segments connecting intersections.

The network used in the experiment contains approximately:

61,000 nodes
124,000 edges

Each road segment contains attributes such as:

road classification
segment length
geometry
speed estimate

Travel time for each road segment is calculated using estimated speed values and segment lengths. Travel time is computed as the distance divided by estimated speed.

The graph is then restricted to the largest weakly connected component. This ensures that all selected origin–destination pairs are connected through the network and prevents routing failures caused by isolated road fragments.

⸻

3. Toll Gate Detection

Salik toll gate locations are loaded from a dataset containing the geographic coordinates of each toll gantry in Dubai.

Each toll gate is assigned a detection radius of approximately 200 meters. This radius accounts for small spatial inaccuracies between gate coordinates and the exact geometry of nearby roads.

To identify toll road segments:
	1.	Road edges are converted into a spatial GeoDataFrame.
	2.	Each toll gate is converted into a point geometry.
	3.	Circular buffers are created around each gate using the defined radius.
	4.	Spatial intersection is used to identify road segments intersecting these buffers.

Road segments intersecting a gate buffer are tagged with the attributes:

is_toll = True
toll_gate = gate name

Approximately 265 road segments in the network are identified as toll segments.

These tags allow the routing algorithm to detect when a route crosses toll infrastructure.

⸻

4. Origin–Destination Corridor Selection

To evaluate realistic travel patterns, a set of major Dubai districts is selected.

Locations included in the experiment:

Marina
JLT
Barsha
Downtown
Business Bay
Dubai International Airport (DXB)
Mirdif
Qusais
Deira
Jebel Ali

Origins are selected from three major residential areas:

Marina
JLT
Barsha

Destinations include seven major commercial and transport hubs.

All valid combinations between these origins and destinations are evaluated, producing:

21 origin–destination corridors.

These corridors represent common commuting patterns across the city.

⸻

5. Route Generation

For each origin–destination pair, multiple candidate routes are generated to represent realistic route alternatives available to drivers.

Three complementary techniques are used.

First, shortest paths are generated based on travel time. These represent the fastest routes available in the network.

Second, penalized rerouting is applied. After selecting a route, the travel time of its edges is temporarily increased. This discourages the algorithm from repeatedly selecting the same route and encourages exploration of alternative corridors.

Third, stochastic route generation is applied. Travel times are randomly perturbed within a small range to simulate variability in traffic conditions and driver behavior. This produces additional routes that may become optimal under slightly different circumstances.

After removing duplicate routes, each corridor typically contains between five and seven distinct candidate routes, although the algorithm allows up to thirty possible routes if necessary.

⸻

6. Congestion Modeling

Traffic congestion is simulated using travel-time multipliers applied to road segments.

Three congestion scenarios are considered:

Baseline – no congestion adjustment
Mild congestion – moderate travel-time increases
Severe congestion – large travel-time increases

Congestion multipliers depend on both road type and time of day.

Major highways experience smaller congestion increases than local streets because they have higher capacity and are designed for heavy traffic.

Minor roads experience larger congestion increases during peak periods because they are more susceptible to traffic buildup.

This simplified congestion model approximates realistic traffic conditions without requiring real-time traffic data.

⸻

7. Simulation Experiment Construction

The full experiment evaluates route choices across multiple dimensions.

Origin–destination pairs: 21
Departure hours: 3
Congestion levels: 3

This produces:

189 simulated traffic scenarios.

Each scenario contains multiple candidate routes, each with a travel time and toll cost.

⸻

8. Economic Route Choice Model

Driver decisions are modeled using a generalized cost framework.

Generalized Cost = Travel Time × Value of Time + Toll Cost

Where:

Travel Time represents the route duration in minutes.

Value of Time represents how much a driver values time savings, measured in AED per minute.

Toll Cost represents the total toll price incurred along the route.

For each driver type, the model selects the route that minimizes generalized travel cost.

This framework allows the simulation to represent heterogeneous driver preferences.

⸻

9. Behavioral Switching Analysis

The model examines whether drivers switch between routes as their value of time increases.

A switching event occurs when the optimal route changes for different value-of-time levels.

For example:

Low value-of-time drivers may choose free routes.

Drivers with higher value-of-time may choose faster tolled routes.

By evaluating route choices across multiple value-of-time levels, the simulation identifies corridors where route choices change as economic preferences vary.

⸻

10. Congestion Sensitivity Analysis

The model also evaluates how congestion affects route choice.

For each origin–destination corridor and departure hour, route choices under baseline conditions are compared with route choices under severe congestion.

If the optimal route changes due to congestion, the decision is recorded as a congestion-induced route change.

This analysis measures how sensitive toll adoption behavior is to traffic conditions.

⸻

11. Break-Even Value of Time

For toll routes that provide travel time savings, the break-even value of time is calculated.

Break-Even Value of Time = Toll Cost / Time Saved

This value represents the minimum driver value of time required for a toll route to become economically rational.

Analyzing the distribution of break-even values provides insight into which driver types are most likely to adopt toll routes.

⸻

12. Machine Learning Dataset Construction

To further analyze toll adoption behavior, the simulation results are converted into a machine learning dataset.

Each row in the dataset represents a simulated driver decision under a specific travel scenario.

The dataset includes the following features:

Value of Time
Peak hour indicator
Congestion severity
Travel time saved relative to the fastest free route
Time saved per unit of toll cost

The target variable indicates whether the chosen route includes toll infrastructure.

The resulting dataset contains approximately 1,134 observations.

⸻

13. Predictive Modeling

Two machine learning models are trained to predict toll adoption.

Logistic Regression

Logistic regression provides an interpretable baseline model that estimates the probability that a driver chooses a toll route.

Random Forest

A random forest classifier is used to capture potential nonlinear relationships between variables.

Model training uses a group-based cross-validation strategy to prevent data leakage between similar route scenarios.

⸻

14. Model Evaluation

Model performance is evaluated using several metrics.

Accuracy measures overall classification performance.

ROC-AUC evaluates the model’s ability to distinguish between toll and non-toll decisions.

Precision, recall, and F1 score evaluate the balance between false positives and false negatives.

Feature importance analysis is also conducted to identify which variables most strongly influence toll adoption decisions.

The results show that driver value of time is the most important predictor of toll usage.

⸻

15. Binary Versus Multi-Option Routing

Finally, the experiment evaluates whether route recommendation systems should offer more than two routing options.

Traditional navigation systems often present only two choices:

Free route
Fastest route

However, many corridors also contain intermediate routes that involve moderate toll usage.

The simulation compares:

Binary routing (free vs fastest)
Tri-option routing (free, moderate toll, high toll)

This analysis measures how often the intermediate option produces a better economic outcome for drivers.

⸻

Experimental Assumptions

Several simplifying assumptions are made in the experiment.

Driver behavior is modeled using rational cost minimization rather than real-world behavioral data.

Congestion is simulated using deterministic multipliers rather than live traffic feeds.

Travel demand is represented using a limited set of representative corridors rather than the full city demand distribution.

Despite these simplifications, the simulation captures key economic tradeoffs present in real-world toll systems.

⸻

Threats to Validity

Several limitations may influence the results.

Road network data is derived from OpenStreetMap, which may contain small inaccuracies.

Congestion effects are approximated rather than measured from real traffic data.

Driver value-of-time distributions are assumed rather than empirically estimated.

Future work could incorporate real traffic APIs, historical toll transaction data, and larger sets of travel corridors.

⸻

Summary

This methodology combines network simulation, economic modeling, and machine learning to analyze toll adoption behavior in Dubai’s Salik system.

By evaluating multiple routes, traffic conditions, and driver preferences, the model reveals how urban road networks produce complex tradeoffs between travel time and toll cost.

The results demonstrate that toll adoption decisions are not binary but instead depend on economic tradeoffs that vary across drivers and traffic conditions.
