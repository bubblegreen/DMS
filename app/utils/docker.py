import docker


def docker_client(url):
    return docker.DockerClient(base_url=url, version='auto', timeout=5)
