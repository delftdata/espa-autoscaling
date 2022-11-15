import traceback

from .Configurations import Configurations


class ScaleManager:

    v1 = None
    configurations: Configurations
    desiredParallelisms: {str, int}

    def __init__(self, configurations: Configurations):
        self.configurations = configurations
        self.desiredParallelisms = {}


    def scaleOperator(self, operator: str, desiredParallelism):
        """
        TODO: implement operator-based scaling
        Perform a scaling operator for the operator.
        The desiredParallelism is set between [MIN_TASKMANAGERS, MAX_PARALLELISM]
        :param operator: Operator to scale
        :param desiredParallelism: Operator to scale to.
        :return: None
        """
        desiredParallelism = max(self.configurations.MIN_PARALLELISM, desiredParallelism)
        desiredParallelism = min(self.configurations.MAX_PARALLELISM, desiredParallelism)
        self.desiredParallelisms[operator] = desiredParallelism
        print(f"TODO: Scale operator '{operator}' to parallelism '{desiredParallelism}'. ")


    def adaptFlinkReactiveTaskmanagers(self, new_number_of_taskmanagers):
        if not self.configurations.USE_FLINK_REACTIVE:
            print(f"Error: trying to scale taskmanagers with disabled Flink Reactive. Returning.")
            return

        try:
            print(f"Scaling total amount of taskmanagers to {new_number_of_taskmanagers}")
            body = {"spec": {"replicas": new_number_of_taskmanagers}}
            api_response = self.v1.patch_namespaced_deployment_scale(
                name="flink-taskmanager", namespace="default", body=body,
                pretty=True)
        except:
            traceback.print_exc()
