import os, sys
import argparse

from bmtk.simulator import pointnet


def run(config_file):
    configure = pointnet.Config.from_json(config_file)
    configure.build_env()

    network = pointnet.PointNetwork.from_config(configure)
    sim = pointnet.PointSimulator.from_config(configure, network)
    sim.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', nargs='?', type=str, default='config.simulation.json')
    args, unknown = parser.parse_known_args()

    run(config_file=args.config_file)
