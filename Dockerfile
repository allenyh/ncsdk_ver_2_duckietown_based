FROM duckietown/rpi-duckiebot-base

#COPY qemu-arm-static /usr/bin/qemu-arm-static 

RUN [ "cross-build-start" ]

RUN mkdir -p /home/software/ncsdk
COPY ncsdk-2.05.00.02 /home/software/ncsdk
WORKDIR /home/software/ncsdk
RUN make install

RUN [ "cross-build-end" ]