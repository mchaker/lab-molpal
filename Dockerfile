FROM nvidia/cuda:11.6.0-base-ubuntu20.04
# install cudatoolkit

# install adfr
RUN wget https://ccsb.scripps.edu/adfr/download/1028/
# Install the conda environment
COPY environment.yml /
RUN conda env create -f /environment.yml -n molpal && conda clean -a

# Add conda installation dir to PATH (instead of doing 'conda activate')
ENV PATH /opt/conda/envs/molpal/bin:$PATH
# install packages
RUN pip install pyscreener
