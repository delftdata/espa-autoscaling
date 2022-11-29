import sys
from a_processing import process_data

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if len(arguments) >= 4:
        prometheus_ip = arguments[0]
        query = arguments[1]
        autoscaler = arguments[2]
        metric = arguments[3]
        load_pattern = arguments[4] if len(arguments) >= 5 else "cosine-60"
        print(f"Processing data from {prometheus_ip} of {query} with {autoscaler}-{metric} on {load_pattern} ")
        process_data(prometheus_ip, query, autoscaler, load_pattern, metric)
    else:
        print(f"Unsufficient parameters. Expected: [prometheus_ip, query, autoscaler, metric, [load_pattern]]. Received: {arguments}")
