# Analysis-project
An analysis and design of algorithms project to analyze and visualize MST algorithms (Kruskal, Prim, Borůvka, Reverse-Delete, Karger) on diverse network datasets. Includes step-by-step visualizations, performance comparisons, and documentation.


Project Overview:
The goal of this project is to implement and compare five algorithms—Kruskal’s, Prim’s, Borůvka’s, Reverse-Delete, and Karger’s for analyzing and visualizing Minimum Spanning Trees (MSTs) and minimum cuts on real-world networks from the Network Repository. We selected the "Web Graphs" category and applied these algorithms to five datasets of varying sizes. Due to visualization challenges with large graphs, we used smaller datasets for visualization purposes. The project includes algorithm implementations, performance analysis, visualization videos.

Team Members:
•	Mamdouh Mohsen
•	Mohamed Refaat
•	Amin El Kady
•	Yassin El Molla
•	Aly El Semary
Selected Network Category: Web Graphs
We chose the "Web Graphs" category, which represents networks of web pages connected by hyperlinks. These graphs are relevant to applications like web crawling, search engine optimization, and network analysis.
Datasets for Analysis
We selected five datasets from the "Web Graphs" category, ensuring a range of sizes:
•	web-spam.mtx: 4,767 nodes, 37,375 edges
•	web-edu.mtx: 3,031 nodes, 6,474 edges
•	web-indochina-2004.mtx: 11,358 nodes, 47,606 edges
•	web-webbase-2001.mtx: 16,062 nodes, 25,593 edges
•	web-stanford.mtx: 281,903 nodes, 2,312,497 edges
Datasets for Visualization
Due to the large size of the web graph datasets, which made visualization computationally infeasible, we used smaller datasets from other categories for visualization:
•	inf-euroroad: 1,174 nodes, 1,417 edges (Kamada-Kawai layout)
•	inf-usair97: 332 nodes, 2,126 edges (Kamada-Kawai layout)
•	power-bcspwr09: 1,724 nodes, 2,394 edges (spring layout)
•	power-bcspwr10: 5,300 nodes, 8,274 edges (spring layout)
•	power-us-grid: 4,941 nodes, 6,594 edges (spring layout)
Algorithms Implemented
We implemented the following algorithms in Python:
1.	Kruskal’s Algorithm: A greedy algorithm that sorts edges by weight and adds them to the MST if they don’t form a cycle, using a Disjoint Set Union (DSU) structure for cycle detection.
2.	Prim’s Algorithm: Grows the MST from a starting vertex by repeatedly adding the smallest edge connecting a new vertex, using a priority queue for efficiency.
3.	Borůvka’s Algorithm: A parallelizable approach that connects components by selecting the smallest outgoing edge from each component until a single MST remains.
4.	Reverse-Delete Algorithm: Starts with all edges and removes the largest ones while ensuring the graph remains connected.
5.	Karger’s Algorithm: A randomized algorithm for finding the minimum cut by contracting edges until two nodes remain. Note: Despite being listed as an MST algorithm in the requirements, Karger’s is traditionally for minimum cuts, and we implemented it as such.

Code Functionality

The code processes the datasets and handles edge cases as follows:
Graph Loading and Preprocessing (graph_utils.py)
•	File Formats: Supports .mtx and .edges files from the Network Repository.
•	Missing Weights: If weights are absent, random weights between 0 and 100 are assigned.
•	Negative Weights: Negative weights are converted to positive by taking their absolute value, ensuring compatibility with MST algorithms.
•	Disconnected Graphs: If a graph is not connected, the largest connected component is used for analysis.
•	Node Remapping: Nodes are remapped to consecutive integers starting from 0 for consistency.
Algorithm Execution (main.py)
•	Each algorithm is applied to all datasets, measuring execution time and total cost (or cut size for Karger’s).
•	Results are cached in a results.pkl file to avoid redundant computations.
•	Parallel processing is used to run algorithms concurrently, improving efficiency.
Visualization (visualize.py)
•	Generates MP4 videos showing the incremental construction of MSTs (or edge contractions for Karger’s).
•	Displays the evolving total edge cost and execution time in each frame.
•	Uses Kamada-Kawai or spring layouts depending on the dataset.
•	Adjusts node sizes and DPI based on graph size for clarity.
Performance Analysis (performance.py)
•	Plots computational cost growth in 3D (nodes vs. edges vs. execution time) using a logarithmic scale for time.
•	Saves individual plots for each algorithm in the visualizations folder.
Repository Structure
•	/src: Algorithm implementations (e.g., kruskal.py, prim.py, etc.) and utility scripts.
•	/data: Network datasets in .mtx or .edges format.
•	/visualizations: Output videos, performance plots, and cached results.
•	/docs: Documentation files for the GitHub Pages site.
Output Summary
Below is a summary of the output from running main.py on the five web graph datasets:
web-stanford (281,903 nodes, 2,312,497 edges)
•	Kruskal: Valid MST: True, Total Cost: 79,076.72, Time: 12.6275s
•	Prim: Valid MST: True, Total Cost: 62,036.38, Time: 634.4860s
•	Borůvka: Valid MST: True, Total Cost: 79,076.72, Time: 23.0669s
•	Reverse-Delete: (Not completed in output)
•	Karger: (Not completed in output)
web-edu (3,031 nodes, 6,474 edges)
•	Kruskal: Valid MST: True, Total Cost: 989.82, Time: 0.0171s
•	Prim: Valid MST: True, Total Cost: 989.82, Time: 0.0416s
•	Borůvka: Valid MST: True, Total Cost: 989.82, Time: 0.0330s
•	Reverse-Delete: Valid MST: True, Total Cost: 989.82, Time: 21.4235s
•	Karger: Cut Size: 0.00, Time: 10.9235s
web-indochina-2004 (11,358 nodes, 47,606 edges)
•	Kruskal: Valid MST: True, Total Cost: 2,720.69, Time: 0.1265s
•	Prim: Valid MST: True, Total Cost: 2,720.69, Time: 0.5177s
•	Borůvka: Valid MST: True, Total Cost: 2,720.69, Time: 0.2680s
•	Reverse-Delete: Valid MST: True, Total Cost: 2,720.69, Time: 955.9757s
•	Karger: Cut Size: 0.00, Time: 211.9107s
web-spam (4,767 nodes, 37,375 edges)
•	Kruskal: Valid MST: True, Total Cost: 1,019.52, Time: 0.0756s
•	Prim: Valid MST: True, Total Cost: 1,019.52, Time: 0.2886s
•	Borůvka: Valid MST: True, Total Cost: 1,019.52, Time: 0.1674s
•	Reverse-Delete: Valid MST: True, Total Cost: 1,019.52, Time: 503.5926s
•	Karger: Cut Size: 0.00, Time: 95.8704s
web-webbase-2001 (16,062 nodes, 25,593 edges)
•	Kruskal: Valid MST: True, Total Cost: 6,604.96, Time: 0.1128s
•	Prim: Valid MST: True, Total Cost: 6,604.96, Time: 0.3621s
•	Borůvka: Valid MST: True, Total Cost: 6,604.96, Time: 0.1973s
•	Reverse-Delete: Valid MST: True, Total Cost: 6,604.96, Time: 462.5775s
•	Karger: Cut Size: 0.00, Time: 188.1209s
Observations
•	Performance: Kruskal’s and Borůvka’s algorithms are generally faster than Prim’s and Reverse-Delete, especially on larger graphs like web-stanford.
•	Cost Discrepancy: For web-stanford, Prim’s total cost (62,036.38) differs from Kruskal’s and Borůvka’s (79,076.72), possibly due to implementation differences or weight handling.
•	Karger’s Issue: Karger’s algorithm consistently returns a cut size of 0.00, suggesting a potential implementation error or unsuitability of the datasets for non-trivial minimum cuts.
Performance Plots
A sample 3D performance plot comparing all five algorithms is available in /visualizations/performance_plot_3d.png. It shows execution time growth with respect to the number of nodes and edges, using a logarithmic scale for clarity.
