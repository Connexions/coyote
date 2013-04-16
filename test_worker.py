def echo_request(build_request, settings={}):
    print(str(build_request))
    print(str(settings))
    print("Building {0}".format(build_request.get_package()))
    return []
