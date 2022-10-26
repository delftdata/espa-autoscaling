# Data processing
#### Author: Job Kanis



# File Structure

## helperclasses.py
Contain helperclasses and two generator functions that help generate the classes.

### Classes
#### Metric
Contains all possible metrics

#### Query
Contains all possible queries

#### Autoscaler
Contains all possible autoscalers and all possibel configurations of these autoscalers

#### Experiment
Represents a valid experiment configuration, including a Query, Autoscaler and AutoscalerVariable.
Experiment complains on creation, if it contains a non-valid configuration.
The ExperimentClass can be used to generate a list of all valid experiment configurations.

#### ExperimentFile
A combination of an experiment and a corresponding datafile located on the system. 

Filenames are generated from Experiment classes and are given the following structure:
  * {label}_q{query}_{autoscaler}_{variable}.csv
  * label is an optional field here that can be used for identifying similar experiments in different runs 

Labels until now:
  * or: /orginal: refers to experiments performed by Wybe on Google Cloud
  * rd: /redone: refers to experiments repeated by Job Kanis on st2 Minikube with a single node
  * 4n: /setup: refers to experiments perfomed by Job Kanis on st2 Minikube with 4 nodes
  * Other labels are a combination of these labels: rd_or, rd_4n_or, etc.

### Functions:

#### Function 1: getAllAvailableExperimentFiles
Input: 
* Directory: directory to get all available source files from. Experiments are fetched from any 'valid' experiment.
* configuration. 
* Label: optional label as prefix of the file. 
* PrintingEnabled: print error messages

Output:
* All Experiment files with the provided label that were found in the source directory.

#### Function 2: getAvailableExperimentFiles
Input:
  * Directory: source directory to fetch source files from. Only provided experiments are fetched.
  * getAvailableExperimentFiles: experiments of which the corresponding files should be fetched.
  * label: optional prefix of the file
  * PrintingEnabled: print error messages

Output: 
 * A list of ExperimentFile classes which contain an experiment and a file location. 
 * ExperimentFiles that could not find a corresponding file are not included in this list.


## helperfunctions.py

The helperfunctions file contains more standalone functions with specialised functionality

### fastCombineSimilarExperiments
Given a list of ExperimentFiles, combine all similar experiments (same autoscaler, query, and variable) in a list 
and return all combinations in a list.
Input [ExperimentList]
Output [[ExperimentList]]
This function can be used to find all similar experiments to combine them in a single graph plot. This is, for example,
usefull when investigating different experimental setups.

### deleteTooSmallLists
Input: [[Var]] and a minimum size n
Goal: filter out all lists in the input list that are smaller than n
Return [[Var]] with all lists inside the list being larger than n.

## plotting.py
Contains all functionality to plot data.

### plotDataFile
Input: 
* ExperimentFile to plot
* (optional) Savelocation
* (optional) Metrics: metrics to plot, all are selected by default
The funtion plots the ExperimentFile and saves the plot on SaveLocation or simply shows it.

### overlapAndPlotMultipleDataFiles
Input:
* [ExperimentFiles]: List of ExperimentFiles to plot in a single graph
* (optional) Savelocation location to save the final plot. Plot is only shown when not set.
* (optional) SaveName: name to save the final plot. Plot is only shown when not set.
* (optional) Metrics: metrics to plot, all are selected by default
The function plots all provided experiments in the same graph and stores them (optionally) on the provided location

### run_experiments
Main function of the entire application. Function can be configured and run from console.
The variables 
* Queries
* Autoscalers
* Metrics
Can be configured to limit the search of the application for certain experiments.

The following actions can be performed:

#### individual plots
Create individual plots of all experiment files found in the provided folder with a certain prefix (label).
Label is optional and will be "" on default.
Datafiles should be stored in {input_folder}/full-data
Results are stored in {input_folder}/graphs/individual-plots
Commandline command:
```
python3 run_experiments.py individual {input_folder} (label)
```

Example:
```
Plot: individual
    python3 {python-file}       {function}      source_folder   label
    python3 run_experiments.py  individual      ./query-1       (rd)
```

#### autoscaler configuration plots
Create plots run on the same experiment (same query and autoscaler), but with different autoscaler configurations.
In the file, all similar autoscalers that executed the same query are grouped and plotted in the same graph.
Label is optional and will be "" on default.
Datafiles should be stored in {input_folder}/full-data
Results are stored in {{input_folder}/graphs/autoscaler-variables-combined
Commandline command:
```
python3 autoscaler run_experiments.py input_folder (label)
```

##### Example:
```
Plot: autoscaler 
    python3 {python-file}       {function}      source_folder   label
    python3 run_experiments.py  individual      ./query-1       (rd)
```


#### autoscaler comparison plot
Creates a plot of different experiments that were performed on the same query, autoscaler and query. This is useful
for comparing different experimental setups. The application automatically fetches all valid experiments present on the specified location 
and having the provided prefix. The system then groups the same experiments together and plots them if they fulfill the 'min_combinations' criteria.

It requires as input the destination folder to save the resulting plots.
The result_label to use as prefix of the file. The file is saved at {prefix}_q{query}_{autoscaler_{configuration}.png
min-combinations: an integer stating the least amount of different data_sources should be used in the graph
Minimal 2 times a source folder followed by the corresponding prefix. 
Datafiles should be stored in {input_folder}/full-data
Commandline:
```
python3 comparison dest_folder result_label min_combinations[INT] \
        src_folder1 label1 src_folder2 label2 [src_foldern labeln]
```

Example: 
```
Plot: comparison
    python3 {python-file}       {function}      dst_folder   result_label   src_folder 1    label 1  src_folder 2       label 2
    python3 run_experiments.py  comparison      ./comparison rd-og          ./redo/query-1  rd       ./origin/query-1   or    
```

#### query run autoscaler pareto plot
Create a pareto plot of the results of a specific query.
Providing the data_folder, the label and the query the to create a plot from, the function fetches all corresponding 
datafiles from the folder and creates a pareto plot from it. The user can specify which metrics to plot on the x-axis and the y-axis.
Metrics can be: [input_rate, taskmanager, latency, lag, throughput, CPU_load, backpressure, busy_time, idle_time]
By default the variables are x-axes: "taskmanager" and y-axis: "latency".
The file is then stored in {src_folder}/graphs/pareto-plots with the following name {prefix}_q{query}_{xMetric}_{yMetric}.
The function fetches all data_files regarding the provided query 

```
python3 pareto src_folder src_label query xMetric yMetric xMetric_limit yMetric_limit 
```
Examples:
```
Plot: pareto
    python3 run_experiments.py pareto ./query-1 rd 1 CPU_load backpressure 16 50
    python3 run_experiments.py pareto ./query-1 rd 1 CPU_load backpressure
    python3 run_experiments.py pareto ./query-1 rd 1 
```


# Plot generation commandline executions

## Individual - generate all individual experiment graphs
Data is present on src_folder/full-data
Plots are saved on src_folder/graphs/individual-plots
```
QUERY=11
python3 ./data_processing/run_experiments.py individual ./results/final_results/redone/query-$QUERY rd
python3 ./data_processing/run_experiments.py individual ./results/final_results/original/query-$QUERY or
python3 ./data_processing/run_experiments.py individual ./results/final_results/setup/query-$QUERY 4n
```

## Individual - generate autoscaler configuration experiment graphs
Data is present on src_folder/full-data
Plots are saved on src_folder/graphs/autoscaler-variables-combined
```
QUERY=1
python3 ./data_processing/run_experiments.py autoscaler ./results/final_results/redone/query-$QUERY rd
python3 ./data_processing/run_experiments.py autoscaler ./results/final_results/original/query-$QUERY or
```

### Comparison - Compare original run (Wyske's run) with redo run
Data is present on src_folder/full-data
Plots are saved on /analysis/query-$QUERY/run_comparisons with label rd_or
```
QUERY=1
python3 data_processing/run_experiments.py comparison ./results/final_results/analysis/query-$QUERY/run_comparisons rd_or 2 \
    ./results/final_results/redone/query-$QUERY rd  ./results/final_results/original/query-$QUERY or  
```

### Setup comparison - Compare 4 node run, redo run (single node) and original run (Wyske's run)
Data is present on src_folder/full-data
Plots are saved on /analysis/query-$QUERY/setup_comparison with label 1n_4n_or
``` 
QUERY=1
python3 data_processing/run_experiments.py comparison ./results/final_results/analysis/query-$QUERY/setup_comparison 1n_4n_or 3 \
    ./results/final_results/redone/query-$QUERY rd  \
    ./results/final_results/setup/query-$QUERY 4n \
    ./results/final_results/original/query-$QUERY or 
```

### Experiment comparison - Create Pareto plot of an experiment run
Data is present on src_folder/full-data
Plots are saved on src_folder/graphs/pareto-plots
``` 
QUERY=3
python3 data_processing/run_experiments.py pareto ./results/final_results/redone/query-$QUERY rd $QUERY taskmanager latency
python3 data_processing/run_experiments.py pareto ./results/final_results/original/query-$QUERY or $QUERY taskmanager latency

python3 data_processing/run_experiments.py pareto ./results/final_results/redone/query-$QUERY rd $QUERY taskmanager latency 6 6
python3 data_processing/run_experiments.py pareto ./results/final_results/original/query-$QUERY or $QUERY taskmanager latency 9 50
```

### Get average metrics
```
QUERY=1
python3 ./data_processing/run_experiments.py averages ./results/final_results/redone/query-$QUERY rd True
python3 ./data_processing/run_experiments.py averages ./results/final_results/original/query-$QUERY or True
python3 ./data_processing/run_experiments.py averages ./results/final_results/setup/query-$QUERY 4n True
```



# Plot generation playground
## Q1

### Dhalion
Dhalion 1
```
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --plot_thresholds --autoscaler dhalion -result_label config-dhalion-1 --metric_range lag 0 300000 --metric_range latency 0 12
python3 ./data_processing/cmd_autoscaler_configuration_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --plot_thresholds --autoscaler dhalion -result_label config-dhalion-1 --metric_range lag 0 300000 --metric_range latency 0 20
python3 ./data_processing/cmd_print_average_metrics.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers dhalion --metrics latency taskmanager --addscalingevents
```
HPA
```
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers HPA --plot_thresholds --metric_range CPU_load 0 1

python3 ./data_processing/cmd_print_average_metrics.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers HPA --metrics latency taskmanager --addscalingevents

```
Varga 1 and 2
```
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers varga1 --plot_thresholds --metric_range lag 0 250000
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers varga2 --plot_thresholds --metric_range lag 0 250000

python3 ./data_processing/cmd_print_average_metrics.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers varga2 --metrics latency taskmanager --addscalingevents

```

DS2 original and updated
```
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers ds2-original --plot_thresholds
python3 ./data_processing/cmd_indivual_experiment_plots.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers ds2-updated --plot_thresholds

python ./data_processing\cmd_indivual_experiment_plots.py ./results\final_results\redone\query-%QUERY% rd --autoscalers ds2-updated --queries %QUERY% --plot_thresholds

python3 ./data_processing/cmd_print_average_metrics.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers ds2-original --metrics latency taskmanager --addscalingevents
python3 ./data_processing/cmd_print_average_metrics.py ./results/final_results/redone/query-$QUERY rd --queries $QUERY --autoscalers ds2-updated --metrics latency taskmanager --addscalingevents
```