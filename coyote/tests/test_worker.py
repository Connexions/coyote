from . import test_functional

def echo_request(build_request, settings={}):
    # send info about the build request back to the test case
    artifacts = [build_request.get_package(), 
                 build_request.get_version(), 
                 build_request.get_job_id()]
    test_functional.artifacts.extend(artifacts)
    return []
