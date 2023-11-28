FROM centos:7

#----------------------------
# Install common dependencies
#----------------------------
RUN yum install -y -q bzip2 ca-certificates curl unzip bc libgomp libXmu libXt tcsh perl gcc mono-mcs\
    && yum clean packages \
    && rm -rf /var/cache/yum/* /tmp/* /var/tmp/*

#--------------------------
# Install FreeSurfer v6.0.0
#--------------------------
 
RUN echo "Downloading and installing Freesurfer 6.0.0..." \
    && curl -sSL --retry 5 https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz \
    | tar xz -C /opt \
    --exclude='freesurfer/trctrain' \
    --exclude='freesurfer/subjects/fsaverage_sym' \
    --exclude='freesurfer/subjects/fsaverage3' \
    --exclude='freesurfer/subjects/fsaverage4' \
    --exclude='freesurfer/subjects/fsaverage5' \
    --exclude='freesurfer/subjects/fsaverage6' \
    --exclude='freesurfer/subjects/cvs_avg35' \
    --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
    --exclude='freesurfer/subjects/bert' \
    --exclude='freesurfer/subjects/V1_average' \
    --exclude='freesurfer/average/mult-comp-cor' \
    --exclude='freesurfer/lib/cuda' \
    --exclude='freesurfer/lib/qt'

#--------------------------
# Install MCR
#--------------------------
RUN echo "Install MCR v80..." \
    && curl -sSL -o MCR_R2012b_glnxa64_installer.zip https://ssd.mathworks.com/supportfiles/MCR_Runtime/R2012b/MCR_R2012b_glnxa64_installer.zip \
    && unzip -d MCR_R2012b MCR_R2012b_glnxa64_installer.zip \
    && rm -f MCR_R2012b*.zip \
    && cd MCR_R2012b \
    && echo "destinationFolder=/opt/freesurfer" > installer_input.txt \
    && echo "agreeToLicense=yes" >> installer_input.txt \
    && echo "mode=silent" >> installer_input.txt \
    && ./install -inputFile installer_input.txt \
    && cd .. && rm -rf MCR_R2012b \
    && mv /opt/freesurfer/v80 /opt/freesurfer/MCRv80 \
    && rm -rf

#-------------------------
# ENV setup
#-------------------------
ENV FS_OVERRIDE=0 \
    OS=Linux \
    FSF_OUTPUT_FORMAT=nii.gz \
    FIX_VERTEX_AREA= \
    FREESURFER_HOME=/opt/freesurfer \
    MNI_DIR=/opt/freesurfer/mni \
    SUBJECTS_DIR=/subjects \
    PERL5LIB=/opt/freesurfer/mni/share/perl5 \
    MNI_PERL5LIB=/opt/freesurfer/mni/share/perl5 \
    MINC_BIN_DIR=/opt/freesurfer/mni/bin \
    MINC_LIB_DIR=/opt/freesurfer/mni/lib \
    MNI_DATAPATH=/opt/freesurfer/mni/data \
    STARTUP="/opt/startup.sh" \
    PATH=/opt/miniconda/envs/default/bin:/opt/freesurfer/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:$PATH


#-------------------------
# COPY pipeline src
#-------------------------
COPY ./src /opt/

#-------------------------------------------------
# Install Miniconda, and set up Python environment
#-------------------------------------------------
RUN echo "Downloading Miniconda installer ..." \
    && curl -sSL -o miniconda.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh \
    && bash miniconda.sh -b -p /opt/miniconda \
    && rm -f miniconda.sh \
    && /opt/miniconda/bin/conda config --add channels conda-forge \
    && /opt/miniconda/bin/conda create -y -q -n default python=2.7 traits \
    && /opt/miniconda/bin/conda clean -y --all \
    && pip install -U -q --no-cache-dir pip \
    && cd /opt \
    && pip install -r requirements.txt \
    && pip install -e .


#-------------------------------------------------
# entry point setup script
#-------------------------------------------------

RUN echo "Installing RS freesurfer pipeline..." \
    && if [ ! -f "$STARTUP" ]; then \
       echo '#!/usr/bin/env bash' >> $STARTUP; \
       echo '. /docker_environment' >> $STARTUP; \
       echo '"$@"' >> $STARTUP; \
       fi \
    && chmod 755 $STARTUP


ENTRYPOINT ["/opt/startup.sh"]
