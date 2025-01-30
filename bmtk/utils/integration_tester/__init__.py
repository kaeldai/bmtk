from .sonata_files import ReportFile, SpikesFile, ECPFile, ConfigJSON
from .sonata_files import NodesFile, EdgesFile

def get_return_code(results):
    all_results = []
    for test_result in results:
        if isinstance(test_result, tuple):
            all_results += test_result[0]
        elif isinstance(test_result, list):
            all_results += test_result
        else:
            all_results.append(test_result)

    return 0 if all(results) else 1
