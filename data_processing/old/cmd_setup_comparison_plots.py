import argparse

from command_functions import includeAutoscalers, includeMetrics, includeQueries, getAutoscalers, getMetrics, \
    getQueries, getDataFolder, getGraphFolder
from DataClasses import ExperimentFile, Experiment
from helperfunctions import fastCombineSimilarExperiments, deleteTooSmallLists
from Plotting import overlapAndPlotMultipleDataFiles


def plotExperimentComparison(result_folder, result_label, minimumCombinations, folders_and_labels : [(str, str)],
                             queries, autoscalers, metrics):
    RESULT_FOLDER = f"{getGraphFolder(result_folder, create_graph_folder=False)}/"
    allExperimentFiles: [ExperimentFile] = []
    for (folder, label) in folders_and_labels:
        folder = getDataFolder(folder)
        # Fetch all possible experiments that can be created using {queries}  and {autoscalers}
        experiments: [Experiment] = Experiment.getAllExperiments(queries, autoscalers, label=label)
        # Fetch all files that correspond to these experiments in folder {folder}
        experimentFiles: [ExperimentFile] = ExperimentFile.getAvailableExperimentFiles(folder, experiments)
        # Append the found files to the allExperimentFiles list
        allExperimentFiles += experimentFiles

    # Combine all ExperimentFiles that ran on the same query, with the same autoscaler and the same configuration.
    # Labels are allowed to differ (as ignoreLabel = True)
    experimentFileLists: [[ExperimentFile]] = fastCombineSimilarExperiments(allExperimentFiles, ignoreLabel=True)
    # Remove all combinations that hold less than {minimumCombinations} amount of files
    experimentFileLists: [[ExperimentFile]] = deleteTooSmallLists(experimentFileLists, minimumCombinations)

    # For every found combination, we create a plot
    for experimentFileList in experimentFileLists:
        expFile0: ExperimentFile = experimentFileList[0]
        query = expFile0.getQuery()
        autoscaler = expFile0.getAutoscaler()
        variable = expFile0.getVariable()

        labelName = f"{result_label}_" if result_label != "" else ""
        fileName = f"{labelName}q{query}_{autoscaler}_{variable}"
        overlapAndPlotMultipleDataFiles(experimentFileList, saveDirectory=RESULT_FOLDER, saveName=fileName,
                                        metrics=metrics)




def parseArguments():
    parser = argparse.ArgumentParser(description='Plot individual experiments')
    parser.add_argument('result_folder', type=str)
    parser.add_argument('result_label', type=str)
    parser.add_argument('min_comparisons', type=int)
    parser.add_argument('-src_folder_labels', type=str, nargs="*")

    includeAutoscalers(parser)
    includeMetrics(parser)
    includeQueries(parser)

    args = parser.parse_args()


    result_folder = args.result_folder
    result_label = args.result_label
    min_comparisons = args.min_comparisons
    src_folder_labels = args.src_folder_labels
    autoscalers = getAutoscalers(args)
    metrics = getMetrics(args)
    queries = getQueries(args)

    if not src_folder_labels or len(src_folder_labels) < 2 or len(src_folder_labels) % 2 != 0:
        print(f"ERROR: not enough folder label pairs in {src_folder_labels}")
        print(f"Canceling execution.")
        return

    comparison_folders_and_labels = list(zip(src_folder_labels[0::2], src_folder_labels[1::2]))
    print(f"Found the following (src_folder, src_label) pairs: {comparison_folders_and_labels}")
    plotExperimentComparison(result_folder, result_label, min_comparisons, comparison_folders_and_labels,
                             queries, autoscalers, metrics)



if __name__ == "__main__":
    parseArguments()
