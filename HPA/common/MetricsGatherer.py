import statistics

import requests
import traceback

from .Configurations import Configurations


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


class PrometheusMetricGatherer:
    configurations: Configurations

    def __init__(self, configurations: Configurations):
        self.configurations = configurations

    # Prometheus fetching
    def __getResultsFromPrometheus(self, query):
        """
        Get the results of a query from Prometheus.
        Prometheus should be fetched from PROMETHEUS_SERVER
        :param query: Query to fetch results for from Prometheus
        :return: A response object send by the Prometheus server.
        """
        url = f"http://{self.configurations.PROMETHEUS_SERVER}/api/v1/query?query={query}"
        return requests.get(url)

    def __extract_per_operator_metrics(self, prometheusResponse):
        """
        Extract per-operator- metrics from the prometheusResponse
        :param prometheusResponse: Response received from Prometheus containing query results
        :return: A directory with per-operator values {operator: values}
        """
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            metrics_per_operator[operator["metric"]["task_name"]] = float(operator["value"][1])
        return metrics_per_operator

    def __extract_per_taskmanager_metrics(self, prometheusResponse):
        metrics = prometheusResponse.json()["data"]["result"]
        metrics_per_operator = {}
        for operator in metrics:
            taskmanager_id = operator["metric"]["tm_id"]
            metrics_per_operator[taskmanager_id] = float(operator["value"][1])
        return metrics_per_operator

    def getTaskmanagerJVMCPUUSAGE(self) -> {str, int}:
        """
        Get the CPU usage of every taskmanager
        :return:
        """
        TaskmanagerJVM_CPUUsage_query = f"avg_over_time(flink_taskmanager_Status_JVM_CPU_Load[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])"
        TaskmanagerJVM_CPUUsage_data = self.__getResultsFromPrometheus(TaskmanagerJVM_CPUUsage_query)
        TaskmanagerJVM_CPUUsage = self.__extract_per_taskmanager_metrics(TaskmanagerJVM_CPUUsage_data)
        return TaskmanagerJVM_CPUUsage

    # Parallelism gathering
    def getCurrentParallelismMetrics(self) -> {str, int}:
        """
        Get the current parallelisms of the individual operators
        :return: A directory with {operator, currentParallelism}
        """
        parallelism_query = f"count(sum_over_time(flink_taskmanager_job_task_operator_numRecordsIn" \
                            f"[{self.configurations.METRIC_AGGREGATION_PERIOD_SECONDS}s])) by (task_name)"
        parallelism_data = self.__getResultsFromPrometheus(parallelism_query)
        parallelism = self.__extract_per_operator_metrics(parallelism_data)
        return parallelism


class MetricsGatherer:
    configurations: Configurations
    jobmanagerMetricGatherer: JobManagerMetricGatherer
    prometheusMetricGatherer: PrometheusMetricGatherer
    v1 = None

    def __init__(self, configurations: Configurations):
        self.configurations = configurations
        self.jobmanagerMetricGatherer = JobManagerMetricGatherer(configurations)
        self.prometheusMetricGatherer = PrometheusMetricGatherer(configurations)


    def gatherReady_UnReadyTaskmanagerMapping(self):
        """
        Get a tuple of two mappings:
            operator -> list of ready operators (Longer alive than initial readyness delay and status = RUNNING)
            operator -> list of non-ready operators (other)
        :return: ({operator -> [taskmanager]}, {operator -> [taskmanager]}
        """
        operator_taskmanager_information = self.jobmanagerMetricGatherer.getOperatorHostInformation()
        operators = self.jobmanagerMetricGatherer.getOperators()

        operator_ready_taskmanagers = {}
        operator_nonready_taskmanagers = {}

        for operator in operators:
            if operator in operator_taskmanager_information:
                ready_taskmanagers = []
                nonready_taskmanagers = []
                print(operator_taskmanager_information[operator])
                for tm_id, status, duration_ms in operator_taskmanager_information[operator]:
                    taskmanager = tm_id.replace(".", "_").replace("-", "_")
                    if duration_ms / 1000 > self.configurations.HPA_AUTOSCALER_INITIAL_READINESS_DELAY_SECONDS:
                        if status == "RUNNING":
                            ready_taskmanagers.append(taskmanager)
                            continue
                    nonready_taskmanagers.append(taskmanager)
                    continue
                operator_ready_taskmanagers[operator] = ready_taskmanagers
                operator_nonready_taskmanagers[operator] = nonready_taskmanagers
            else:
                print(
                    f"Error: did not find operator '{operator} in operator_taskmanager_information "
                    f"'{operator_taskmanager_information}'")
                operator_ready_taskmanagers[operator] = []
                operator_nonready_taskmanagers[operator] = []
        return operator_ready_taskmanagers, operator_nonready_taskmanagers


    def gatherCPUUsageOfTaskmanagers(self, taskmanagers: [str], taskmanager_CPUUsages=None) -> [float]:
        """
        Given a list of taskmanagers. Fetch their CPU_usage and add them to a list.
        If CPU_usage is unavailable, add taskmanager_unavailable_value. Add nothing if taskmanager_unavailable_value is None.
        :param taskmanagers: Taskmanagers to fetch CPU usage from
        :param taskmanager_CPUUsages: Optional variable containing all taskmanagers CPU usages
        :return: List of CPU_values belonging to the taskmanagers
        """
        if not taskmanager_CPUUsages:
            taskmanager_CPUUsages = self.prometheusMetricGatherer.getTaskmanagerJVMCPUUSAGE()
        cpu_usages = []
        for taskmanager in taskmanagers:
            if taskmanager in taskmanager_CPUUsages:
                cpu_usages.append(taskmanager_CPUUsages[taskmanager])
            else:
                print(f"Error: taskmanager '{taskmanager}' not found in cpu_usages '{cpu_usages}'")
        return cpu_usages


    # Metrics gathering
    def gatherUtilizationMetrics(self) -> {str, int}:
        """
        1 - (avg(flink_taskmanager_job_task_idleTimeMsPerSecond) by (<<.GroupBy>>) / 1000)
        :return:
        """
        print("todo")
        return None

    def gatherRelativeLagChangeMetrics(self) -> {str, int}:
        """
        ((
             sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
             by ( <<.GroupBy >>) - 50000) / (abs(sum(
            flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
                                             by ( <<.GroupBy >>) - 50000)))*(1 + deriv(
            sum(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_lag_max * flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_assigned_partitions)
                                                                             by ( <<.GroupBy >>)[1
        m: 2
        s]) / sum(
            avg_over_time(flink_taskmanager_job_task_operator_KafkaSourceReader_KafkaConsumer_records_consumed_rate[1
        m])) by( <<.GroupBy >>))
        """
        return None

    def __getCurrentNumberOfTaskmanagersMetrics(self) -> int:
        if self.v1:
            try:
                number_of_taskmanagers = -1
                ret = self.v1.list_namespaced_deployment(watch=False, namespace="default", pretty=True,
                                                         field_selector="metadata.name=flink-taskmanager")
                for i in ret.items:
                    number_of_taskmanagers = int(i.spec.replicas)
                return number_of_taskmanagers
            except:
                traceback.print_exc()
                return -1
        else:
            print("Error fetching current number of taskmanagers: v1 is not defined.")

    def fetchCurrentOperatorParallelismInformation(self, knownOperators: [str] = None) -> {str, int}:
        """
        Get per-operator parallelism
        If Flink reactive is used:
            Fetch current amount of taskmanagers
            Return a direcotry with all operators having this parallelism
            v1 is required for this scenario
        If Flink reactive is not used:
            Fetch taskmanagers using the getCurrentParallelismMetrics() function.
            v1 is not required for this scenario
        :param knownOperators:
        :return: Directory with operators as key and parallelisms as values
        """
        if self.configurations.USE_FLINK_REACTIVE:
            currentTaskmanagers = self.__getCurrentNumberOfTaskmanagersMetrics()
            if currentTaskmanagers < 0:
                print(f"Error: no valid amount of taskmanagers found: {currentTaskmanagers}")
                return {}
            operatorParallelismInformation = {}
            for operator in knownOperators:
                operatorParallelismInformation[operator] = currentTaskmanagers
            return operatorParallelismInformation
        else:
            return self.jobmanagerMetricGatherer.getOperatorParallelism()
