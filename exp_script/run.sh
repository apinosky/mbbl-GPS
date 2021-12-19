# generate the config files and run the experiments

date_str=`date`
date_str=${date_str// /-}
date_str=${date_str//:/-}
env_name=$1
test_name=$2
# test_name="test1_buff"

batch_size=5000
num_frames=100000
# python python/gps/gps_main.py gym_cheetah_mdgps_example 2>&1 | tee output.log
# for env_name in gym_cheetah gym_fhopper; do
for rand_seed in $(seq 13 100 50); do
    # for rand_seed in 1234 2345 2314 1234 1235; do
    # generate the config files
    log_name=${date_str}_${env_name}_batch_${batch_size}_seed_${rand_seed}_mdgps
    exp_name="${env_name}/${test_name}/seed_${rand_seed}"
    mkdir -p experiments/${exp_name}
    cp -r experiments/gym_mdgps_example/hyperparams.py experiments/${exp_name}/.

    # modify the config files
    sed -i "s/ENV_NAME/${env_name}/g" experiments/${exp_name}/hyperparams.py
    sed -i "s/TEST_NAME/${test_name}/g" experiments/${exp_name}/hyperparams.py
    sed -i "s/RAND_SEED/${rand_seed}/g" experiments/${exp_name}/hyperparams.py
    sed -i "s/TIMESTEPS_PER_BATCH/${batch_size}/g" experiments/${exp_name}/hyperparams.py
    sed -i "s/TOTAL_TIMESTEPS/${num_frames}/g" experiments/${exp_name}/hyperparams.py

    # run the experiments
    python python/gps/gps_main.py ${exp_name} 2>&1 | tee ./log/${log_name}.log

done
# done
