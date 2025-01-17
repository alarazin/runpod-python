"""
RunPod | API Wrapper | CTL Commands
"""
# pylint: disable=too-many-arguments,too-many-locals

from typing import Optional

from .queries import gpus
from .queries import pods as pod_queries
from .graphql import run_graphql_query
from .mutations import pods as pod_mutations


def get_gpus() -> dict:
    '''
    Get all GPU types
    '''
    raw_response = run_graphql_query(gpus.QUERY_GPU_TYPES)
    cleaned_return = raw_response["data"]["gpuTypes"]
    return cleaned_return


def get_gpu(gpu_id : str, gpu_quantity : int = 1):
    '''
    Get a specific GPU type

    :param gpu_id: the id of the gpu
    :param gpu_quantity: how many of the gpu should be returned
    '''
    raw_response = run_graphql_query(gpus.generate_gpu_query(gpu_id, gpu_quantity))

    cleaned_return = raw_response["data"]["gpuTypes"]

    if len(cleaned_return) < 1:
        raise ValueError("No GPU found with the specified ID, "
                         "run runpod.get_gpus() to get a list of all GPUs")

    return cleaned_return[0]

def get_pods() -> dict:
    '''
    Get all pods
    '''
    raw_return = run_graphql_query(pod_queries.QUERY_POD)
    cleaned_return = raw_return["data"]["myself"]["pods"]
    return cleaned_return

def get_pod(pod_id : str):
    '''
    Get a specific pod

    :param pod_id: the id of the pod
    '''
    raw_response = run_graphql_query(pod_queries.generate_pod_query(pod_id))
    return raw_response["data"]["pod"]

def create_pod(
        name:str, image_name:str, gpu_type_id:str,
        cloud_type:str="ALL", support_public_ip:bool=False,
        data_center_id : Optional[str]=None, country_code:Optional[str]=None,
        gpu_count:int=1, volume_in_gb:int=0, container_disk_in_gb:int=5,
        min_vcpu_count:int=1, min_memory_in_gb:int=1, docker_args:str="",
        ports:Optional[str]=None, volume_mount_path:str="/workspace", 
        network_volume_id:Optional[str]=None, template_id:Optional[str]=None, 
        env:Optional[dict]=None
    ) -> dict:
    '''
    Create a pod

    :param name: the name of the pod
    :param image_name: the name of the docker image to be used by the pod
    :param gpu_type_id: the gpu type wanted by the pod (retrievable by get_gpus)
    :param cloud_type: if secure cloud, community cloud or all is wanted
    :param data_center_id: the id of the data center
    :param country_code: the code for country to start the pod in
    :param gpu_count: how many gpus should be attached to the pod
    :param volume_in_gb: how big should the pod volume be
    :param ports: the ports to open in the pod, example format - "8888/http,666/tcp"
    :param volume_mount_path: where to mount the volume?
    :param env: the environment variables to inject into the pod,
                for example {EXAMPLE_VAR:"example_value", EXAMPLE_VAR2:"example_value 2"}, will
                inject EXAMPLE_VAR and EXAMPLE_VAR2 into the pod with the mentioned values

    :example:

    >>> pod_id = runpod.create_pod("test", "runpod/stack", "NVIDIA GeForce RTX 3070")
    '''
    # Input Validation
    get_gpu(gpu_type_id) # Check if GPU exists, will raise ValueError if not.
    if cloud_type not in ["ALL", "COMMUNITY", "SECURE"]:
        raise ValueError("cloud_type must be one of ALL, COMMUNITY or SECURE")

    raw_response = run_graphql_query(
        pod_mutations.generate_pod_deployment_mutation(
            name, image_name, gpu_type_id,
            cloud_type, support_public_ip,
            data_center_id, country_code, gpu_count,
            volume_in_gb, container_disk_in_gb, min_vcpu_count, min_memory_in_gb, docker_args,
            ports, volume_mount_path, network_volume_id, template_id, env)
    )

    cleaned_response = raw_response["data"]["podFindAndDeployOnDemand"]
    return cleaned_response


def stop_pod(pod_id: str):
    '''
    Stop a pod

    :param pod_id: the id of the pod

    :example:

    >>> pod_id = runpod.create_pod("test", "runpod/stack", "NVIDIA GeForce RTX 3070")
    >>> runpod.stop_pod(pod_id)
    '''
    raw_response = run_graphql_query(
        pod_mutations.generate_pod_stop_mutation(pod_id)
    )

    cleaned_response = raw_response["data"]["podStop"]
    return cleaned_response


def resume_pod(pod_id: str, gpu_count: int):
    '''
    Resume a pod

    :param pod_id: the id of the pod
    :param gpu_count: the number of GPUs to attach to the pod

    :example:

    >>> pod_id = runpod.create_pod("test", "runpod/stack", "NVIDIA GeForce RTX 3070")
    >>> runpod.stop_pod(pod_id)
    >>> runpod.resume_pod(pod_id)
    '''
    raw_response = run_graphql_query(
        pod_mutations.generate_pod_resume_mutation(pod_id, gpu_count)
    )

    cleaned_response = raw_response["data"]["podResume"]
    return cleaned_response


def terminate_pod(pod_id: str):
    '''
    Terminate a pod

    :param pod_id: the id of the pod

    :example:

    >>> pod_id = runpod.create_pod("test", "runpod/stack", "NVIDIA GeForce RTX 3070")
    >>> runpod.terminate_pod(pod_id)
    '''
    run_graphql_query(
        pod_mutations.generate_pod_terminate_mutation(pod_id)
    )
