#!/usr/bin/env python
import argparse
import json
from vat.simulation import get_world
from vat.envs.api import get_api, get_task_world
from vat.envs.bullet_interface import BulletInterface


def parse_args():
    parser = argparse.ArgumentParser(
        description='Bullet Wrapper Demo'
    )

    parser.add_argument('--physics', dest='physics',
                        help='The physics engine.',
                        default='bullet', type=str)

    parser.add_argument('--time_step', dest='time_step',
                        help='Time step for the simulation.',
                        default=0.001, type=float)

    parser.add_argument('--display', dest='display',
                        help='If render the simulation. [1]/[0] for yes/no.',
                        default=1, type=int)

    parser.add_argument('--data', dest='data_dir',
                        help='The data directory.',
                        default='assets/urdf/', type=str)

    parser.add_argument('--scene', dest='scene',
                        help='The scene xml file.',
                        default='tasks/scene/base.xml', type=str)

    parser.add_argument('--task', dest='task',
                        help='The task specification file',
                        # default='tasks/specs/stack/stack_2000.json', type=str)
                        default='tasks/specs/pick_place/pick_place_54.json', type=str)
    
    parser.add_argument('--save_trace', dest='save_trace',
                        help='Specify the save location of the trace',
                        default='trace.npy', type=str)

    args = parser.parse_args()

    return args


def main():
    # Process arguments
    args = parse_args()

    # The world configuration file
    world_path = args.scene

    # Process data directory
    print(('Data will be loaded from `{:s}`.'.format(args.data_dir)))

    # camera params
    camera_params = {
        'fov': 60,
        'aspect': 1,
        'near': 0.02,
        'far': 1,
        'view_matrix': [[0.0, -0.4, 1.4],
                        [0, 0.0, 0],
                        [1, 0, 0]]
    }

    # Build the simulation world
    world = get_world(
        args.physics,
        display=args.display,
        data_dir=args.data_dir,
        camera_params=camera_params,
        verbose=True)

    # load scene
    world.load(world_path)

    # Star the simulator
    print('Starting the simulation...')
    world.start(args.time_step)
    interface = BulletInterface(world)
    print('Done.')

    # load task specifications
    task_config = json.load(open(args.task))

    TaskWorld = get_task_world(task_config['name'], real=False)

    bw = TaskWorld(interface, task_config['scene'], random_task=False)

    # NTP full hierarchical API
    t = get_api('full')(bw, full_demo=True)
    bw.start_world()

    # iterate through tasks
    traces = []
    for i, task in enumerate(task_config['tasks']):
        bw.set_task(task)
        bw.start_task()
        done = False
        # try until complete a task
        while not done:
            out = t.model_program_trace()
            if out:
                if args.save_trace:
                    traces.append(out)
                done = True
                assert(bw.task_done)
            bw.reset_world()
            bw.start_task()
            print((task['id']))
            
    if args.save_trace:
        import numpy as np
        np.save(args.save_trace, traces, allow_pickle=True)

    print('Terminating the simulation...')
    world.close()
    print('Done.')

if __name__ == '__main__':
    main()
