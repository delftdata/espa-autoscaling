import requests

from common import Configurations


class JobManagerMetricGatherer:
    configurations: Configurations

    def __init__(self, configurations: Configurations):
        self.configurations = configurations

    def __getJobId(self) -> int:
        job_id_json = requests.get(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/")
        job_id = job_id_json.json()['jobs'][0]['id']
        return job_id

    def __getJobJson(self, job_id=None):
        if not job_id:
            job_id = self.__getJobId()
        job_plan_json = requests.get(f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}").json()
        return job_plan_json

    def __getJobPlanJson(self, job_id=None):
        if not job_id:
            job_id = self.__getJobId()
        job_plan_json = requests.get(
            f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/plan").json()
        return job_plan_json

    def __getVerticeJSON(self, vertice_id, job_id=None):
        if not job_id:
            job_id = self.__getJobId()
        vertice_json = requests.get(
            f"http://{self.configurations.FLINK_JOBMANAGER_SERVER}/jobs/{job_id}/vertices/{vertice_id}").json()
        return vertice_json

    def __getVerticeJSONs(self, job_id=None, job=None) -> [str]:
        if not job_id:
            job_id = self.__getJobId()
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
        if not job_id:
            job_id = self.__getJobId()
            job = self.__getJobJson(job_id)
        if not job:
            job = self.__getJobJson(job_id)

        verticeJSONs = self.__getVerticeJSONs(job_id, job)
        taskmanagerMapping = {}
        for verticeJSON in verticeJSONs:
            operator = verticeJSON['name']
            taskmanager_information = []
            for subtask_json in verticeJSON['subtasks']:
                taskmanager_information.append((subtask_json['taskmanager-id'], subtask_json['status'], subtask_json['duration']))
            taskmanagerMapping[operator] = taskmanager_information
        return taskmanagerMapping

    def getOperators(self, jobPlan=None) -> {str, int}:
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        node_json = jobPlan['plan']['nodes']
        nodes = list(map(lambda node: node['description'], node_json))
        return nodes

    def getIdOperatorMapping(self, jobPlan=None) -> {str, int}:
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        node_json = jobPlan['plan']['nodes']
        operator_id_mapping: {str, str} = {}
        for n in node_json:
            operator_id_mapping[n['id']] = n['description']
        return operator_id_mapping

    def getOperatorParallelism(self, jobPlan=None) -> {str, int}:
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        nodes = jobPlan['plan']['nodes']
        parallelisms: {str, int} = {}
        for node in nodes:
            parallelisms[node['description']] = node['parallelism']
        return parallelisms

    def getTopology(self, jobPlan=None) -> [(str, str)]:
        if not jobPlan:
            jobPlan = self.__getJobPlanJson()
        id_operator_mapping = self.getIdOperatorMapping(jobPlan)

        topology: [(str, str)] = []
        for node_json in jobPlan['plan']['nodes']:
            node_name = node_json['description']
            if "inputs" in node_json:
                for edge_in_json in node_json['inputs']:
                    edge_in_operator_id = edge_in_json['id']
                    if edge_in_operator_id in id_operator_mapping.keys():
                        node_in_name = id_operator_mapping[edge_in_operator_id]
                        topology.append((node_in_name, node_name))
        return topology

