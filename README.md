# Gopher

This tool attempts to find deadlock bugs in the eBPF runtime. The following steps are performed by the tool:
1) Dynamic analysis to find relevant information needed to detect deadlock bugs. 
	1.1) Context Analysis using eBPF selftests
	1.2) API analysis using eBPF verifier
2) Callgraph Generation using MLTA
3) Static Analysis to detect deadlock bugs
Optional:
4) Automated testing of reports generated in step 3 using S2E symbolic analysis.

## Requirements
You will need to build a linux kernel from source with BTF information included. You will also need to install the kernel headers. Next you will need to build and install libbpf and bpftool. Finally you will need to generate vmlinux.bc for the kernel you wish to test. Instructions for this can be found in a dedicated section in this document.

Note: It is recommended to use this tool within a VM to prevent breaking anything.

The kernel configuration used will affect the results of the analysis. Thus, it is recommended to enable all BFF related configurations.

## Running the analysis
1) First install necessary dependencies:
```bash
	$ ./install_dependencies.sh
	$ cd mlta
	$ ./build-llvm.sh
```
2) Run context analysis:
	```bash 
	$ ./run_selftests.sh path/to/kernel/source
	```
3) Run API analysis:
	```bash 
	$ ./run_fptests.sh path/to/kernel/source
	```
	You might want to look at any errors at this point. These could indicate some unsatisfied requirements that could affect the accuracy of the analysis. 
4) Generate callgraph:
```bash
	$ cd mlta
	<write the path to your vmlinux.bc file in bc.list>
	$ cd ..
	$ ./run_mlta.sh 
```
The generated callgraph should be found in mlta/callgraph.dot
5) Generate bug reports:
```bash
	$ ./run_graphtraverse.sh path/to/callgraph
```

## Generating vmlinux.bc
There are a few ways to do this but we describe one method here.

1) Make a copy of your running kernel, so you do not need to modify your running kernel
2) Install and use clang-14. Install wllvm. 
3) Enter the copied kernel source directory
```bash
	$ cd /path/to/kernel/source/for/bc/generation
```
4) Add the following lines to the Makefile
```
	KBUILD_CFLAGS += -fno-inline
	KBUILD_CFLAGS += -Wno-error
```
5) Edit include/asm-generic/vmlinux.lds.h by adding a new section for llvm_bc. It should look something like this.
```
#define ELF_DETAILS                                                     \
                .comment 0 : { *(.comment) }                            \
                .symtab 0 : { *(.symtab) }                              \
                .strtab 0 : { *(.strtab) }                              \
                .shstrtab 0 : { *(.shstrtab) }                          \
                .llvm_bc 0 : { *(.llvm_bc) }
```
6) Build the kernel
```bash
$ sudo -E make CC=wllvm LLVM_COMPILER=clang CFLAG="-emit-llvm -c -Wno-error" -j16
```

At this stage you may see some errors triggered by BUILD_BUGS. You can comment out the lines in the kernel source that cause these errors. 
This will not cause any problems as you will not install this kernel source.
7) Extract vmlinux.bc
```bash
$ sudo extract-bc vmlinux
```


## Automated Testing of Reports:

### S2E setup:
You will need to build s2e. Instructions to do this can be found in the official documentation: https://s2e.systems/docs/s2e-env.html#

Next, copy the linux kernels provided in this repository to s2e/source/s2e-linux-kernel
The kernels provided in this repository have been instrumented. Symbolic arguments have been added at various places in the code that should allow you to test the majority of helper functions that we provide templates for. Nevertheless, it may be necessary to add your own instrumentation if you wish to test other helper functions. https://s2e.systems/docs/Tutorials/BasicLinuxSymbex/SourceCode.html can help you getting started with adding your own instrumentation.

To build an image using your preferred kernel

1) Edit s2e/source/guest-images/Makefile.linux - set LINUX_VERSION to your preferred kernel version.
2) Activate s2e environment:
```bash
	$ cd s2e-env
	$ . venv/bin/activate
	$ source ~/s2e/s2e_activate
```
3) Build kernel image:
```bash	
	$ s2e image_build debian-12.5-x86_64
```

The last step is to add the necessary s2e plugins.

1) Make sure s2e environment is activated.
2) Create new plugins: 
```bash
	$ s2e new_plugin LockdepCheck
	$ s2e new_plugin DeadlockTimer
	$ s2e new_plugin ForkEBPF
```
3) Copy all the files in the s2e_plugins directory of this repository to s2e/source/s2e/libs2eplugins/src/s2e/Plugins
4) Rebuild s2e: 
```bash
	$ s2e build
```

### Tool setup:
1) Generate vmlinux.h in the poc/output directory 
```bash
$ bpftool btf dump file /sys/kernel/btf/vmlinux format c> poc/output/vmlinux.h 
```
2) Configuration - Edit the config.conf file with the information for your setup.

You can now generate sample programs for testing using the analyze_reports.sh script.

### Generating sample programs

Generate s2e projects for all the reports in the report file you provided in the configuration file:
```bash
$ ./analyze_reports.sh 
```

Generate s2e projects only for the specified report-number:
```bash
$ ./analyze_reports.sh -r report-number
```
Generate an s2e project of the specified report-number and will try to use the specified program type for the tracing program.
(Applicable only to nested locking reports)
```bash
$ ./analyze_reports.sh -r report-number -p preferred-prog-type
``` 
The available options for -p preferred-prog-type are:
- `kprobe`
- `fentry`
- `fentry_unlock`
- `tracepoint`
