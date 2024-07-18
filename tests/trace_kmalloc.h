#ifndef __TRACE_KMALLOC_H
#define __TRACE_KMALLOC_H

#define TASK_COMM_LEN 16

#define MAX_STACK_DEPTH 128
#define __NEW_UTS_LEN 64
//#include "vmlinux.h"

typedef __u64 stack_trace_t[MAX_STACK_DEPTH];


struct new_utsname1 {
	char *sysname[__NEW_UTS_LEN + 1];
	char *nodename[__NEW_UTS_LEN + 1];
	char *release[__NEW_UTS_LEN + 1];
	char *version[__NEW_UTS_LEN + 1];
	char *machine[__NEW_UTS_LEN + 1];
	char *domainname[__NEW_UTS_LEN + 1];
};

struct pid_namespace1 {
	unsigned int idr_base;
	unsigned int idr_next;
	unsigned int pid_allocated;
	unsigned int level;
	int reboot;
};

struct mnt_namespace1 {
	__u64 seq;
	__u64 event;
	unsigned int nr_mounts;
	unsigned int pending_mounts;
};

struct ipc_namespace1 {
	int		sem_ctls[4];
	int		used_sems;
	unsigned int	msg_ctlmax;
	unsigned int	msg_ctlmnb;
	unsigned int	msg_ctlmni;
	size_t		shm_ctlmax;
	size_t		shm_ctlall;
	unsigned long	shm_tot;
	int		shm_ctlmni;
	int		shm_rmid_forced;
	unsigned int    mq_queues_count;
	unsigned int    mq_queues_max;   /* initialized to DFLT_QUEUESMAX */
	unsigned int    mq_msg_max;      /* initialized to DFLT_MSGMAX */
	unsigned int    mq_msgsize_max;  /* initialized to DFLT_MSGSIZEMAX */
	unsigned int    mq_msg_default;
	unsigned int    mq_msgsize_default;
};

struct kmalloc_details {
	unsigned long call_site;
	const void *ptr;
	size_t bytes_req;
	size_t bytes_alloc;
	unsigned long gfp_flags;
	int node;
};

struct trace_t {
        __u32 pid;
        __u32 tgid;
        __u32 uid;
        __u32 gid;
	
	char *comm[TASK_COMM_LEN];
	struct nsproxy *ns;

	struct kmalloc_details kd;
	//uts namespace
	struct new_utsname1 utsname;

	//pid namespace
	struct pid_namespace1 pns;
	
	struct mnt_namespace1 mns;
		
	struct ipc_namespace1 ins;

	__s32 kstack_sz;
	__s32 ustack_sz;
	stack_trace_t kstack;
	stack_trace_t ustack;
};



#endif
