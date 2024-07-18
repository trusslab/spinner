#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>
#include <sys/sysinfo.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <sys/resource.h>
#include <signal.h>
#include <time.h>

int main(void)
{
	struct perf_event_attr attr = {
		.type = PERF_TYPE_RAW,
		.size = sizeof(attr),
		.config = INTEL_ARCH_CPU_CYCLES,
		.freq = 1
	};

	syscall(SYS_perf_event_open, &attr, 0, -1, -1, 0);

	if (PERF_RECORD_SWITCH != 14 || PERF_RECORD_MISC_SWITCH_OUT != (1 << 13))
		return -1;

	return 0;
}
