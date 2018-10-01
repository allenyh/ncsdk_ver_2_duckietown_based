FROM duckietown/rpi-duckiebot-base

COPY qemu-arm-static /usr/bin/qemu-arm-static 

RUN mkdir /home/software/ncsdk-2.05.00.02
COPY ncsdk-2.05.00.02 /home/software/ncsdk-2.05.00.02
WORKDIR /home/software/ncsdk-2.05.00.02
RUN make install
