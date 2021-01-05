FROM python:3.7-slim-buster AS build
WORKDIR /usr/src/app
COPY requirements.txt main.py ./
RUN apt update
RUN apt install -y cmake pkg-config libssl-dev git build-essential clang libclang-dev curl
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN echo $PATH
RUN rustup install nightly
RUN rustup target add wasm32-unknown-unknown --toolchain nightly
RUN rustup default nightly
RUN pip install --upgrade pip --upgrade setuptools 
RUN pip install -r requirements.txt
FROM gcr.io/distroless/python3-debian10:nonroot
COPY --from=build --chown=nonroot:nonroot /usr/src/app/main.py /
COPY --from=build --chown=nonroot:nonroot /usr/local/lib/python3.7/site-packages /usr/local/lib/python3.7/site-packages
CMD ["/main.py"]