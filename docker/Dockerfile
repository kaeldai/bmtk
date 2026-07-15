# FROM continuumio/miniconda3:4.11.0
FROM continuumio/miniconda3:latest
LABEL maintainer="Kael Dai <kaeld@alleninstitute.org>"

RUN apt-get -y update && apt-get install -y automake \
                                            build-essential \
                                            git \
                                            libgsl-dev 


COPY environment.py3.11.yml environment.yml
RUN conda env create -f environment.yml

# Make sure all further commands will run using bmtk environment
SHELL ["conda", "run", "-n", "bmtk", "/bin/bash", "-c"]

ENV BUILD_DIR=/home/build
ENV HOME_DIR=/home/shared
ENV WORK_DIR=${HOME_DIR}/workspace
ENV GIT_REPO=https://github.com/AllenInstitute/bmtk.git
ENV GIT_BRANCH=update/workshop-2026
ARG WORKSHOP_REPO=https://github.com/AllenInstitute/bmtk-workshop.git
ARG WORKSHOP_BRANCH=updates/2026

RUN mkdir -p ${BUILD_DIR}
RUN mkdir -p ${HOME_DIR}
RUN mkdir -p ${WORK_DIR}


#### Install the bmtk
RUN cd ${BUILD_DIR} \
    && git clone --branch ${GIT_BRANCH} ${GIT_REPO} \
    && cd bmtk \
    && pip install -e .


#### Setup the examples and tutorials
RUN cd ${BUILD_DIR}/bmtk; \
    cp -R examples ${HOME_DIR};
    # cp -R docs/tutorial ${HOME_DIR}


# Pre-compile mechanisms for BioNet examples
RUN cd ${HOME_DIR}/examples/bio_components/mechanisms \
    && nrnivmodl modfiles/


## Install Workshop tutorials
RUN cd ${HOME_DIR}; \
    git clone --branch ${WORKSHOP_BRANCH} ${WORKSHOP_REPO}


RUN cd ${HOME_DIR}/bmtk-workshop/Ch2_single_cell/components/mechanisms \
    && nrnivmodl modfiles/


RUN cd ${HOME_DIR}/bmtk-workshop/Ch3_multicells/components/mechanisms \
    && nrnivmodl modfiles/


#### Create an entry point for running the image
COPY entry_script.sh ${BUILD_DIR}
RUN chmod +x ${BUILD_DIR}/entry_script.sh
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "bmtk", "/home/build/entry_script.sh"]
# ENTRYPOINT ["/home/build/entry_script.sh"]
