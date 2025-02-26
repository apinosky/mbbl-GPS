""" @brief: The template hyperparams for the gym_envrionments
"""
from __future__ import division
from datetime import datetime
import os.path
import numpy as np
from gps import __file__ as gps_filepath
from gps.agent.mjc.gym_agent import AgentMuJoCo
from gps.algorithm.algorithm_mdgps import AlgorithmMDGPS
from gps.algorithm.cost.gym_cost import gym_cost
from gps.algorithm.dynamics.dynamics_lr_prior import DynamicsLRPrior
from gps.algorithm.dynamics.dynamics_prior_gmm import DynamicsPriorGMM
from gps.algorithm.traj_opt.traj_opt_lqr_python import TrajOptLQRPython
from gps.algorithm.policy_opt.tf_model_example import tf_network
from gps.algorithm.policy_opt.policy_opt_tf import PolicyOptTf
from gps.algorithm.policy.lin_gauss_init import init_lqr
from gps.algorithm.policy.policy_prior_gmm import PolicyPriorGMM
from gps.gui.config import generate_experiment_info
from gps.agent.gym_env_util import get_x0
from mbbl.env.env_register import get_env_info

env_name = 'gym_cheetah'  # 'gym_cheetah'
test_name = 'test1'
rand_seed = 613  # 1234
timesteps_per_batch = 5000
env_info = get_env_info(env_name)

total_timestep = 100000 # 1000000
iterations = int(total_timestep / timesteps_per_batch)  # 2000
num_samples = 5 # int(timesteps_per_batch / env_info['max_length'])  # 5
assert timesteps_per_batch % env_info['max_length'] == 0

SENSOR_DIMS = {
    "observation": env_info['ob_size'],
    'action': env_info['action_size'],
}

# BASE_DIR = '/'.join(str.split(gps_filepath, '/')[:-3])
# exp_dir = BASE_DIR + '/../experiments/' + env_name + '_mdgps_example/'
exp_dir = 'experiments/' + env_name + '/' + test_name + '/seed_' + str(rand_seed) + '/'

common = {
    'experiment_name': env_name + '_experiments' + '_' +
    datetime.strftime(datetime.now(), '%m-%d-%y_%H-%M'),
    'experiment_dir': exp_dir,
    'data_files_dir': exp_dir + 'data_files/',
    'target_filename': exp_dir + 'target.npz',
    'log_filename': exp_dir + 'log.txt',
    'conditions': 1,
}

if not os.path.exists(common['data_files_dir']):
    os.makedirs(common['data_files_dir'])

agent = {
    'type': AgentMuJoCo,
    # 'filename': './mjc_models/pr2_arm3d.xml',
    'x0': get_x0(env_name,rand_seed),
    'dt': 0.01 if env_name=='gym_cheetah' else 0.002, # hopper = 0.002, half cheetah = 0.01
    'substeps': 5  if env_name=='gym_cheetah' else 4, # hopper = 4, half cheetah = 5
    'conditions': common['conditions'],
    'sensor_dims': SENSOR_DIMS,
    'state_include': ['observation'],
    'obs_include': ['observation'],
    'camera_pos': np.array([0., 0., 2., 0., 0.2, 0.5]),

    # the real config files
    'T': env_info['max_length'],
    'env_name': env_name,
}

algorithm = {
    'type': AlgorithmMDGPS,
    'conditions': common['conditions'],
    'iterations': iterations,
    'kl_step': 1.0,
    'min_step_mult': 0.5,
    'max_step_mult': 3.0,
    'policy_sample_mode': 'replace',
}

algorithm['init_traj_distr'] = {
    'type': init_lqr,
    'init_gains':  np.ones(SENSOR_DIMS['action']), #1.0 / PR2_GAINS,
    'init_acc': np.zeros(SENSOR_DIMS['action']),
    'init_var': 1.0,
    'stiffness': 1.0,
    'stiffness_vel': 0.5,
    'final_weight': 50.0,
    'dt': agent['dt'],
    'T': agent['T'],
}

algorithm['cost'] = {
    'type': gym_cost,
    'env_name': env_name
}

algorithm['dynamics'] = {
    'type': DynamicsLRPrior,
    'regularization': 1e-6,
    'prior': {
        'type': DynamicsPriorGMM,
        'max_clusters': 20,
        'min_samples_per_cluster': 40,
        'max_samples': 20,
        'max_iterations': 100 # 100
    },
}

algorithm['traj_opt'] = {
    'type': TrajOptLQRPython,
}

algorithm['policy_opt'] = {
    'type': PolicyOptTf,
    'network_params': {
        'obs_include': ['observation'],
        'sensor_dims': SENSOR_DIMS,
        'n_layers' : 1,
        'hidden_dim' : 128
    },
    'weights_file_prefix': exp_dir + 'policy',
    'iterations': 3000,
    'network_model': tf_network,
    'random_seed': rand_seed
}

algorithm['policy_prior'] = {
    'type': PolicyPriorGMM,
    'max_clusters': 20,
    'min_samples_per_cluster': 40,
    'max_samples': 20,
    'max_iterations': 100 # 100
}

config = {
    'gui_on': False,
    'iterations': algorithm['iterations'],
    'total_timestep': total_timestep,
    'num_samples': num_samples,
    'verbose_trials': 1,
    'verbose_policy_trials': 1,
    'common': common,
    'agent': agent,
    'algorithm': algorithm,
    'random_seed': rand_seed
}

common['info'] = generate_experiment_info(config)
