from common import MetricsGatherer


class HPAMetricsGathererCPU(MetricsGatherer):

    def gatherReady_UnReadyTaskmanagerMapping(self):
        """
        Get a tuple of two mappings:
            operator -> list of ready operators (status = RUNNING)
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
                for tm_id, status, duration_ms in operator_taskmanager_information[operator]:
                    taskmanager = tm_id.replace(".", "_").replace("-", "_")
                    if status == "RUNNING":
                        ready_taskmanagers.append(taskmanager)
                    else:
                        nonready_taskmanagers.append(taskmanager)
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
