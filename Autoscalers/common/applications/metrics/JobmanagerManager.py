import requests

from common import Configurations


class JobManagerMetricGatherer:
    """
    JobManagerMetricGatherer is responsible for gathering information from the JobManager pod.
    To do so, it uses the address of the jobmanager provided in the configurations folder.
    """
    configurations: Configurations

    def __init__(self, configurations: Configurations):
        """
        Constructor of the JobManagerMetricGatherer
        :param configurations: Current configurations of the run.
        """
        self.configurations = configurations

    @staticmethod
    def __stripOperatorName(operatorName: str):
        """
        The operator names of Prometheus differ from the Jobmanager. While the jobmanager supports " ", ".", and "-",
        Prometheus presents the characters as a "_". To ensure compatibility between the prometheus metrics and the
        jobmanager metrics, characters in the operator names are replaced with "_".
        :param operatorName: Operatorname to replace characters with.
        :return: Operator name that has all forbidden characters replaced with a "_"
        """
        unsupportedCharacters = ["-&gt", " ", ",", ".", "-", ";", "/", ">"]
        for unsupportedCharacter in unsupportedCharacters:
            operatorName = operatorName.replace(unsupportedCharacter, "_")
        return operatorName

    def getJobId(self) -> int:
        """
        Get get the first ID of the listed jobs on the jobmanager.
        :return: The first ID of the listed jobs on the jobmanager.
        """
        job_id_json = requests.get(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/")
        job_id = job_id_json.json()['jobs'][0]['id']
        return job_id

    def __getJobJson(self, job_id=None):
        """
        Get information of the job from the jobmanager. Return this information in json format.
        :param job_id: Optional parameter indicating the current job_id. Is fetched from jobmanager is not provided
        :return: JSON representation of the  job.
        """
        if not job_id:
            job_id = self.getJobId()
        job_plan_json = requests.get(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}").json()
        return job_plan_json

    def __getJobPlanJson(self, job_id=None):
        """
        Get information of the job's plan from the jobmanager. Return this information in json format.
        :param job_id: Optional parameter indicating the current job_id. Is fetched from jobmanager is not provided
        :return: JSON representation of the current plan of the job.
        """
        if not job_id:
            job_id = self.getJobId()
        job_plan_json = requests.get(
            f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/plan").json()
        return job_plan_json

    def __getVerticeJSON(self, vertice_id, job_id=None):
        """
        Get vertice information from the jobmanager. Return this information in json format.
        :param vertice_id: Vertice id to fetch information for
        :param job_id: Optional parameter indicating the current job_id. Is fetched from jobmanager is not provided
        :return: JSON representation of the current status of the vertice.
        """
        if not job_id:
            job_id = self.getJobId()
        vertice_json = requests.get(
            f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/vertices/{vertice_id}").json()
        return vertice_json

    def __getVerticeJSONs(self, job_id=None, job=None) -> [str]:
        """
        Get a list of vertices deployed in the current job
        :param job_id: Optional parameter indicating the current job_id. Is fetched from jobmanager is not provided
        :param job: Optional parameter providing entire job overview. Else it is fetched from jobmanager.
        :return: A list of vertice_id's that are currently deployed in the job
        """
        if not job_id:
            job_id = self.getJobId()
            job = self.__getJobJson(job_id)
        if not job:
            job = self.__getJobJson(job_id)

        vertice_jsons = []
        for vertice_json in job['vertices']:
            vertice_id = vertice_json['id']
            vertice_json = self.__getVerticeJSON(vertice_id, job_id)
            vertice_jsons.append(vertice_json)
        return vertice_jsons


    def getOperatorHostInformation(self, job_id=None, job=None):
        """
        Get a directory with operatorNames as key with as value tuples indicating information of the taskmanagers the
        operator is deployed on. Information consists out of (taskmanager-id, status, duration)
        :param job_id: Optional parameter indicating the current job_id. Is fetched from jobmanager is not provided
        :param job: Optional parameter providing entire job overview. Else it is fetched from jobmanager.
        :return: A directory with {operator -> [(taskmanager_id, taskmanager_status, taskmanager_duration)]} indicating
        on which taskmanagers the operator is deployed and providing the status of this deployment
        """
        if not job_id:
            job_id = self.getJobId()
            job = self.__getJobJson(job_id)
        if not job:
            job = self.__getJobJson(job_id)

        verticeJSONs = self.__getVerticeJSONs(job_id, job)
        taskmanagerMapping = {}
        for verticeJSON in verticeJSONs:
            operatorName = self.__stripOperatorName(verticeJSON['name'])
            taskmanager_information = []
            for subtask_json in verticeJSON['subtasks']:
                taskmanager_information.append((subtask_json['taskmanager-id'], subtask_json['status'],
                                                subtask_json['duration']))
            taskmanagerMapping[operatorName] = taskmanager_information
        return taskmanagerMapping

    def getOperators(self, jobPlan=None) -> {str, int}:
        """
        Get a list of operator names.
        :param jobPlan: Optional parameter providing jobPlan. Else it is fetched from jobmanager.
        :return: A list all operator names in the current jobs plan.
        """
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        node_json = jobPlan['plan']['nodes']
        nodes = list(map(lambda node: self.__stripOperatorName(node['description']), node_json))
        return nodes

    def getIdOperatorMapping(self, jobPlan=None) -> {str, int}:
        """
        Get a mapping between the operator's id and the operator name
        :param jobPlan: Optional parameter providing jobPlan. Else it is fetched from jobmanager.
        :return: A directory with {operator_id -> operator_name}
        """
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        node_json = jobPlan['plan']['nodes']
        operator_id_mapping: {str, str} = {}
        for n in node_json:
            operator_name = self.__stripOperatorName(n['description'])
            operator_id = n['id']
            operator_id_mapping[operator_id] = operator_name
        return operator_id_mapping

    def getOperatorParallelism(self, jobPlan=None) -> {str, int}:
        """
        Get the parallelism of every operator.
        :param jobPlan: Optional parameter providing jobPlan. Else it is fetched from jobmanager.
        :return: A directory with {operator_name -> operator_parallelism}
        """
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        nodes = jobPlan['plan']['nodes']
        parallelisms: {str, int} = {}
        for node in nodes:
            nodeName = self.__stripOperatorName(node['description'])
            nodeParallelism = node['parallelism']
            parallelisms[nodeName] = nodeParallelism
        return parallelisms

    def getTopology(self, jobPlan=None) -> [(str, str)]:
        """
        Get the toplogy of the current jobPlan
        :param jobPlan: Optional parameter providing jobPlan. Else it is fetched from jobmanager.
        :return: List of directed edges l -> r:  [(left operator, right operator)]
        """
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        id_operator_mapping = self.getIdOperatorMapping(jobPlan)

        topology: [(str, str)] = []
        for node_json in jobPlan['plan']['nodes']:
            node_name = self.__stripOperatorName(node_json['description'])
            if "inputs" in node_json:
                for edge_in_json in node_json['inputs']:
                    edge_in_operator_id = edge_in_json['id']
                    if edge_in_operator_id in id_operator_mapping.keys():
                        node_in_name = self.__stripOperatorName(id_operator_mapping[edge_in_operator_id])
                        topology.append((node_in_name, node_name))
        return topology

