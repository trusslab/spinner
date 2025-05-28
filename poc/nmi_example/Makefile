# Use fallback if KERNEL_VERSION not set
ifeq ($(strip $(KERNEL_VERSION)),)
    KERNEL_VERSION := $(DEFAULT_KERNEL_VERSION)
endif

obj-m += nmi_example.o

#KDIR := /lib/modules/$(shell uname -r)/build
KDIR := /lib/modules/$(KERNEL_VERSION)/build

# Default target
all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

# Clean target
clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
