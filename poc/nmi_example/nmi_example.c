#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/nmi.h>
#include <linux/irq.h>
#include <linux/delay.h>
#include <linux/cpumask.h>
#include <linux/smp.h>
#include <linux/debugfs.h>
#include <linux/uaccess.h>

#include <asm/apic.h>
#include <asm/nmi.h>

#define NMI_NAME "example_nmi_handler"
#define TRIGGER_FILE "trigger_nmi"

static struct dentry *nmi_debugfs_dir;
static struct dentry *nmi_debugfs_trigger;

//static DECLARE_BITMAP(nmi_ipi_mask, NR_CPUS) __initdata;

void my_nmi_print_function(void);

void my_nmi_print_function() {
	pr_info("nmi handler");
}

static int my_nmi_handler(unsigned int val, struct pt_regs *regs)
{
    my_nmi_print_function();
    return NMI_HANDLED; // Indicate the NMI was handled
}

static ssize_t nmi_debugfs_write(struct file *file, const char __user *buf,
                                 size_t count, loff_t *ppos)
{
    cpumask_t mask;
    unsigned long timeout;

    // Set the mask to all online CPUs
    cpumask_copy(&mask, cpu_online_mask);

    pr_info("Triggering NMI on CPUs: %*pbl\n", cpumask_pr_args(&mask));

    // Send NMI to all CPUs
    __apic_send_IPI_mask(&mask, NMI_VECTOR);

    // Optional: Wait for completion or timeout
    timeout = USEC_PER_SEC; // 1 second timeout
    while (!cpumask_empty(&mask) && --timeout)
        udelay(1);

    return count;
}

static const struct file_operations nmi_debugfs_fops = {
    .write = nmi_debugfs_write,
};

static int __init nmi_example_init(void)
{
    int ret;

    pr_info("Loading NMI example module...\n");

    // Register the NMI handler
    ret = register_nmi_handler(NMI_LOCAL, my_nmi_handler, 0, NMI_NAME);
    if (ret != 0) {
        pr_err("Failed to register NMI handler: %d\n", ret);
        return ret;
    }

    // Create debugfs directory and file
    nmi_debugfs_dir = debugfs_create_dir(NMI_NAME, NULL);
    if (!nmi_debugfs_dir) {
        pr_err("Failed to create debugfs directory\n");
        unregister_nmi_handler(NMI_LOCAL, NMI_NAME);
        return -ENOMEM;
    }

    nmi_debugfs_trigger = debugfs_create_file(TRIGGER_FILE, 0200, nmi_debugfs_dir,
                                              NULL, &nmi_debugfs_fops);
    if (!nmi_debugfs_trigger) {
        pr_err("Failed to create debugfs trigger file\n");
        debugfs_remove_recursive(nmi_debugfs_dir);
        unregister_nmi_handler(NMI_LOCAL, NMI_NAME);
        return -ENOMEM;
    }

    pr_info("NMI handler registered successfully.\n");
    return 0;
}

static void __exit nmi_example_exit(void)
{
	/*
    unsigned long timeout;
    cpumask_copy(to_cpumask(nmi_ipi_mask), cpu_online_mask);
    //cpumask_clear_cpu(smp_processor_id(), to_cpumask(nmi_ipi_mask));
    if (!cpumask_empty(to_cpumask(nmi_ipi_mask)))
    {
        __apic_send_IPI_mask(to_cpumask(nmi_ipi_mask), NMI_VECTOR);

        // Don't wait longer than a second 
        timeout = USEC_PER_SEC;
        while (!cpumask_empty(to_cpumask(nmi_ipi_mask)) && --timeout)
                udelay(1);
    }
    */

    debugfs_remove_recursive(nmi_debugfs_dir);
    // Unregister the NMI handler
    unregister_nmi_handler(NMI_LOCAL, NMI_NAME);
    pr_info("NMI handler unregistered. Module unloaded.\n");
}

module_init(nmi_example_init);
module_exit(nmi_example_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Example NMI handler kernel module");
