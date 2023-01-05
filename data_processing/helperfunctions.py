from DataClasses import ExperimentFile

def get_buckets_of_similar_experiments(experiment_files: [ExperimentFile], ignore_query: bool, ignore_autoscaler: bool,
                                       ignore_mode: bool, ignore_tag: bool) -> [[ExperimentFile]]:
    """
    Given a list of experiment_files and boolean indicating which experiment characteristics to ignore in similarity
    comparison, return a list containing lists of experiment_files that are deemed to be 'similar' to each other.
    :param experiment_files: List of ExperimentFiles
    :param ignore_query: Whether to not consider the query of the experiments in the similarity comparison.
    :param ignore_autoscaler: Whether to nto consider the autoscaler of the experiments in the similarity comparison.
    :param ignore_mode: Whether to not consider the mode of the experiments in the similarity comparison.
    :param ignore_tag: Whether to not consider the tag of the experiments in the similarity comparison
    :return: A list of lists containing similar experiment_Files
    """
    experiment_file_buckets: [[str]] = []
    for experiment_file in experiment_files:
        found_bucket = False
        experiment = experiment_file.get_experiment()
        for experiment_file_bucket in experiment_file_buckets:
            experiment_in_bucket = experiment_file_bucket[0].get_experiment()
            if experiment_in_bucket.is_similar_experiment(experiment, ignore_query, ignore_autoscaler, ignore_mode,
                                                          ignore_tag):
                experiment_file_bucket.append(experiment_file)
                found_bucket = True
                break
        if not found_bucket:
            experiment_file_buckets.append([experiment_file])
    return experiment_file_buckets





def fastCombineSimilarExperiments(experimentFiles: [ExperimentFile], ignoreLabel=True):
    """
    Function combines all similar experiments in a single list.
    :param experimentFiles: ExperimentFiles to combine all similar experiments
    :param ignoreLabel: Whether to ignor ethe label recognizing simmilar experiments
    :return: List of lists containing all similar experiments
    """
    combinations = []
    for experimentFile in experimentFiles:
        found = False
        for combination in combinations:
            if experimentFile.experiment.isSimilarExperiment(combination[0].experiment, ignoreLabel=ignoreLabel):
                combination.append(experimentFile)
                found = True
                break
        if not found:
            combinations.append([experimentFile])
    return combinations




def deleteTooSmallLists(experimentFiles: [[ExperimentFile]], minimumSize: int):
    return list(filter(lambda l: len(l) >= minimumSize, experimentFiles))