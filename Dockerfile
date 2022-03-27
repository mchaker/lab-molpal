FROM nvidia/cuda:11.6.0-base-ubuntu20.04
# install basics 
RUN apt-get update
RUN apt-get install -y tmux wget curl git
# install adfr
RUN wget https://ccsb.scripps.edu/adfr/download/1028/
RUN mv 
# Install conda and the conda environment
RUN wget -q -P . https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash ./Miniconda3-latest-Linux-x86_64.sh -b
RUN rm Miniconda3-latest-Linux-x86_64.sh
RUN . "./conda/etc/profile.d/conda.sh"
ENV PATH="/conda/condabin:${PATH}"
RUN conda env create -f /environment.yml -n molpal && conda clean -a
# Add conda installation dir to PATH (instead of doing 'conda activate')
ENV PATH /opt/conda/envs/molpal/bin:$PATH
# Switch to the new environment:
SHELL ["conda", "run", "-n", "molpal", "/bin/bash", "-c"] 
COPY environment.yml /
# install dependency packages
RUN pip install optuna
RUN conda install -c tmap tmap
RUN conda install -c conda-forge rdkit
# install MAP4
RUN pip install git+https://github.com/reymond-group/map4@v1.0
# install pyscreener
RUN pip install pyscreener