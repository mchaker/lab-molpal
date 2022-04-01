# Running MolPAL in a Docker container with GPUs

NOTE: My setup:

* 128 GB RAM (important for the `--shm-size` flag later in these notes)
* 48-thread EPYC 7402 CPU
* 250 GB SSD
* 7x NVIDIA Tesla GPUs

## On the host machine:

1. Install the OS of your choice, in my case I used Ubuntu 20.04 (LTS).
1. Install Docker. On Ubuntu 20.04, the `apt` package is named `docker.io` .
1. Install the NVIDIA drivers (server edition). I installed version 510.
1. Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit).
    * Remember to run `sudo systemctl restart docker` afterwards!
1. Test your installation: run the `nvidia-smi` command in a test docker container:
    * `sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi`
1. Run the LabDAO `molpal` container interactively with the `--gpus` and `--shm-size` flags. The `--shm-size` flag sets the available shared memory size so that you can have ample `shm` space in the container (`molpal` complains if the shared memory/shm size is too small):
    * `docker run -it -p 8265:8265 --gpus all --name labdao-molpal --shm-size=48gb ghcr.io/labdao/lab-molpal:main`
1. Inside that `molpal` container, run the following commands:
    * ```
      source /root/miniconda3/etc/profile.d/conda.sh
      conda activate molpal

      python scripts/fingerprints.py --libraries libraries/Enamine50k.csv.gz --fingerprint pair --length 2048 --radius 2 --name fps_enamine50k
      ```
1. If you want, try another `molpal` sample:
    * ```
      mkdir /root/output-dir-test/

      python run.py --write-intermediate --write-final --retrain-from-scratch --library libraries/Enamine50k.csv.gz --metric greedy --init-size 0.01 --batch-sizes 0.01 --model rf --fingerprint pair --length 2048 --radius 2 --objective lookup --objective-config examples/objective/Enamine50k_lookup.ini --top-k 0.01 --window-size 10 --delta 0.01 --max-iters 5 --output-dir /root/output-dir-test/
      ```
    * ```
      python run.py --config examples/config/Enamine50k_retrain.ini --metric greedy --init-size 0.01 --batch-sizes 0.01 --model rf
      ```
