obj-m += nmi_example.o

#KDIR := /lib/modules/$(shell uname -r)/build
KDIR := /lib/modules/6.8.2-s2e/build

# Default target
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Clean target
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
