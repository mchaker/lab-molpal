FROM nvidia/cuda:11.6.0-base-ubuntu20.04
# install basics 
RUN apt-get update
RUN apt-get install -y tmux wget curl git
# install cudatoolkit

# install adfr
RUN wget https://ccsb.scripps.edu/adfr/download/1028/
# Install the conda environment
COPY environment.yml /
RUN conda env create -f /environment.yml -n molpal && conda clean -a
# Add conda installation dir to PATH (instead of doing 'conda activate')
ENV PATH /opt/conda/envs/molpal/bin:$PATH
# install dependency packages
RUN pip install optuna
RUN conda install -c tmap tmap
RUN conda install -c conda-forge rdkit
# install MAP4
RUN pip install git+https://github.com/reymond-group/map4@v1.0
# install pyscreener
RUN pip install pyscreener