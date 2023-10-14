FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# We need to set the host to 0.0.0.0 to allow outside access
ENV HOST 0.0.0.0

RUN apt-get update && apt-get upgrade -y \
  && apt-get install -y git build-essential \
  python3 python3-pip gcc wget \
  ocl-icd-opencl-dev opencl-headers clinfo \
  libclblast-dev libopenblas-dev \
  && mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

# setting build related env vars
ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade -r /app/requirements.txt
RUN pip install accelerate transformers>=4.32.0 optimum>=1.12.0
RUN pip3 install auto-gptq --extra-index-url https://huggingface.github.io/autogptq-index/whl/cu118/

COPY main.py /app

EXPOSE 8080

CMD ["python3", "main.py"]